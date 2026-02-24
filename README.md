# AI Skill Agent (Local Skills Registry)

Minimal local registry for AI agent skills with a Typer-based CLI.

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

## Workflow (Minimal)

1. Ask an LLM to build a skill using `~/skills/skill.build`.
2. Provide a skill name + reference folder (for example `reactflow`, `~/Downloads/reactflow-reference`).
3. Save the generated skill folder locally.
4. Register it into the global registry:
   - `skills register <path-to-generated-skill>`
5. Install it to one or more agents:
   - `skills install <skill-name> --agent codex,claude --project <repo-path>`
   - or `skills sync --agent all --project <repo-path>` for all registered skills

## What Is Working (Verified)

- `skills` CLI installed globally from local path using editable install (`pip install -e ~/skills --no-deps`)
- `skills where --project <repo>`
- `skills list`
- `skills register <skill-folder> --install --agent codex,claude --project <repo>`

## Core Commands

```bash
skills init
skills list
skills register C:/path/to/skill --install --agent codex,claude --project .
skills install reactflow-v12 --agent all --project .
skills sync --agent all --project .
skills where --project .
```

## Agent Targets

- `codex` -> `~/.codex/skills`
- `claude` -> `<project>/.claude/skills`
- `kiro` -> `<project>/.kiro/skills`
- `gemini` -> `<project>/.gemini/skills`
