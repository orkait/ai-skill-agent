#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import shutil
import sys
from pathlib import Path
from typing import Annotated, Optional

from verification import verify_skill_directory


def _load_typer():
    try:
        import typer as _typer  # type: ignore
    except Exception:
        print(
            "Typer is required but not available in this Python environment. "
            "Install it first (or use the global Python where Typer is already installed).",
            file=sys.stderr,
        )
        raise SystemExit(1)
    return _typer


# Perform the Typer availability check first, before defining the CLI.
typer = _load_typer()

app = typer.Typer(add_completion=False, help="Skills registry CLI (Typer)")

HOME = Path.home()
REGISTRY_ROOT = HOME / "skills"
REGISTRY_SKILLS_DIR = REGISTRY_ROOT / "skills"
BUILDER_PROMPT_PATH = REGISTRY_ROOT / "skill.build"
IMPROVE_PROMPT_PATH = REGISTRY_ROOT / "skill.improve"
AGENTS = ("codex", "claude", "kiro", "gemini", "antigravity")


def expand_home(value: str | None) -> Path | None:
    if value is None:
        return None
    return Path(os.path.expanduser(value)).resolve()


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def normalize_skill_name(name: str) -> str:
    normalized = "-".join(name.strip().lower().replace("_", "-").split())
    while "--" in normalized:
        normalized = normalized.replace("--", "-")
    return normalized.strip("-")


SKILL_MD_NAMES = {"SKILL.md", "SKILLS.md", "skills.md"}


def has_skill_file(path: Path) -> bool:
    """Return True if the directory contains any recognized skill manifest file."""
    return any((path / name).exists() for name in SKILL_MD_NAMES)


def find_skill_folders_in_dir(path: Path) -> list[Path]:
    """Return sorted direct child directories of `path` that contain a skill manifest file."""
    if not path.is_dir():
        return []
    return sorted(
        child for child in path.iterdir()
        if child.is_dir() and has_skill_file(child)
    )


def validate_skill_dir(skill_dir: Path) -> None:
    if not skill_dir.exists() or not skill_dir.is_dir():
        raise typer.BadParameter(f"Skill source is not a directory: {skill_dir}")
    if not (skill_dir / "SKILL.md").exists():
        raise typer.BadParameter(f"Missing SKILL.md in: {skill_dir}")


def resolve_skill_source(source: str) -> Path:
    """Accept either a filesystem path or a registered skill name."""
    expanded = expand_home(source)
    if expanded is not None and expanded.exists():
        return expanded

    ensure_dir(REGISTRY_SKILLS_DIR)
    registry_candidate = (REGISTRY_SKILLS_DIR / source).resolve()
    if registry_candidate.exists():
        return registry_candidate

    return (expanded if expanded is not None else registry_candidate)


def list_registered_skill_names() -> list[str]:
    ensure_dir(REGISTRY_SKILLS_DIR)
    names: list[str] = []
    for item in REGISTRY_SKILLS_DIR.iterdir():
        if item.is_dir() and (item / "SKILL.md").exists():
            names.append(item.name)
    return sorted(names)


def read_text_if_exists(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return None


def default_builder_prompt() -> str:
    legacy_path = HOME / "skill.build"
    legacy = read_text_if_exists(legacy_path)
    if legacy:
        text = legacy.replace("\r\n", "\n")
        marker = "You must create a copy of the generated skill at each location:"
        if marker in text:
            text = text.split(marker, 1)[0].rstrip()
        if "CLI HANDOFF" not in text:
            text += (
                "\n\nCLI HANDOFF\n"
                "Do NOT copy skills to agent directories.\n"
                "Place the generated skill bundle only in the local registry path (for example: ~/skills/skills/{skill-name}).\n"
                "Agent distribution is handled by the Python CLI (~/skills/cli.py) using install/sync commands.\n"
            )
        return text.rstrip() + "\n"

    return (
        "ROLE\n"
        "You are a Senior Agentic Skill Architect specializing in Progressive Disclosure skill bundles.\n\n"
        "OBJECTIVE\n"
        "Convert the provided @ref folder into a compliant skill bundle.\n\n"
        "CRITICAL\n"
        "If no valid @ref folder is provided, stop and ask for it.\n\n"
        "MANDATORY\n"
        "- Enforce 1-3-10 rule\n"
        "- Keep SKILL.md focused on critical setup/invariants only\n"
        "- Put deep details in /references\n"
        "- Split references semantically (not arbitrary line splits)\n"
        "- Keep each reference file under 800 lines\n"
        "- Pin supported versions in SKILL.md metadata\n"
        "- Include activation semantics with triggers and priority\n\n"
        "CLI HANDOFF\n"
        "Do NOT copy skills to agent directories.\n"
        "Place the generated skill bundle only in the local registry path requested by the user/runner.\n"
        "Agent distribution is handled by the Python CLI (~/skills/cli.py) using install/sync commands.\n"
    )


def default_improve_prompt() -> str:
    return (
        "ROLE\n"
        "You are a Senior Agentic Skill Refiner. Improve an existing registered skill folder so it reaches STRICT quality while preserving correctness and usefulness.\n\n"
        "ENTRY FORMAT (MANDATORY)\n"
        "This prompt is invoked like: `~/skills/skill.improve <skill_name_or_path>`\n"
        "Parse the invocation on the first line and extract `<skill_name_or_path>`.\n"
        "If no target is provided, stop and ask for one.\n\n"
        "DISCOVERY (MANDATORY)\n"
        "1. If the argument looks like a path and exists, use that folder as the target skill folder.\n"
        "2. Otherwise, treat it as a registered skill name and resolve the target folder from the local registry.\n"
        "3. If no target folder exists, stop and ask the user to create/register the skill first.\n"
        "4. Run: `skills verify <skill_name_or_path> --strict --verbose`\n"
        "5. Use STRICT findings as the improvement checklist.\n\n"
        "GOAL\n"
        "Improve the entire target skill folder (all relevant files, not just SKILL.md) so it passes STRICT mode.\n"
        "Minor refinement additions are allowed if they improve clarity, consistency, and agentskills.io alignment.\n"
        "If the target is an unregistered local folder in bad shape, repair it enough to pass verification, then the user can register it.\n\n"
        "COMMON FIXES FOR STRICT PASS\n"
        "- Add/repair frontmatter fields used by strict quality checks (`triggers`, `references`, `activation`)\n"
        "- Move examples/large code blocks out of `SKILL.md` into `references/`\n"
        "- Reorganize references under taxonomy folders (`references/<category>/...`)\n"
        "- Ensure `references` paths exist and are relative\n"
        "- Add version governance / compatibility metadata\n"
        "- Keep SKILL.md as 'brain only' (critical setup rules and invariants)\n\n"
        "WORKFLOW\n"
        "1. Verify in STRICT mode.\n"
        "2. Load and edit files in the registered skill folder in-place.\n"
        "3. Re-run STRICT verify.\n"
        "4. Repeat until STRICT passes or clarification is needed.\n\n"
        "CONSTRAINTS\n"
        "- Do not copy to agent directories directly (`skills install` handles distribution).\n"
        "- Preserve agentskills.io spec compliance while improving strict quality.\n"
        "- If the folder is missing `SKILL.md` or has invalid YAML, create/fix it as part of the improvement.\n"
    )


def project_root_from_option(project: str | None) -> Path:
    if project:
        return expand_home(project) or Path.cwd()
    return Path.cwd().resolve()


def agent_targets(project_root: Path) -> dict[str, Path]:
    return {
        "codex": HOME / ".codex" / "skills",
        "claude": project_root / ".claude" / "skills",
        "kiro": project_root / ".kiro" / "skills",
        "gemini": project_root / ".gemini" / "skills",
        "antigravity": project_root / ".agent" / "skills",
    }


def parse_agents(agent: list[str] | None) -> list[str]:
    if not agent:
        return list(AGENTS)
    parsed: list[str] = []
    for value in agent:
        for token in value.split(","):
            name = token.strip().lower()
            if not name:
                continue
            if name == "all":
                return list(AGENTS)
            if name not in AGENTS:
                raise typer.BadParameter(f"Unknown agent: {name}")
            if name not in parsed:
                parsed.append(name)
    return parsed or list(AGENTS)


def copy_dir(src: Path, dest: Path) -> None:
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(src, dest)


def remove_dir_if_exists(target: Path) -> bool:
    if not target.exists():
        return False
    if target.is_dir():
        shutil.rmtree(target)
    else:
        target.unlink()
    return True


def require_force(force: bool, action: str) -> None:
    if not force:
        raise typer.BadParameter(f"{action} is destructive. Re-run with --force.")


def install_skills(
    skill_names: list[str],
    agents: list[str],
    project_root: Path,
    *,
    mode: str = "install",
) -> None:
    if not skill_names:
        raise typer.BadParameter("No skills specified for install")
    targets = agent_targets(project_root)
    ensure_dir(REGISTRY_SKILLS_DIR)

    for skill_name in skill_names:
        src = REGISTRY_SKILLS_DIR / skill_name
        validate_skill_dir(src)
        for agent in agents:
            dest_root = targets[agent]
            ensure_dir(dest_root)
            dest = dest_root / skill_name
            copy_dir(src, dest)
            if mode == "sync":
                typer.echo(f"[sync] updated {skill_name} -> {dest}")
            else:
                typer.echo(f"[install] {skill_name} -> {agent} ({dest})")


def desync_skills(skill_names: list[str], agents: list[str], project_root: Path) -> None:
    if not skill_names:
        raise typer.BadParameter("No skills specified for desync")
    targets = agent_targets(project_root)
    for skill_name in skill_names:
        for agent in agents:
            dest = targets[agent] / skill_name
            if remove_dir_if_exists(dest):
                typer.echo(f"[desync] removed {skill_name} from {agent} ({dest})")
            else:
                typer.echo(f"[desync] missing {skill_name} in {agent} ({dest})")


def main() -> None:
    app()


def _enforce_gate(result, gate: str) -> None:
    gate = gate.lower().strip()
    if gate not in {"spec", "strict"}:
        raise typer.BadParameter("`--gate` must be `spec` or `strict`.")
    if gate == "spec" and not result.spec_passed:
        raise typer.Exit(code=1)
    if gate == "strict" and not result.strict_passed:
        raise typer.Exit(code=1)


def _gate_passed(result, gate: str) -> bool:
    gate = gate.lower().strip()
    if gate not in {"spec", "strict"}:
        raise typer.BadParameter("`--gate` must be `spec` or `strict`.")
    return result.spec_passed if gate == "spec" else result.strict_passed


def _status_text(passed: bool) -> str:
    return "PASS" if passed else "FAIL"


def _status_color(passed: bool) -> str:
    return "green" if passed else "red"


def _render_issue_group(title: str, errors, warnings) -> None:
    if not errors and not warnings:
        return
    typer.secho(f"\n{title}", fg=typer.colors.BRIGHT_BLUE, bold=True)
    for issue in errors:
        typer.secho(f"  [ERROR] {issue.message}", fg=typer.colors.RED)
    for issue in warnings:
        typer.secho(f"  [WARN]  {issue.message}", fg=typer.colors.YELLOW)


def _verification_payload(result, verbose: bool = False) -> dict:
    payload = {
        "skill_dir": str(result.skill_dir),
        "grades": {
            "spec": {"score": result.spec_grade, "status": _status_text(result.spec_passed)},
            "strict": {
                "score": result.strict_grade,
                "status": _status_text(result.strict_passed),
                "threshold": result.strict_threshold,
            },
        },
        "counts": {
            "spec": {"errors": len(result.spec_errors), "warnings": len(result.spec_warnings)},
            "strict": {"errors": len(result.errors), "warnings": len(result.warnings)},
        },
    }
    if verbose:
        payload["findings"] = {
            "spec": {
                "errors": [i.message for i in result.spec_errors],
                "warnings": [i.message for i in result.spec_warnings],
            },
            "strict": {
                "errors": [i.message for i in result.errors],
                "warnings": [i.message for i in result.warnings],
            },
        }
    return payload


def _print_verification_report_text(result, verbose: bool = False) -> None:
    p = _verification_payload(result, verbose=verbose)
    typer.echo(f"[verify] {p['skill_dir']}")
    typer.echo(
        f"[verify] SPEC   grade={p['grades']['spec']['score']}/100 status={p['grades']['spec']['status']} "
        f"errors={p['counts']['spec']['errors']} warnings={p['counts']['spec']['warnings']}"
    )
    typer.echo(
        f"[verify] STRICT grade={p['grades']['strict']['score']}/100 status={p['grades']['strict']['status']} "
        f"threshold={p['grades']['strict']['threshold']} "
        f"errors={p['counts']['strict']['errors']} warnings={p['counts']['strict']['warnings']}"
    )
    if not verbose:
        if any([p["counts"]["spec"]["errors"], p["counts"]["spec"]["warnings"], p["counts"]["strict"]["errors"], p["counts"]["strict"]["warnings"]]):
            typer.echo("[verify] Use --verbose for full findings.")
        return
    findings = p.get("findings", {})
    for scope in ("spec", "strict"):
        f = findings.get(scope, {})
        if not f.get("errors") and not f.get("warnings"):
            continue
        typer.echo(f"[verify] {scope.upper()} Findings")
        for msg in f.get("errors", []):
            typer.echo(f"  {scope.upper()} ERROR: {msg}")
        for msg in f.get("warnings", []):
            typer.echo(f"  {scope.upper()} WARN: {msg}")


def _print_verification_report(result, verbose: bool = False, output: str = "pretty") -> None:
    output = output.lower().strip()
    if output not in {"pretty", "text", "json"}:
        raise typer.BadParameter("`--output` must be `pretty`, `text`, or `json`.")
    if output == "json":
        typer.echo(json.dumps(_verification_payload(result, verbose=verbose), indent=2))
        return
    if output == "text":
        _print_verification_report_text(result, verbose=verbose)
        return

    typer.secho(f"\nVerify: {result.skill_dir}", fg=typer.colors.CYAN, bold=True)
    typer.echo("-" * 72)

    typer.echo("Grades")
    typer.secho(
        f"  SPEC   : {_status_text(result.spec_passed)}  ({result.spec_grade}/100)",
        fg=_status_color(result.spec_passed),
        bold=result.spec_passed,
    )
    strict_text = (
        f"  STRICT : {_status_text(result.strict_passed)}  "
        f"({result.strict_grade}/100, threshold={result.strict_threshold})"
    )
    typer.secho(
        strict_text,
        fg=_status_color(result.strict_passed),
        bold=result.strict_passed,
    )
    typer.echo(
        f"Counts  SPEC(e={len(result.spec_errors)}, w={len(result.spec_warnings)})  "
        f"STRICT(e={len(result.errors)}, w={len(result.warnings)})"
    )

    if not result.spec_issues and not result.issues:
        typer.secho("\nNo findings.", fg=typer.colors.GREEN)
        return

    if not verbose:
        if result.spec_errors or result.errors:
            seen = set()
            merged_errors = []
            for issue in [*result.spec_errors, *result.errors]:
                key = issue.message
                if key in seen:
                    continue
                seen.add(key)
                merged_errors.append(issue)
            _render_issue_group("Errors", merged_errors, [])
        typer.secho(
            "\nTip: Use --verbose for full spec/strict warnings and grouped findings.",
            fg=typer.colors.BRIGHT_BLACK,
        )
        return

    _render_issue_group("Spec Findings", result.spec_errors, result.spec_warnings)
    _render_issue_group("Strict Findings", result.errors, result.warnings)


@app.command()
def init(
    force_prompt: Annotated[bool, typer.Option("--force-prompt", help="Rewrite ~/skills/skill.build")]
    = False,
    force_improve_prompt: Annotated[
        bool, typer.Option("--force-improve-prompt", help="Rewrite ~/skills/skill.improve")
    ] = False,
) -> None:
    """Create ~/skills layout and seed skill.build."""
    ensure_dir(REGISTRY_ROOT)
    ensure_dir(REGISTRY_SKILLS_DIR)

    if force_prompt or not BUILDER_PROMPT_PATH.exists():
        BUILDER_PROMPT_PATH.write_text(default_builder_prompt(), encoding="utf-8")
        typer.echo(f"Wrote prompt: {BUILDER_PROMPT_PATH}")
    else:
        typer.echo(f"Prompt exists: {BUILDER_PROMPT_PATH}")

    if force_improve_prompt or not IMPROVE_PROMPT_PATH.exists():
        IMPROVE_PROMPT_PATH.write_text(default_improve_prompt(), encoding="utf-8")
        typer.echo(f"Wrote improve prompt: {IMPROVE_PROMPT_PATH}")
    else:
        typer.echo(f"Improve prompt exists: {IMPROVE_PROMPT_PATH}")

    typer.echo(f"Registry skills dir: {REGISTRY_SKILLS_DIR}")


@app.command("list")
def list_cmd() -> None:
    """List registered skills."""
    skills = list_registered_skill_names()
    if not skills:
        typer.echo("No registered skills found.")
        return
    for skill in skills:
        typer.echo(skill)


@app.command()
def create(
    name: Annotated[str, typer.Argument(help="Skill name (used as folder name)")],
    force: Annotated[bool, typer.Option("--force", help="Overwrite existing registry skill folder")] = False,
) -> None:
    """Create a minimal skill scaffold in ~/skills/skills/<name>."""
    ensure_dir(REGISTRY_SKILLS_DIR)

    skill_name = normalize_skill_name(name)
    if not skill_name:
        raise typer.BadParameter("Skill name is empty after normalization")

    skill_dir = REGISTRY_SKILLS_DIR / skill_name
    references_dir = skill_dir / "references"
    misc_references_dir = references_dir / "misc"
    skill_md = skill_dir / "SKILL.md"

    if skill_dir.exists():
        if not force:
            raise typer.BadParameter(
                f"Skill already exists: {skill_dir}. Use --force to overwrite."
            )
        shutil.rmtree(skill_dir)

    ensure_dir(misc_references_dir)
    skill_md.write_text(
        (
            "---\n"
            f"name: {skill_name}\n"
            "description: >-\n"
            f"  Describe what the `{skill_name}` skill does and when to use it.\n"
            "triggers:\n"
            f"  - {skill_name}\n"
            "references:\n"
            "  - references/misc/overview.md\n"
            "compatibility: \"Add supported versions/platforms here\"\n"
            "metadata:\n"
            "  skill_version: \"0.1.0\"\n"
            "  owner: \"\"\n"
            "activation:\n"
            "  mode: fuzzy\n"
            "  triggers:\n"
            f"    - {skill_name}\n"
            "  priority: normal\n"
            "---\n\n"
            "# Skill Instructions\n\n"
            "Keep this file focused on critical setup rules and invariants only.\n\n"
            "## Critical Rules\n\n"
            "1. Replace this scaffold with the actual setup constraints.\n"
            "2. Move detailed docs/examples into `references/` files.\n"
        ),
        encoding="utf-8",
    )
    (misc_references_dir / "overview.md").write_text(
        (
            f"# {skill_name} Reference\n\n"
            "Add detailed documentation, examples, API notes, and patterns here.\n"
        ),
        encoding="utf-8",
    )

    typer.echo(f"[create] scaffolded {skill_dir}")
    typer.echo(f"[create] edit {skill_md}")


@app.command()
def register(
    sources: Annotated[
        list[str],
        typer.Argument(
            help=(
                "Path(s) to skill folder(s). "
                "Pass '.' to discover all skill subfolders in the current directory. "
                "Multiple paths are accepted: skills register path1 path2 path3"
            )
        ),
    ] = [],
    name: Annotated[
        Optional[str],
        typer.Option("--name", help="Override registry folder name (single skill only)"),
    ] = None,
    install: Annotated[bool, typer.Option("--install", help="Install to agent directories after register")] = False,
    agent: Annotated[list[str], typer.Option("--agent", help="Agent(s): codex,claude,kiro,gemini,antigravity,all")] = [],
    project: Annotated[Optional[str], typer.Option("--project", help="Project root for agent-local folders")] = None,
    gate: Annotated[str, typer.Option("--gate", help="Registration gate: spec or strict")] = "spec",
    verbose: Annotated[bool, typer.Option("--verbose", help="Show full verification findings")] = False,
    output: Annotated[str, typer.Option("--output", help="Verification output format: pretty, text, json")] = "pretty",
) -> None:
    """Register one or more skills into ~/skills/skills.

    Pass '.' to discover and register all skill subfolders in the current directory.
    Multiple explicit paths are also accepted.
    """
    raw_sources = list(sources)
    if not raw_sources:
        raw_sources = [typer.prompt("Skill source folder path")]

    if name and len(raw_sources) > 1:
        raise typer.BadParameter("--name cannot be used when registering multiple skills.")

    # Expand each source: directories without a skill file trigger discovery of subfolders
    resolved: list[Path] = []
    for src in raw_sources:
        p = expand_home(src)
        if p is None:
            raise typer.BadParameter(f"Invalid path: {src}")
        if p.is_dir() and not has_skill_file(p):
            discovered = find_skill_folders_in_dir(p)
            if not discovered:
                typer.secho(f"[register] No skill folders found in: {p}", fg=typer.colors.YELLOW)
            else:
                typer.echo(f"[register] Discovered {len(discovered)} skill folder(s) in: {p}")
                resolved.extend(discovered)
        else:
            resolved.append(p)

    if not resolved:
        raise typer.BadParameter("No skill source paths resolved.")

    batch = len(resolved) > 1
    project_root = project_root_from_option(project)
    agents = parse_agents(agent)
    success_count = 0
    fail_count = 0

    for src_path in resolved:
        if batch:
            typer.secho(f"\n--- {src_path.name} ---", fg=typer.colors.CYAN)

        verification = verify_skill_directory(src_path)
        _print_verification_report(verification, verbose=verbose, output=output)

        if not _gate_passed(verification, gate):
            if batch:
                typer.secho(
                    f"[register] Skipped {src_path.name} (failed `{gate}` gate).",
                    fg=typer.colors.YELLOW,
                )
                fail_count += 1
                continue
            typer.secho(
                f"\nRegistration blocked by `{gate}` gate.",
                fg=typer.colors.RED,
                bold=True,
            )
            typer.secho(
                f"Repair path: run `skills improve {src_path}` and fix the folder in-place, then register again.",
                fg=typer.colors.YELLOW,
            )
            raise typer.Exit(code=1)

        skill_name = (name or src_path.name).strip()
        if not skill_name:
            if batch:
                typer.secho(
                    f"[register] Skipped: resolved skill name is empty for {src_path}",
                    fg=typer.colors.YELLOW,
                )
                fail_count += 1
                continue
            raise typer.BadParameter("Resolved skill name is empty")

        frontmatter_name = verification.get_frontmatter_name()
        if frontmatter_name and name and skill_name != frontmatter_name:
            if batch:
                typer.secho(
                    f"[register] Skipped {src_path.name}: --name ({skill_name}) does not match "
                    f"SKILL.md name ({frontmatter_name}).",
                    fg=typer.colors.YELLOW,
                )
                fail_count += 1
                continue
            raise typer.BadParameter(
                f"--name ({skill_name}) must match SKILL.md frontmatter name ({frontmatter_name}) to remain spec-compliant."
            )

        ensure_dir(REGISTRY_SKILLS_DIR)
        dest = REGISTRY_SKILLS_DIR / skill_name
        copy_dir(src_path, dest)
        typer.echo(f"[register] {src_path} -> {dest}")
        success_count += 1

        if install:
            install_skills([skill_name], agents, project_root)

    if batch:
        typer.echo(f"\n[register] Done: {success_count} registered, {fail_count} skipped.")
        if fail_count > 0:
            raise typer.Exit(code=1)


@app.command()
def verify(
    source: Annotated[str, typer.Argument(help="Path to a skill folder OR registered skill name")],
    gate: Annotated[str, typer.Option("--gate", help="Exit-code gate: spec or strict")] = "spec",
    strict: Annotated[bool, typer.Option("--strict", help="Shortcut for --gate strict")] = False,
    verbose: Annotated[bool, typer.Option("--verbose", help="Show full verification findings")] = False,
    output: Annotated[str, typer.Option("--output", help="Output format: pretty, text, json")] = "pretty",
) -> None:
    """Validate a skill folder against the Agent Skills spec checks."""
    src_path = resolve_skill_source(source)
    if src_path is None:
        raise typer.BadParameter("Missing source path")
    if strict:
        gate = "strict"
    result = verify_skill_directory(src_path)
    _print_verification_report(result, verbose=verbose, output=output)
    _enforce_gate(result, gate)


@app.command()
def deregister(
    skill_name: Annotated[Optional[str], typer.Argument(help="Registered skill name")] = None,
    all: Annotated[bool, typer.Option("--all", help="Remove all registered skills from registry")] = False,
    force: Annotated[bool, typer.Option("--force", help="Confirm destructive removal")] = False,
) -> None:
    """Remove skill(s) from the global registry (~/skills/skills)."""
    require_force(force, "deregister")
    ensure_dir(REGISTRY_SKILLS_DIR)

    if all:
        names = list_registered_skill_names()
        if not names:
            typer.echo("No registered skills to deregister.")
            raise typer.Exit(0)
    elif skill_name:
        names = [skill_name]
    else:
        raise typer.BadParameter("Provide <skill-name> or use --all.")

    for name in names:
        target = REGISTRY_SKILLS_DIR / name
        if remove_dir_if_exists(target):
            typer.echo(f"[deregister] removed {target}")
        else:
            typer.echo(f"[deregister] missing {target}")


@app.command()
def install(
    skill_name: Annotated[Optional[str], typer.Argument(help="Registered skill name")]
    = None,
    agent: Annotated[list[str], typer.Option("--agent", help="Agent(s): codex,claude,kiro,gemini,antigravity,all")]
    = [],
    project: Annotated[Optional[str], typer.Option("--project", help="Project root for agent-local folders")]
    = None,
    all: Annotated[bool, typer.Option("--all", help="Install all registered skills")] = False,
) -> None:
    """Install registered skill(s) to agent directories."""
    if all or skill_name is None:
        skills = list_registered_skill_names()
        if not skills:
            typer.echo("No registered skills to install.")
            raise typer.Exit(0)
    else:
        skills = [skill_name]

    install_skills(skills, parse_agents(agent), project_root_from_option(project))


@app.command()
def sync(
    skill_names: Annotated[
        list[str],
        typer.Argument(help="Optional registered skill names to sync (defaults to all if omitted)"),
    ] = [],
    agent: Annotated[list[str], typer.Option("--agent", help="Agent(s): codex,claude,kiro,gemini,antigravity,all")]
    = [],
    project: Annotated[Optional[str], typer.Option("--project", help="Project root for agent-local folders")]
    = None,
) -> None:
    """Sync registered skill(s) to agent directories (all if no skill names are provided)."""
    skills = skill_names or list_registered_skill_names()
    if not skills:
        typer.echo("No registered skills to sync.")
        raise typer.Exit(0)
    install_skills(skills, parse_agents(agent), project_root_from_option(project), mode="sync")


@app.command()
def desync(
    skill_name: Annotated[Optional[str], typer.Argument(help="Installed/registered skill name")] = None,
    agent: Annotated[list[str], typer.Option("--agent", help="Agent(s): codex,claude,kiro,gemini,antigravity,all")]
    = [],
    project: Annotated[Optional[str], typer.Option("--project", help="Project root for agent-local folders")] = None,
    all: Annotated[bool, typer.Option("--all", help="Remove all registered skills from agent directories")] = False,
    force: Annotated[bool, typer.Option("--force", help="Confirm destructive removal")] = False,
) -> None:
    """Remove installed skill copies from agent directories."""
    require_force(force, "desync")

    if all:
        skills = list_registered_skill_names()
        if not skills:
            typer.echo("No registered skills to desync.")
            raise typer.Exit(0)
    elif skill_name:
        skills = [skill_name]
    else:
        raise typer.BadParameter("Provide <skill-name> or use --all.")

    desync_skills(skills, parse_agents(agent), project_root_from_option(project))


@app.command()
def where(
    project: Annotated[Optional[str], typer.Option("--project", help="Project root for agent-local folders")]
    = None,
) -> None:
    """Show registry and agent target locations."""
    project_root = project_root_from_option(project)
    targets = agent_targets(project_root)
    typer.echo(f"registryRoot: {REGISTRY_ROOT}")
    typer.echo(f"registrySkills: {REGISTRY_SKILLS_DIR}")
    typer.echo(f"builderPrompt: {BUILDER_PROMPT_PATH}")
    typer.echo(f"improvePrompt: {IMPROVE_PROMPT_PATH}")
    typer.echo(f"projectRoot: {project_root}")
    for agent_name in AGENTS:
        typer.echo(f"{agent_name}: {targets[agent_name]}")


@app.command()
def prompt() -> None:
    """Print the builder prompt path."""
    typer.echo(str(BUILDER_PROMPT_PATH))


@app.command()
def improve(
    target: Annotated[
        str, typer.Argument(help="Registered skill name OR local folder path to improve")
    ],
    verify_first: Annotated[
        bool, typer.Option("--verify/--no-verify", help="Run STRICT verification before showing improve instructions")
    ] = True,
    verbose: Annotated[bool, typer.Option("--verbose", help="Show full STRICT findings when verifying")] = True,
    output: Annotated[str, typer.Option("--output", help="Verify output format: pretty, text, json")] = "pretty",
) -> None:
    """Prepare improvement of a skill folder (registered or local path) and show the LLM invocation."""
    ensure_dir(REGISTRY_SKILLS_DIR)
    skill_dir = resolve_skill_source(target)
    if not skill_dir.exists() or not skill_dir.is_dir():
        raise typer.BadParameter(
            f"Target skill folder not found: {target}. Pass a registered skill name or an existing folder path."
        )

    target_label = target
    try:
        rel = skill_dir.relative_to(REGISTRY_SKILLS_DIR)
        target_kind = "registered"
        target_label = rel.as_posix()
    except ValueError:
        target_kind = "local-path"

    typer.secho(f"Improve Skill Folder: {target_label}", fg=typer.colors.CYAN, bold=True)
    typer.echo(f"Target kind: {target_kind}")
    typer.echo(f"Target folder: {skill_dir}")
    typer.echo(f"LLM entrypoint: {IMPROVE_PROMPT_PATH} {target}")

    if verify_first:
        typer.secho("\nPreflight STRICT verify", fg=typer.colors.BRIGHT_BLUE, bold=True)
        result = verify_skill_directory(skill_dir)
        _print_verification_report(result, verbose=verbose, output=output)
        if result.strict_passed:
            typer.secho(
                "\nSTRICT already passes. You can still run the improve prompt for refinement if desired.",
                fg=typer.colors.GREEN,
            )
        else:
            typer.secho(
                "\nNext step: run the LLM prompt and let it fix STRICT findings in-place.",
                fg=typer.colors.YELLOW,
            )

        if target_kind == "local-path" and result.spec_passed:
            typer.secho(
                "\nAfter repair, you can register it with: "
                f"skills register {skill_dir}",
                fg=typer.colors.BRIGHT_BLACK,
            )

    typer.echo(f"\nRun in Gemini/Claude CLI: {IMPROVE_PROMPT_PATH} {target}")


@app.command("improve-path")
def improve_path() -> None:
    """Print the improve prompt path (low-level helper)."""
    typer.echo(str(IMPROVE_PROMPT_PATH))


@app.command("improve-prompt")
def improve_prompt_legacy() -> None:
    """Deprecated alias for `improve-path` (kept for compatibility)."""
    typer.echo(str(IMPROVE_PROMPT_PATH))


if __name__ == "__main__":
    main()
