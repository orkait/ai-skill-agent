---
name: design-patterns-skill
description: Apply core programming principles and design patterns from Clean Code, The Pragmatic Programmer, Code Complete, Refactoring, and Design Patterns. Use when writing code, reviewing PRs, refactoring, or designing system architecture.
triggers:
  - "code review"
  - "design pattern"
  - "refactor"
  - "clean code"
  - "SOLID"
  - "code quality"
  - "architecture design"
  - "code generation"
activation:
  mode: fuzzy
  priority: normal
  triggers:
    - "code review"
    - "design pattern"
    - "refactor"
    - "clean code"
    - "SOLID"
    - "code quality"
    - "architecture design"
    - "code generation"
compatibility: ">=1.0.0"
metadata:
  version: "1.0.0"
references:
  - references/patterns/readability.md
  - references/patterns/simplicity.md
  - references/patterns/design-architecture.md
  - references/patterns/testing.md
  - references/patterns/error-handling.md
  - references/patterns/maintainability.md
---

# Design Patterns & Programming Principles

## Overview

Structured guidance on programming principles and design patterns from foundational software engineering books. Ensures code follows industry-standard practices for readability, maintainability, simplicity, and architectural soundness.

## When to Apply

- **Code Generation:** Writing new functions, classes, or modules
- **Code Review:** Evaluating pull requests or existing codebases
- **Refactoring:** Improving code structure and clarity
- **Architecture Design:** Choosing appropriate patterns and abstractions

---

## Core Philosophy

1. **Readability over cleverness** — Code is read more than written
2. **Simplicity over complexity** — Use the simplest solution that works
3. **Testability by design** — Write code that's easy to test
4. **Incremental improvement** — Leave code better than you found it
5. **Patterns as tools** — Apply patterns when they clarify, not by default

---

## Principle Categories

### 1. Readability & Clarity
- Descriptive naming, consistent formatting, self-documenting code, small focused functions
- **Reference:** `references/patterns/readability.md`

### 2. Simplicity & Efficiency
- KISS, DRY, YAGNI
- **Reference:** `references/patterns/simplicity.md`

### 3. Design & Architecture
- SRP, composition over inheritance, program to interfaces
- Patterns: Factory, Strategy, Observer, Decorator, Adapter, Command, Singleton
- **Reference:** `references/patterns/design-architecture.md`

### 4. Testing & Quality
- Automated testing, focused assertions, edge case coverage
- **Reference:** `references/patterns/testing.md`

### 5. Error Handling
- Clear error messages, early validation, proper exception usage
- **Reference:** `references/patterns/error-handling.md`

### 6. Maintainability
- Boy Scout Rule, continuous refactoring, atomic commits, automation
- **Reference:** `references/patterns/maintainability.md`

---

## AI-Specific Guidance

When generating or reviewing code, always:
1. Check for AI pitfalls listed in each principle
2. Avoid pattern prediction bias — don't use patterns just because they're common
3. Question generic naming — resist `data`, `temp`, `result` without context
4. Validate edge cases — don't skip error handling
5. Keep functions focused — resist combining unrelated operations
6. Match project conventions — maintain consistency with existing codebase

---

## Quick Reference

| Situation | Apply |
|-----------|-------|
| Function > 20 lines | Split into smaller functions (SRP) |
| Repeated code blocks | Extract to function/constant (DRY) |
| Complex conditionals | Strategy or State pattern |
| Object creation logic | Factory pattern |
| Cross-cutting concerns | Decorator or Observer pattern |
| Incompatible interfaces | Adapter pattern |
| Need undo/logging | Command pattern |
| Global access point | Singleton (use sparingly) |

---

## Sources

- *Clean Code* — Robert C. Martin
- *The Pragmatic Programmer* — Andrew Hunt & David Thomas
- *Code Complete* — Steve McConnell
- *Refactoring* — Martin Fowler
- *Design Patterns* — Gang of Four
