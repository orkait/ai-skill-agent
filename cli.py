#!/usr/bin/env python3
from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path
from typing import Annotated, Optional


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
AGENTS = ("codex", "claude", "kiro", "gemini")


def expand_home(value: str | None) -> Path | None:
    if value is None:
        return None
    return Path(os.path.expanduser(value)).resolve()


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def validate_skill_dir(skill_dir: Path) -> None:
    if not skill_dir.exists() or not skill_dir.is_dir():
        raise typer.BadParameter(f"Skill source is not a directory: {skill_dir}")
    if not (skill_dir / "SKILL.md").exists():
        raise typer.BadParameter(f"Missing SKILL.md in: {skill_dir}")


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


def install_skills(skill_names: list[str], agents: list[str], project_root: Path) -> None:
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
            typer.echo(f"[install] {skill_name} -> {agent} ({dest})")


def main() -> None:
    app()


@app.command()
def init(
    force_prompt: Annotated[bool, typer.Option("--force-prompt", help="Rewrite ~/skills/skill.build")]
    = False,
) -> None:
    """Create ~/skills layout and seed skill.build."""
    ensure_dir(REGISTRY_ROOT)
    ensure_dir(REGISTRY_SKILLS_DIR)

    if force_prompt or not BUILDER_PROMPT_PATH.exists():
        BUILDER_PROMPT_PATH.write_text(default_builder_prompt(), encoding="utf-8")
        typer.echo(f"Wrote prompt: {BUILDER_PROMPT_PATH}")
    else:
        typer.echo(f"Prompt exists: {BUILDER_PROMPT_PATH}")

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
def register(
    source: Annotated[Optional[str], typer.Argument(help="Path to generated skill folder")] = None,
    name: Annotated[Optional[str], typer.Option("--name", help="Override registry skill folder name")] = None,
    install: Annotated[bool, typer.Option("--install", help="Install to agent directories after register")] = False,
    agent: Annotated[list[str], typer.Option("--agent", help="Agent(s): codex,claude,kiro,gemini,all")]
    = [],
    project: Annotated[Optional[str], typer.Option("--project", help="Project root for agent-local folders")]
    = None,
) -> None:
    """Register a skill into ~/skills/skills."""
    if not source:
        source = typer.prompt("Skill source folder path")

    src_path = expand_home(source)
    if src_path is None:
        raise typer.BadParameter("Missing source path")
    validate_skill_dir(src_path)

    skill_name = (name or src_path.name).strip()
    if not skill_name:
        raise typer.BadParameter("Resolved skill name is empty")

    ensure_dir(REGISTRY_SKILLS_DIR)
    dest = REGISTRY_SKILLS_DIR / skill_name
    copy_dir(src_path, dest)
    typer.echo(f"[register] {src_path} -> {dest}")

    if install:
        install_skills([skill_name], parse_agents(agent), project_root_from_option(project))


@app.command()
def install(
    skill_name: Annotated[Optional[str], typer.Argument(help="Registered skill name")]
    = None,
    agent: Annotated[list[str], typer.Option("--agent", help="Agent(s): codex,claude,kiro,gemini,all")]
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
    agent: Annotated[list[str], typer.Option("--agent", help="Agent(s): codex,claude,kiro,gemini,all")]
    = [],
    project: Annotated[Optional[str], typer.Option("--project", help="Project root for agent-local folders")]
    = None,
) -> None:
    """Install all registered skills to agent directories."""
    skills = list_registered_skill_names()
    if not skills:
        typer.echo("No registered skills to sync.")
        raise typer.Exit(0)
    install_skills(skills, parse_agents(agent), project_root_from_option(project))


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
    typer.echo(f"projectRoot: {project_root}")
    for agent_name in AGENTS:
        typer.echo(f"{agent_name}: {targets[agent_name]}")


@app.command()
def prompt() -> None:
    """Print the builder prompt path."""
    typer.echo(str(BUILDER_PROMPT_PATH))


if __name__ == "__main__":
    main()
