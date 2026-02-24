# Skills CLI — Flow & Design

## Directory Layout

```
~/skills/
├─ skills/                    # global registry — one folder per skill
│  └─ <skill-name>/
│     ├─ SKILL.md             # REQUIRED: YAML frontmatter + guidance body
│     ├─ references/          # categorized reference files
│     │  └─ <category>/       # api | hooks | types | patterns | architecture
│     │                       # performance | migration | validation | examples | misc
│     ├─ scripts/             # optional
│     ├─ assets/              # optional
│     └─ agents/              # optional
├─ skill.build                # LLM prompt: build a skill from docs/references
├─ skill.improve              # LLM prompt: improve a skill to STRICT pass
├─ cli.py
└─ pyproject.toml
```

## SKILL.md Schema

```yaml
---
name: my-skill                    # required — lowercase+hyphens, matches folder name
description: "..."                # required — 20-1024 chars
triggers:                         # required — non-empty string list
  - keyword
references:                       # required — relative paths to reference files
  - references/api/overview.md
activation:                       # required — controls agent invocation
  mode: strict                    # strict | fuzzy
  triggers: [keyword]
  priority: normal                # normal | high
compatibility: "lib@^1.0"         # optional — version pins
license: "MIT"                    # optional
metadata:                         # optional — string key-value pairs
  version: "1.0.0"
allowed-tools: "Bash Read Write"  # optional — space-delimited
---
```

> Trigger items starting with `@` must be quoted (e.g. `- "@xyflow/react"`).

---

## Registry State Transitions

```
[not registered]
      │
      ▼  skills create <name>
         └─ scaffold SKILL.md + references/misc/overview.md in registry
      │
      ▼  (edit locally or generate via skill.build + LLM)
      │
      ▼  skills register <path> [--gate spec|strict]
         └─ validate → enforce gate → copy into ~/skills/skills/<name>
      │
      ▼  skills verify <name> [--gate strict]
         └─ read-only: prints SPEC + STRICT grades and findings
      │
      ▼  skills improve <name>
         └─ preflight STRICT verify → print gaps → show LLM invocation
         └─ (LLM runs skill.improve, edits in-place, iterates until STRICT passes)
      │
      ▼  skills install <name> --agent all --project <repo>
         └─ copy from registry to each agent directory
      │
      ├─▶  skills sync [<name>]
      │       └─ re-copy from registry to agents (refresh after edits)
      │
      ▼  skills desync <name> --agent all --force
         └─ remove copies from agent directories
      │
      ▼  skills deregister <name> --force
         └─ remove from registry
      │
[not registered]
```

---

## Distribution Flow

```
~/skills/skills/<name>/              ← single source of truth

        ├──▶  ~/.codex/skills/<name>/              always global (HOME-based)
        ├──▶  <project>/.claude/skills/<name>/     project-scoped
        ├──▶  <project>/.kiro/skills/<name>/       project-scoped
        └──▶  <project>/.gemini/skills/<name>/     project-scoped
```

If `--project` is omitted, the current working directory is used. `codex` ignores `--project` and always uses `~/.codex`.

---

## Improve Loop

```
skills improve <name>
      └─▶ STRICT preflight verify — surface gaps

~/skills/skill.improve <name>        ← invoked inside Claude/Gemini CLI
      └─▶ LLM reads STRICT findings
      └─▶ edits files in-place inside ~/skills/skills/<name>/
            - moves code blocks out of SKILL.md → references/examples/
            - fixes missing frontmatter fields
            - reorganizes files into taxonomy folders
            - pins version in compatibility or metadata
      └─▶ re-runs: skills verify <name> --strict --verbose
      └─▶ iterates until STRICT passes

skills sync <name> --agent all       ← push improved skill to agents
```

---

## Verification Pipeline

`verify_skill_directory(path)` runs these checks in order:

1. Dir exists + SKILL.md present
2. Optional dirs (scripts/, references/, assets/) are valid if present
3. No unexpected top-level files outside `{SKILL.md, references, scripts, assets, agents}`
4. SKILL.md is valid UTF-8
5. Frontmatter parsed from `---` delimiters via `yaml.safe_load`
6. Unquoted `@` trigger items flagged
7. Spec field checks — name format, description length, license/compatibility types, metadata values, allowed-tools
8. Workflow field checks — triggers, references (exist + taxonomy), activation shape, version governance
9. Reference taxonomy — each file under `references/<category>/`, category must be in allowed set
10. File size limits — each reference file ≤ 800 lines
11. Fragmentation guard — warn if 5+ files with 50%+ under 100 lines
12. Brain-only check — no large code blocks in SKILL.md (>25 lines or >60 total code lines)
13. Grades finalized

### Grading

```
SPEC grade   = 100 − (spec_errors × 25) − (spec_warnings × 4)
STRICT grade = 100 − (all_errors  × 15) − (all_warnings  × 3)

spec_passed   = zero spec errors
strict_passed = spec_passed AND strict_grade ≥ 80
```

### Gate Enforcement

| Gate     | Fails when               | Default for   |
|----------|--------------------------|---------------|
| `spec`   | any spec error           | `register`, `verify` |
| `strict` | strict_passed == False   | opt-in via `--gate strict` / `--strict` |

---

## Command Summary

| Command | What it does |
|---------|-------------|
| `skills init` | Create registry dirs, seed skill.build + skill.improve |
| `skills create <name>` | Scaffold minimal skill in registry |
| `skills register <path>` | Validate + copy skill into registry |
| `skills verify <path\|name>` | Report SPEC + STRICT grades (read-only) |
| `skills list` | List all registered skill names |
| `skills install [<name>]` | Copy from registry to agent dirs |
| `skills sync [<name>...]` | Refresh agent copies from registry |
| `skills desync [<name>]` | Remove skill from agent dirs (`--force`) |
| `skills deregister [<name>]` | Remove skill from registry (`--force`) |
| `skills improve <name>` | Preflight STRICT verify + show LLM invocation |
| `skills where` | Print registry path + all agent target paths |

---

## Key Decisions

- **LLMs only write to registry** — `skill.build` instructs the LLM to never copy to agent dirs. Distribution is always CLI-driven (install/sync).
- **Two independent grades** — SPEC (agentskills.io compliance) and STRICT (workflow quality). Either can gate registration; defaults to SPEC-only.
- **codex is global, others are project-scoped** — codex always installs to `~/.codex/skills`; claude/kiro/gemini use `<project>/.<agent>/skills`.
- **Destructive ops require `--force`** — desync and deregister will not run without it, preventing accidental deletion.
- **Sync = overwrite, not diff** — always replaces agent copies wholesale from registry; no incremental patching.
- **Brain-only SKILL.md** — no code examples in SKILL.md body; all examples belong in `references/examples/`. Keeps the guidance file concise and LLM-token-efficient.
- **References taxonomy enforced** — files must live under `references/<category>/` with a controlled category set; flat reference dumps are rejected.
