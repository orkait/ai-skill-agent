# Skills CLI

Local registry for AI agent skills with a Typer-based CLI.

## Layout

```
~/skills/
├─ skills/          # global registry — one folder per skill
├─ skill.build      # LLM prompt: build a skill from docs/references
├─ skill.improve    # LLM prompt: improve a skill to STRICT pass
├─ cli.py
└─ pyproject.toml
```

## Workflow

1. Build a skill with an LLM using `~/skills/skill.build`
2. Verify + register: `skills register <path>`
3. Install to agents: `skills install <name> --agent all --project <repo>`
4. Improve toward STRICT: `skills improve <name-or-path>`, then run `~/skills/skill.improve <name-or-path>` in Claude/Gemini CLI

## Commands

| Command | What it does |
|---------|-------------|
| `skills init` | Create registry dirs, seed prompts |
| `skills create <name>` | Scaffold minimal skill in registry |
| `skills register <path>` | Validate + copy skill into registry |
| `skills verify <path\|name>` | Report SPEC + STRICT grades (read-only) |
| `skills list` | List all registered skill names |
| `skills install [<name>]` | Copy from registry to agent dirs |
| `skills sync [<name>...]` | Refresh agent copies from registry |
| `skills improve <name\|path>` | Preflight STRICT verify for a registered skill or local folder + show LLM invocation |
| `skills desync [<name>]` | Remove skill from agent dirs (`--force`) |
| `skills deregister [<name>]` | Remove skill from registry (`--force`) |
| `skills where` | Print registry + agent target paths |

## Agent Targets

| Agent | Path |
|-------|------|
| `codex` | `~/.codex/skills` (always global) |
| `claude` | `<project>/.claude/skills` |
| `kiro` | `<project>/.kiro/skills` |
| `gemini` | `<project>/.gemini/skills` |


## Prompt to fix Skill via LLM
```
Can you read and execute `~/skills/skill.improve C:\skills\<folder_name>`? Implement improvements for all skill if it fail to register.
Then trigger `skills list` to check if it actually registrated.
```
> Note: Run this prompt if your skill wont register but you have good context of your skill


See `flow.md` for architecture details, grading rules, and the improve loop.

If `skills register <path>` is blocked by the verification gate, use:
- `skills improve <path>` to repair the folder in-place, then run `skills register <path>` again.
