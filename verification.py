from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import re
from typing import Any

import yaml


NAME_RE = re.compile(r"^[a-z0-9-]{1,64}$")
OPTIONAL_DIRS = ("scripts", "references", "assets")
WORKFLOW_ALLOWED_TOPLEVEL = {"SKILL.md", "references", "scripts", "assets", "agents"}
WORKFLOW_REFERENCE_TAXONOMY = {
    "api",
    "hooks",
    "types",
    "patterns",
    "architecture",
    "performance",
    "migration",
    "validation",
    "examples",
    "misc",
}


@dataclass
class VerificationIssue:
    level: str
    message: str


@dataclass
class VerificationResult:
    skill_dir: Path
    skill_md_path: Path
    issues: list[VerificationIssue] = field(default_factory=list)
    spec_issues: list[VerificationIssue] = field(default_factory=list)
    frontmatter: dict[str, Any] | None = None
    body: str | None = None

    spec_grade: int = 0
    strict_grade: int = 0
    spec_passed: bool = False
    strict_passed: bool = False
    strict_threshold: int = 80

    @property
    def errors(self) -> list[VerificationIssue]:
        return [i for i in self.issues if i.level == "error"]

    @property
    def warnings(self) -> list[VerificationIssue]:
        return [i for i in self.issues if i.level == "warning"]

    @property
    def is_valid(self) -> bool:
        return self.spec_passed

    def add_error(self, message: str) -> None:
        self.issues.append(VerificationIssue(level="error", message=message))

    def add_warning(self, message: str) -> None:
        self.issues.append(VerificationIssue(level="warning", message=message))

    def add_spec_error(self, message: str) -> None:
        self.spec_issues.append(VerificationIssue(level="error", message=message))

    def add_spec_warning(self, message: str) -> None:
        self.spec_issues.append(VerificationIssue(level="warning", message=message))

    @property
    def spec_errors(self) -> list[VerificationIssue]:
        return [i for i in self.spec_issues if i.level == "error"]

    @property
    def spec_warnings(self) -> list[VerificationIssue]:
        return [i for i in self.spec_issues if i.level == "warning"]

    def get_frontmatter_name(self) -> str | None:
        if not isinstance(self.frontmatter, dict):
            return None
        value = self.frontmatter.get("name")
        return value if isinstance(value, str) else None


def _split_frontmatter(text: str) -> tuple[str, str] | None:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    for idx in range(1, len(lines)):
        if lines[idx].strip() == "---":
            frontmatter = "\n".join(lines[1:idx])
            body = "\n".join(lines[idx + 1 :])
            return frontmatter, body
    return None


def _validate_name(value: Any, parent_dir_name: str, result: VerificationResult) -> None:
    if not isinstance(value, str):
        result.add_error("Frontmatter field `name` is required and must be a string.")
        return

    if len(value) == 0 or len(value) > 64:
        result.add_error("`name` must be 1-64 characters.")

    if not NAME_RE.fullmatch(value):
        result.add_error(
            "`name` must contain only lowercase letters, numbers, and hyphens."
        )

    if value.startswith("-") or value.endswith("-"):
        result.add_error("`name` must not start or end with `-`.")

    if "--" in value:
        result.add_error("`name` must not contain consecutive hyphens (`--`).")

    if value != parent_dir_name:
        result.add_error(
            f"`name` ({value}) must match the parent directory name ({parent_dir_name})."
        )


def _validate_description(value: Any, result: VerificationResult) -> None:
    if not isinstance(value, str):
        result.add_error("Frontmatter field `description` is required and must be a string.")
        return

    length = len(value.strip())
    if length == 0 or length > 1024:
        result.add_error("`description` must be non-empty and at most 1024 characters.")
    elif length < 20:
        result.add_warning(
            "`description` is very short; Agent Skills spec recommends describing what the skill does and when to use it."
        )


def _validate_optional_string_field(
    key: str, value: Any, result: VerificationResult, max_len: int | None = None
) -> None:
    if value is None:
        return
    if not isinstance(value, str):
        result.add_error(f"`{key}` must be a string if provided.")
        return
    trimmed = value.strip()
    if key == "compatibility" and len(trimmed) == 0:
        result.add_error("`compatibility` must be 1-500 characters if provided.")
        return
    if max_len is not None and len(trimmed) > max_len:
        result.add_error(f"`{key}` must be at most {max_len} characters.")


def _validate_metadata(value: Any, result: VerificationResult) -> None:
    if value is None:
        return
    if not isinstance(value, dict):
        result.add_error("`metadata` must be a key-value mapping if provided.")
        return
    for k, v in value.items():
        if not isinstance(k, str):
            result.add_error("`metadata` keys must be strings.")
        if not isinstance(v, str):
            result.add_warning(
                f"`metadata.{k}` is structured (non-string). Agent Skills spec prefers string metadata values, but this workflow currently allows richer metadata."
            )


def _validate_metadata_spec(value: Any, result: VerificationResult) -> None:
    if value is None:
        return
    if not isinstance(value, dict):
        result.add_spec_error("`metadata` must be a key-value mapping if provided.")
        return
    for k, v in value.items():
        if not isinstance(k, str):
            result.add_spec_error("`metadata` keys must be strings.")
        if not isinstance(v, str):
            result.add_spec_warning(
                f"`metadata.{k}` is structured (non-string). Spec-oriented tooling may expect string metadata values."
            )


def _validate_allowed_tools(value: Any, result: VerificationResult) -> None:
    if value is None:
        return
    if not isinstance(value, str):
        result.add_error("`allowed-tools` must be a space-delimited string if provided.")
        return
    if len(value.strip()) == 0:
        result.add_error("`allowed-tools` must not be empty if provided.")


def _validate_allowed_tools_spec(value: Any, result: VerificationResult) -> None:
    if value is None:
        return
    if not isinstance(value, str):
        result.add_spec_error("`allowed-tools` must be a space-delimited string if provided.")
        return
    if len(value.strip()) == 0:
        result.add_spec_error("`allowed-tools` must not be empty if provided.")


def _validate_optional_dirs(skill_dir: Path, result: VerificationResult) -> None:
    for dirname in OPTIONAL_DIRS:
        p = skill_dir / dirname
        if p.exists() and not p.is_dir():
            result.add_error(f"`{dirname}` exists but is not a directory.")


def _validate_yaml_frontmatter_safety(frontmatter_text: str, result: VerificationResult) -> None:
    # Workflow rule from ~/skill.build: quote scalars that start with @ (especially trigger items).
    for line in frontmatter_text.splitlines():
        if re.match(r"^\s*-\s+@", line):
            result.add_error(
                "YAML frontmatter safety rule violated: quote trigger/scalar values starting with `@` (use `- \"@pkg/name\"`)."
            )


def _validate_top_level_layout(skill_dir: Path, result: VerificationResult) -> None:
    for child in skill_dir.iterdir():
        if child.name == ".DS_Store":
            continue
        if child.name not in WORKFLOW_ALLOWED_TOPLEVEL:
            if child.is_dir():
                result.add_warning(
                    f"Unexpected top-level directory `{child.name}`. Workflow convention expects SKILL.md plus optional scripts/references/assets/agents."
                )
            else:
                result.add_warning(
                    f"Unexpected top-level file `{child.name}`. Workflow convention prefers only `SKILL.md` at skill root."
                )


def _validate_name_spec(value: Any, parent_dir_name: str, result: VerificationResult) -> None:
    if not isinstance(value, str):
        result.add_spec_error("Frontmatter field `name` is required and must be a string.")
        return
    if len(value) == 0 or len(value) > 64:
        result.add_spec_error("`name` must be 1-64 characters.")
    if not NAME_RE.fullmatch(value):
        result.add_spec_error(
            "`name` must contain only lowercase letters, numbers, and hyphens."
        )
    if value.startswith("-") or value.endswith("-"):
        result.add_spec_error("`name` must not start or end with `-`.")
    if "--" in value:
        result.add_spec_error("`name` must not contain consecutive hyphens (`--`).")
    if value != parent_dir_name:
        result.add_spec_error(
            f"`name` ({value}) must match the parent directory name ({parent_dir_name})."
        )


def _validate_description_spec(value: Any, result: VerificationResult) -> None:
    if not isinstance(value, str):
        result.add_spec_error("Frontmatter field `description` is required and must be a string.")
        return
    length = len(value.strip())
    if length == 0 or length > 1024:
        result.add_spec_error("`description` must be non-empty and at most 1024 characters.")
    elif length < 20:
        result.add_spec_warning(
            "`description` is very short; include what the skill does and when to use it."
        )


def _validate_optional_string_field_spec(
    key: str, value: Any, result: VerificationResult, max_len: int | None = None
) -> None:
    if value is None:
        return
    if not isinstance(value, str):
        result.add_spec_error(f"`{key}` must be a string if provided.")
        return
    trimmed = value.strip()
    if key == "compatibility" and len(trimmed) == 0:
        result.add_spec_error("`compatibility` must be 1-500 characters if provided.")
        return
    if max_len is not None and len(trimmed) > max_len:
        result.add_spec_error(f"`{key}` must be at most {max_len} characters.")


def _is_non_empty_string_list(value: Any) -> bool:
    return isinstance(value, list) and len(value) > 0 and all(
        isinstance(x, str) and x.strip() for x in value
    )


def _validate_activation(frontmatter: dict[str, Any], result: VerificationResult) -> None:
    activation = frontmatter.get("activation")
    if not isinstance(activation, dict):
        result.add_error(
            "Workflow gate: `activation` is required and must be a mapping with `mode`, `triggers`, and `priority`."
        )
        return

    mode = activation.get("mode")
    if mode not in {"strict", "fuzzy"}:
        result.add_error("Workflow gate: `activation.mode` must be `strict` or `fuzzy`.")

    triggers = activation.get("triggers")
    if not _is_non_empty_string_list(triggers):
        result.add_error("Workflow gate: `activation.triggers` must be a non-empty list of strings.")

    priority = activation.get("priority")
    if priority not in {"normal", "high"}:
        result.add_error("Workflow gate: `activation.priority` must be `normal` or `high`.")


def _validate_version_and_compatibility(frontmatter: dict[str, Any], result: VerificationResult) -> None:
    metadata = frontmatter.get("metadata")
    compatibility = frontmatter.get("compatibility")
    metadata_compat = metadata.get("compatibility") if isinstance(metadata, dict) else None
    has_metadata_compat = (
        isinstance(metadata_compat, str) and bool(metadata_compat.strip())
    ) or (
        isinstance(metadata_compat, dict) and len(metadata_compat) > 0
    )
    if compatibility is None and not has_metadata_compat:
        result.add_error(
            "Workflow gate: version governance requires compatibility metadata (prefer top-level `compatibility`)."
        )

    version_pinned = False
    if isinstance(metadata, dict):
        for k, v in metadata.items():
            if isinstance(k, str) and "version" in k.lower() and isinstance(v, str) and v.strip():
                if re.search(r"\d", v):
                    version_pinned = True
                    break
    if not version_pinned and isinstance(compatibility, str) and re.search(r"\d", compatibility):
        version_pinned = True

    if not version_pinned:
        result.add_error(
            "Workflow gate: version appears unpinned. Add at least one metadata `*version*` string (e.g., `metadata.version: \"1.0\"` or dependency version pin)."
        )


def _validate_references_taxonomy_and_sizes(skill_dir: Path, frontmatter: dict[str, Any], result: VerificationResult) -> None:
    references_dir = skill_dir / "references"
    refs_field = frontmatter.get("references")

    if _is_non_empty_string_list(refs_field) and not references_dir.exists():
        result.add_error("Workflow gate: `references` field is present but `references/` directory is missing.")
        return

    if not references_dir.exists():
        return

    if not references_dir.is_dir():
        result.add_error("`references` must be a directory when present.")
        return

    reference_files = sorted([p for p in references_dir.rglob("*") if p.is_file()])
    md_reference_files = [p for p in reference_files if p.suffix.lower() == ".md"]

    # Deterministic taxonomy: all reference docs should live under references/<category>/...
    for ref_file in md_reference_files:
        rel = ref_file.relative_to(skill_dir)
        parts = rel.parts
        if len(parts) < 3:
            result.add_error(
                f"Workflow gate: reference file must be under taxonomy folder `references/<category>/...`, got `{rel.as_posix()}`."
            )
            continue
        category = parts[1]
        if category not in WORKFLOW_REFERENCE_TAXONOMY:
            allowed = ", ".join(sorted(WORKFLOW_REFERENCE_TAXONOMY))
            result.add_error(
                f"Workflow gate: invalid reference category `{category}` in `{rel.as_posix()}`. Allowed: {allowed}."
            )

        try:
            line_count = len(ref_file.read_text(encoding="utf-8").splitlines())
        except UnicodeDecodeError:
            result.add_error(f"Reference file must be UTF-8 decodable: `{rel.as_posix()}`")
            continue
        if line_count > 800:
            result.add_error(
                f"Workflow gate: reference file exceeds 800 lines ({line_count}): `{rel.as_posix()}`."
            )

    # Also validate listed references point to markdown files in taxonomy and exist (errors already partly covered).
    if isinstance(refs_field, list):
        for ref in refs_field:
            if not isinstance(ref, str) or not ref.strip():
                continue
            ref_path = Path(ref)
            resolved = skill_dir / ref_path
            if resolved.exists() and resolved.is_file():
                parts = ref_path.parts
                if len(parts) < 3 or parts[0] != "references":
                    result.add_error(
                        f"Workflow gate: `references` entries must use taxonomy paths under `references/<category>/...`, got `{ref}`."
                    )
                elif parts[1] not in WORKFLOW_REFERENCE_TAXONOMY:
                    result.add_error(
                        f"Workflow gate: `references` entry category `{parts[1]}` is not allowed: `{ref}`."
                    )

    # Fragmentation guard (warning): many micro-files suggests over-splitting.
    micro_files = []
    for ref_file in md_reference_files:
        try:
            line_count = len(ref_file.read_text(encoding="utf-8").splitlines())
        except UnicodeDecodeError:
            continue
        if line_count < 100:
            micro_files.append((ref_file, line_count))
    if len(md_reference_files) >= 5 and len(micro_files) >= max(3, len(md_reference_files) // 2):
        result.add_warning(
            "Workflow gate: many reference files are under 100 lines. Check fragmentation guard and merge semantically related files where possible."
        )


def _validate_brain_only_guidance(skill_md_text: str, result: VerificationResult, references_total_lines: int | None = None) -> None:
    lines = skill_md_text.splitlines()
    in_code = False
    code_lines = 0
    code_blocks = 0
    current_block_lines = 0
    max_block_lines = 0
    for line in lines:
        if line.strip().startswith("```"):
            if not in_code:
                in_code = True
                code_blocks += 1
                current_block_lines = 0
            else:
                in_code = False
                max_block_lines = max(max_block_lines, current_block_lines)
            continue
        if in_code:
            code_lines += 1
            current_block_lines += 1
    if in_code:
        max_block_lines = max(max_block_lines, current_block_lines)
        result.add_warning("SKILL.md contains an unclosed fenced code block.")

    if re.search(r"(?im)^#{1,6}\s+.*example", skill_md_text):
        result.add_warning(
            "Workflow gate: SKILL.md appears to contain example sections. Move examples into `references/` files."
        )
    if code_blocks > 0:
        result.add_warning(
            "Workflow gate: SKILL.md contains fenced code blocks. Keep SKILL.md focused on critical rules and move examples/code to `references/`."
        )
    if max_block_lines > 25 or code_lines > 60:
        result.add_error(
            "Workflow gate: SKILL.md contains large code block(s). Prompt rules require examples/large code blocks to be moved to `references/`."
        )

    if references_total_lines and references_total_lines >= 200:
        ratio = len(lines) / max(references_total_lines, 1)
        if ratio > 0.20:
            result.add_warning(
                f"Workflow gate: SKILL.md is {len(lines)} lines vs {references_total_lines} reference lines (~{ratio:.0%}). Target ~10% per your builder prompt."
            )


def _validate_custom_frontmatter_conventions(frontmatter: dict[str, Any], skill_dir: Path, result: VerificationResult) -> None:
    # Non-spec fields commonly used in your workflow. These are warnings/errors only when malformed.
    if not _is_non_empty_string_list(frontmatter.get("triggers")):
        result.add_error(
            "Workflow gate: `triggers` is required and must be a non-empty list of strings."
        )

    if "references" in frontmatter:
        refs = frontmatter["references"]
        if not _is_non_empty_string_list(refs):
            result.add_error(
                "Workflow gate: `references` is required and must be a non-empty list of relative file paths."
            )
            return
        for ref in refs:
            ref_path = Path(ref)
            if ref_path.is_absolute():
                result.add_error(
                    f"`references` entry must be relative to the skill root, got absolute path: {ref}"
                )
                continue
            if ".." in ref_path.parts:
                result.add_error(
                    f"`references` entry must not traverse outside the skill root: {ref}"
                )
                continue
            if not (skill_dir / ref_path).exists():
                result.add_error(f"`references` entry not found: {ref}")
    else:
        result.add_error("Workflow gate: `references` field is required in SKILL.md frontmatter.")

    _validate_activation(frontmatter, result)
    _validate_version_and_compatibility(frontmatter, result)


def _run_spec_validation(parsed: dict[str, Any], skill_dir: Path, body: str | None, result: VerificationResult) -> None:
    _validate_name_spec(parsed.get("name"), skill_dir.name, result)
    _validate_description_spec(parsed.get("description"), result)
    _validate_optional_string_field_spec("license", parsed.get("license"), result)
    _validate_optional_string_field_spec(
        "compatibility", parsed.get("compatibility"), result, max_len=500
    )
    _validate_metadata_spec(parsed.get("metadata"), result)
    _validate_allowed_tools_spec(parsed.get("allowed-tools"), result)
    if body is None or not body.strip():
        result.add_spec_warning("SKILL.md has no Markdown body after frontmatter.")


def _calc_grade(errors: int, warnings: int, *, error_weight: int, warning_weight: int) -> int:
    score = 100 - (errors * error_weight) - (warnings * warning_weight)
    if score < 0:
        return 0
    if score > 100:
        return 100
    return score


def _finalize_grades(result: VerificationResult) -> None:
    result.spec_grade = _calc_grade(
        len(result.spec_errors),
        len(result.spec_warnings),
        error_weight=25,
        warning_weight=4,
    )
    result.strict_grade = _calc_grade(
        len(result.errors),
        len(result.warnings),
        error_weight=15,
        warning_weight=3,
    )
    result.spec_passed = len(result.spec_errors) == 0
    result.strict_passed = result.spec_passed and result.strict_grade >= result.strict_threshold


def verify_skill_directory(skill_dir: str | Path) -> VerificationResult:
    skill_dir = Path(skill_dir).resolve()
    result = VerificationResult(skill_dir=skill_dir, skill_md_path=skill_dir / "SKILL.md")

    if not skill_dir.exists() or not skill_dir.is_dir():
        result.add_error(f"Skill path is not a directory: {skill_dir}")
        result.add_spec_error(f"Skill path is not a directory: {skill_dir}")
        _finalize_grades(result)
        return result

    skill_md = result.skill_md_path
    if not skill_md.exists():
        result.add_error(f"Missing required file: {skill_md.name}")
        result.add_spec_error(f"Missing required file: {skill_md.name}")
        _finalize_grades(result)
        return result

    _validate_optional_dirs(skill_dir, result)
    _validate_top_level_layout(skill_dir, result)

    try:
        text = skill_md.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        result.add_error("SKILL.md must be UTF-8 decodable text.")
        result.add_spec_error("SKILL.md must be UTF-8 decodable text.")
        _finalize_grades(result)
        return result
    except OSError as exc:
        result.add_error(f"Unable to read SKILL.md: {exc}")
        result.add_spec_error(f"Unable to read SKILL.md: {exc}")
        _finalize_grades(result)
        return result

    split = _split_frontmatter(text)
    if split is None:
        result.add_error("SKILL.md must start with YAML frontmatter delimited by `---`.")
        result.add_spec_error("SKILL.md must start with YAML frontmatter delimited by `---`.")
        _finalize_grades(result)
        return result

    frontmatter_text, body = split
    result.body = body
    _validate_yaml_frontmatter_safety(frontmatter_text, result)

    try:
        parsed = yaml.safe_load(frontmatter_text) if frontmatter_text.strip() else None
    except yaml.YAMLError as exc:
        result.add_error(f"Invalid YAML frontmatter in SKILL.md: {exc}")
        result.add_spec_error(f"Invalid YAML frontmatter in SKILL.md: {exc}")
        _finalize_grades(result)
        return result

    if not isinstance(parsed, dict):
        result.add_error("SKILL.md frontmatter must be a YAML mapping/object.")
        result.add_spec_error("SKILL.md frontmatter must be a YAML mapping/object.")
        _finalize_grades(result)
        return result

    result.frontmatter = parsed

    _validate_name(parsed.get("name"), skill_dir.name, result)
    _validate_description(parsed.get("description"), result)
    _validate_optional_string_field("license", parsed.get("license"), result)
    _validate_optional_string_field(
        "compatibility", parsed.get("compatibility"), result, max_len=500
    )
    _validate_metadata(parsed.get("metadata"), result)
    _validate_allowed_tools(parsed.get("allowed-tools"), result)
    _validate_custom_frontmatter_conventions(parsed, skill_dir, result)
    _validate_references_taxonomy_and_sizes(skill_dir, parsed, result)
    _run_spec_validation(parsed, skill_dir, result.body, result)

    if result.body is None or not result.body.strip():
        result.add_warning("SKILL.md has no Markdown body after frontmatter.")

    skill_md_lines = text.splitlines()
    if len(skill_md_lines) > 500:
        result.add_warning(
            f"SKILL.md has {len(skill_md_lines)} lines; Agent Skills recommends keeping it under 500 lines."
        )
    references_total_lines = 0
    for ref_file in (skill_dir / "references").rglob("*.md") if (skill_dir / "references").exists() else []:
        try:
            references_total_lines += len(ref_file.read_text(encoding="utf-8").splitlines())
        except UnicodeDecodeError:
            continue
    _validate_brain_only_guidance(text, result, references_total_lines if references_total_lines else None)
    _finalize_grades(result)

    return result


def format_verification_report(result: VerificationResult) -> str:
    lines: list[str] = []
    lines.append(f"[verify] {result.skill_dir}")
    lines.append(
        f"[verify] SPEC  grade={result.spec_grade}/100 status={'PASS' if result.spec_passed else 'FAIL'}"
    )
    lines.append(
        f"[verify] STRICT grade={result.strict_grade}/100 status={'PASS' if result.strict_passed else 'FAIL'} threshold={result.strict_threshold}"
    )

    if result.spec_issues:
        lines.append("[verify] Spec Findings")
        for issue in result.spec_errors:
            lines.append(f"  SPEC ERROR: {issue.message}")
        for issue in result.spec_warnings:
            lines.append(f"  SPEC WARN: {issue.message}")

    if result.issues:
        lines.append("[verify] Strict Findings")
        for issue in result.errors:
            lines.append(f"  STRICT ERROR: {issue.message}")
        for issue in result.warnings:
            lines.append(f"  STRICT WARN: {issue.message}")
    return "\n".join(lines)


def verify_or_raise(skill_dir: str | Path) -> VerificationResult:
    result = verify_skill_directory(skill_dir)
    if not result.is_valid:
        raise ValueError(format_verification_report(result))
    return result
