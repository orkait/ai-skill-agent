# AI Skill Agent (Local Skills Registry)

Minimal local registry for AI agent skills with a Typer-based CLI.

Validation is aligned with the Agent Skills specification: `https://agentskills.io/specification`
and also supports a stricter workflow-quality grade derived from `~/skill.build`.

## What This Does

- Stores all generated skills in one place: `~/skills/skills`
- Stores the skill-builder prompt at: `~/skills/skill.build`
- Uses a local Python CLI (`~/skills/cli.py`) to distribute skills to agent folders
- Keeps agent-specific copy logic out of the LLM prompt (saves tokens)

## Folder Layout

```text
~/skills
├─ skills/          # Global registry of generated skills
├─ skill.build      # Prompt used with LLMs to build skills from refs
├─ cli.py           # Typer CLI to register/install/sync skills
└─ pyproject.toml   # Local package metadata (installed via pip -e)
```

Related improve prompt:
- `~/skills/skill.improve` (used as: `~/skills/skill.improve <skill_name>`)

## Workflow (Minimal)

1. Ask an LLM to build a skill using `~/skills/skill.build`.
2. Provide a skill name + reference folder (for example `reactflow`, `~/Downloads/reactflow-reference`).
3. Save the generated skill folder locally.
4. Register it into the global registry:
   - `skills verify <path-to-generated-skill>` (optional pre-check; prints spec + strict grades)
   - `skills register <path-to-generated-skill>` (runs grading automatically; default gate is `spec`)
   - or scaffold first: `skills create <name>`
5. Install it to one or more agents:
   - `skills install <skill-name> --agent codex,claude --project <repo-path>`
   - or `skills sync --agent all --project <repo-path>` for all registered skills
6. Remove skill copies or registry entries when needed (destructive; requires `--force`):
   - `skills desync <skill-name> --agent all --project <repo-path> --force`
   - `skills deregister <skill-name> --force`
7. Improve a registered skill toward STRICT mode using the LLM prompt:
   - Run `skills improve <skill_name>` for a preflight + exact LLM invocation
   - Then run `~/skills/skill.improve <skill_name>` in Gemini/Claude CLI
   - The prompt will instruct the LLM to run `skills verify <skill_name> --strict --verbose` and iteratively fix the registered skill in-place

## Default Project Root Behavior

- If you run `skills install` or `skills sync` without `--project`, the CLI uses the current working directory.
- This affects agent-local targets:
  - `claude` -> `<current-dir>/.claude/skills`
  - `kiro` -> `<current-dir>/.kiro/skills`
  - `gemini` -> `<current-dir>/.gemini/skills`
- `codex` always installs to `~/.codex/skills`.

## What Is Working (Verified)

- `skills` CLI installed globally from local path using editable install (`pip install -e ~/skills --no-deps`)
- `skills where --project <repo>`
- `skills list`
- `skills verify <skill-folder>` validates a skill folder against Agent Skills spec checks
- `skills verify <skill-name>` also works for registered skills in `~/skills/skills`
- `skills verify <skill-folder>` prints two grades:
  - `SPEC` (agentskills.io spec-only)
  - `STRICT` (your stricter workflow quality rules)
- `skills register <skill-folder> --install --agent codex,claude --project <repo>`
- `skills install` (with no args) installs all registered skills
- `skills desync` removes installed copies from agent directories (requires `--force`)
- `skills deregister` removes from the global registry (requires `--force`)
- Running from `C:\skills` installs agent-local copies into `C:\skills\.claude`, `C:\skills\.kiro`, `C:\skills\.gemini` unless `--project` is passed

## Core Commands

```bash
skills init
skills create my-skill
skills list
skills verify C:/path/to/skill
skills verify C:/path/to/skill --gate strict
skills verify lenis-react --strict --verbose --output text
skills verify C:/path/to/skill --verbose
skills verify C:/path/to/skill --output json
skills register C:/path/to/skill --install --agent codex,claude --project .
skills register C:/path/to/skill --gate strict
skills register C:/path/to/skill --verbose --output text
skills improve lenis-react
skills deregister my-skill --force
skills install reactflow-v12 --agent all --project .
skills sync --agent all --project .
skills sync lenis-react reactflow-v12 --agent codex
skills desync reactflow-v12 --agent all --project . --force
skills where --project .
skills improve-path     # low-level helper: prints ~/skills/skill.improve path
```

## Example Session (PowerShell)

```powershell
PS C:\skills> skills register lenis-react
[register] C:\skills\lenis-react -> C:\Users\Admin\skills\skills\lenis-react

PS C:\skills> skills list
lenis-react
reactflow-v12

PS C:\skills> skills install
[install] lenis-react -> codex (C:\Users\Admin\.codex\skills\lenis-react)
[install] lenis-react -> claude (C:\skills\.claude\skills\lenis-react)
[install] lenis-react -> kiro (C:\skills\.kiro\skills\lenis-react)
[install] lenis-react -> gemini (C:\skills\.gemini\skills\lenis-react)
[install] reactflow-v12 -> codex (C:\Users\Admin\.codex\skills\reactflow-v12)
[install] reactflow-v12 -> claude (C:\skills\.claude\skills\lenis-react)
[install] reactflow-v12 -> kiro (C:\skills\.kiro\skills\lenis-react)
[install] reactflow-v12 -> gemini (C:\skills\.gemini\skills\lenis-react)
```

Use `--project` to target a specific repo:

```powershell
skills install --project C:\codingFiles\orkait\nitrogen
```

## Registration Verification (Agent Skills Spec)

- `skills register` now validates the source skill before copying it into the registry (first gate).
- If validation fails, registration stops and prints clear errors/warnings.
- `skills verify <path>` runs the same checks manually.
- Validation combines:
  - Agent Skills spec checks (`https://agentskills.io/specification`)
  - Workflow bundle checks derived from `~/skill.build` (1-3-10, taxonomy, activation, reference limits, version governance)
- Output is graded with two binary statuses (no partial pass label):
  - `SPEC`: pass/fail against spec-oriented checks
  - `STRICT`: pass/fail against strict workflow checks using a score threshold (currently `80`)
- `register` and `verify` support `--gate spec|strict`:
  - `--gate spec` (default) requires only spec pass
  - `--gate strict` requires strict pass
- `verify` and `register` also support report formatting flags:
  - `--verbose` = print full findings (errors + warnings, grouped)
  - `--output pretty|text|json` = terminal-friendly, plain text, or machine-readable output
- `verify` also supports `--strict` as a shortcut for `--gate strict`
- Examples of checked items:
  - `SKILL.md` exists and starts with YAML frontmatter
  - `name` and `description` exist and have valid types/constraints
  - `name` matches the parent skill folder name
  - optional spec fields (`license`, `compatibility`, `metadata`, `allowed-tools`) use valid types
  - workflow-required custom fields (`triggers`, `references`, `activation`) are validated
  - `references` paths must exist, be relative, and follow the taxonomy (`references/<category>/...`)
  - reference files are checked for UTF-8 + max 800 lines
  - YAML safety rule for unquoted `@...` trigger items in frontmatter
  - SKILL.md is checked for large code blocks/examples (brain-only guidance)

## Improve Prompt (`~/skills/skill.improve`)

- `skills init --force-improve-prompt` writes/refreshes `~/skills/skill.improve`
- `skills improve <skill_name>` validates the registered skill exists, runs STRICT verify (by default), and prints the exact LLM invocation
- Intended usage in an LLM CLI:

```powershell
~/skills/skill.improve lenis-react
```

- The prompt instructs the LLM to:
  - parse `<skill_name>` from the invocation
  - check the registered skill exists at `~/skills/skills/<skill_name>`
  - run `skills verify <skill_name> --strict --verbose`
  - use STRICT findings to improve the registered skill in-place until STRICT passes (or ask for clarification)

Destructive cleanup examples:

```powershell
skills desync lenis-react --agent codex,claude --project C:\codingFiles\orkait\nitrogen --force
skills deregister lenis-react --force
skills desync --all --project C:\codingFiles\orkait\nitrogen --force
skills deregister --all --force
```

## Agent Targets

- `codex` -> `~/.codex/skills`
- `claude` -> `<project>/.claude/skills`
- `kiro` -> `<project>/.kiro/skills`
- `gemini` -> `<project>/.gemini/skills`

## Sync Output

- `skills sync` now prints explicit update messages:
  - `[sync] updated <skill_name> -> <full_destination_path>`
- `skills sync` also supports syncing specific skills:
  - `skills sync <skill_1> <skill_2> ...`
