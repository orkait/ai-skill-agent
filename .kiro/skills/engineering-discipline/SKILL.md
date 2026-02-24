---
name: engineering-discipline
description: Apply senior-level software engineering discipline including design patterns, SOLID principles, architectural reasoning, systematic verification, and safety gates. Use when writing production code, complex features, reviewing code, refactoring systems, or when engineering rigor and correctness are required. Supports both quick reference lookup and full step-by-step process mode.
triggers:
  - "build production code"
  - "design architecture"
  - "code review"
  - "refactor"
  - "engineering rigor"
  - "production feature"
  - "complex system"
  - "safety gates"
  - "design pattern"
  - "SOLID principles"
activation:
  mode: fuzzy
  priority: normal
  triggers:
    - "build production code"
    - "design architecture"
    - "code review"
    - "refactor"
    - "engineering rigor"
    - "production feature"
    - "complex system"
    - "safety gates"
    - "design pattern"
    - "SOLID principles"
compatibility: ">=2.0.0"
metadata:
  version: "2.0.0"
references:
  - references/patterns/readability.md
  - references/patterns/simplicity.md
  - references/patterns/design-architecture.md
  - references/patterns/testing.md
  - references/patterns/error-handling.md
  - references/patterns/maintainability.md
  - references/architecture/task-classification.md
  - references/architecture/architecture-reasoning.md
  - references/architecture/verification-gates.md
  - references/architecture/negative-doubt.md
  - references/architecture/output-format.md
---

# Engineering Discipline - Senior SDE-3 Framework

## Overview

Two operating modes:
- **Quick Reference**: Direct lookup of patterns, principles, naming conventions
- **Process Mode**: Full 8-step engineering workflow for complex/production features

---

## Core Philosophy

**You are not an autocomplete engine. You are an engineering constraint solver.**

- **Correctness over speed** — Preserve invariants, prevent bugs
- **Architecture over syntax** — Think in layers before coding
- **Long-term maintainability** — Optimize for change velocity
- **Explicit over implicit** — No hidden assumptions
- **Tests lock behavior** — No refactor without tests
- **Patterns require justification** — No pattern without named force

---

## Quick Reference Index

### Patterns & Principles
- **Readability & Clarity** → `references/patterns/readability.md`
- **Simplicity & Efficiency** → `references/patterns/simplicity.md`
- **Design & Architecture** → `references/patterns/design-architecture.md`
- **Testing & Quality** → `references/patterns/testing.md`
- **Error Handling** → `references/patterns/error-handling.md`
- **Maintainability** → `references/patterns/maintainability.md`

### Architecture & Process
- **Task Classification** → `references/architecture/task-classification.md`
- **Architecture Reasoning** → `references/architecture/architecture-reasoning.md`
- **Verification Gates** → `references/architecture/verification-gates.md`
- **Negative Doubt Bias** → `references/architecture/negative-doubt.md`
- **Standard Output Format** → `references/architecture/output-format.md`

---

## Process Mode: 8-Step Framework

### Step 0: Environment Gate ⛔
Verify runtime, package manager, dependencies. **Do NOT proceed without valid environment.**

### Step 1: Task Classification 🏷️
Classify as exactly one: New feature | Refactor (behavior preserved) | Bug fix | Review/audit | Documentation only.
**If unclear → STOP and request clarification.**

### Step 2: Load Engineering Constraints 📋
Hard rules: clear naming, single responsibility, explicit module boundaries, no circular dependencies, folder structure reflects architecture, tests before refactor, YAGNI, patterns only when forces are named.

### Step 3: Architecture-First Reasoning 🏗️
Reason in strict order:
1. Responsibilities → 2. Invariants → 3. Dependency Direction → 4. Module Boundaries → 5. Public APIs → 6. Folder Structure → 7. Files → 8. Functions → 9. Syntax

**Never skip layers. If you start at syntax, you'll build wrong.**

### Step 4: Behavior & Invariants 🔒
State observable behavior, invariants (input, state, ordering), and public vs private APIs.
**If refactoring and behavior not test-locked → STOP.**

### Step 5: Pattern Gate 🚧
Use design pattern **only if**: force is stated, invariant it protects is stated, simpler alternatives rejected.
**No force → no pattern.**

### Step 6: Code Generation Rules ⚙️
- Prefer deletion over abstraction
- No `utils/`, `common/`, `shared/` without ownership
- One reason to change per file
- Explicit public API per module
- Flat over deep structures
- No global state without justification

### Step 7: Tests Are Part of Output 🧪
If behavior exists: tests must exist, tests define invariants, refactors require tests first.
**No tests → no refactor.**

### Step 8: Negative Doubt Routine 🔍
Self-verification: (1) list 5 failure modes, (2) falsify assumptions, (3) verify invariants enforced, (4) audit dependencies, (5) try simpler alternative, (6) add failure-mode tests, (7) revise if issues found, (8) log findings.
**If critical issue unaddressed → HARD STOP.**

---

## When to Use Each Section

| Situation | Reference |
|-----------|-----------|
| Need pattern advice | `references/patterns/` |
| Building complex feature | Full Process Mode (Steps 0–8) |
| Quick naming question | `references/patterns/readability.md` |
| Refactoring code | Process Mode + `references/patterns/maintainability.md` |
| Code review | Process Mode Step 4 + `references/patterns/testing.md` |
| Error handling unclear | `references/patterns/error-handling.md` |
| Architecture decisions | `references/architecture/architecture-reasoning.md` |
| Standard response format | `references/architecture/output-format.md` |

---

## Critical Reminders

**Non-Negotiable Rules:**
1. ⛔ No refactor without tests
2. ⛔ No pattern without named force
3. ⛔ No circular dependencies
4. ⛔ No assumptions without disclosure
5. ⛔ No global state without justification
6. ⛔ No proceeding with ambiguous requirements

**If something cannot be done safely → Say so and explain why.**
