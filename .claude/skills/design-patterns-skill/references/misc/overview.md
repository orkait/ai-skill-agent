# Design Patterns & Programming Principles Skill

A comprehensive Kiro skill that provides structured guidance on programming principles and design patterns from foundational software engineering books.

## Overview

This skill encapsulates best practices from:
- *Clean Code* by Robert C. Martin
- *The Pragmatic Programmer* by Andrew Hunt & David Thomas
- *Code Complete* by Steve McConnell
- *Refactoring* by Martin Fowler
- *Design Patterns* by Gang of Four

## Installation

### For Workspace (Project-Specific)
```bash
mkdir -p .kiro/skills
cp -r design-patterns .kiro/skills/
```

### For Global (All Projects)
```bash
mkdir -p ~/.kiro/skills
cp -r design-patterns ~/.kiro/skills/
```

## Structure

```
design-patterns/
├── SKILL.md                      # Main skill definition
├── README.md                     # This file
└── references/
    ├── readability.md            # Naming, formatting, documentation
    ├── simplicity.md             # KISS, DRY, YAGNI principles
    ├── design-architecture.md    # SRP, patterns, composition
    ├── testing.md                # Testing strategies and best practices
    ├── error-handling.md         # Validation, exceptions, recovery
    └── maintainability.md        # Refactoring, commits, automation
```

## Usage

The skill activates automatically when:
- Writing new code
- Reviewing pull requests
- Refactoring existing code
- Designing system architecture
- Assisting with AI code generation

## Principle Categories

### 1. Readability & Clarity
- Descriptive naming conventions
- Consistent code formatting
- Self-documenting code principles
- Small, focused functions

### 2. Simplicity & Efficiency
- KISS (Keep It Simple, Stupid)
- DRY (Don't Repeat Yourself)
- YAGNI (You Aren't Gonna Need It)
- Avoiding premature optimization

### 3. Design & Architecture
- Single Responsibility Principle (SRP)
- Composition over Inheritance
- Program to Interfaces
- Essential Design Patterns:
  - Factory Pattern
  - Strategy Pattern
  - Observer Pattern
  - Decorator Pattern
  - Adapter Pattern
  - Command Pattern
  - Singleton Pattern

### 4. Testing & Quality
- Test-driven development approach
- Focused test assertions
- Test pyramid (unit/integration/e2e)
- Mocking and test doubles

### 5. Error Handling
- Clear error messages
- Early input validation
- Exception hierarchies
- Recovery strategies

### 6. Maintainability
- Boy Scout Rule
- Continuous refactoring
- Incremental commits
- Automation and tooling

## AI-Specific Guidance

This skill includes specific guidance for AI code generation, helping avoid common pitfalls such as:
- Generic naming (`data`, `temp`, `result`)
- Over-commenting obvious code
- Skipping edge case validation
- Applying patterns unnecessarily
- Creating monolithic functions
- Duplicating code structures

## Quick Reference Examples

### Before & After

**Poor Code:**
```python
def proc(u):
    if u['age'] < 13: return False
    db.save(u)
    email.send(u['email'], 'Welcome')
    return True
```

**Improved Code:**
```python
def is_eligible_user(user):
    return user['age'] >= 13

def save_user(user):
    db.save(user)

def send_welcome_email(user):
    email.send(user['email'], 'Welcome to the platform')

def register_user(user):
    if not is_eligible_user(user):
        raise ValueError('User must be 13 or older')
    save_user(user)
    send_welcome_email(user)
```

## When to Apply

| Situation | Recommended Principle/Pattern |
|-----------|------------------------------|
| Function > 20 lines | Split using SRP |
| Repeated code blocks | Extract with DRY |
| Complex conditionals | Strategy or State pattern |
| Object creation complexity | Factory pattern |
| Cross-cutting concerns | Decorator or Observer |
| Incompatible interfaces | Adapter pattern |
| Need undo/logging | Command pattern |

## Contributing

This skill is structured to be easily extended. To add new principles or patterns:

1. Update the relevant reference file in `references/`
2. Add a cross-reference in `SKILL.md`
3. Include examples with "Do", "Don't", and "AI Pitfalls" sections

## License

This skill is based on principles from publicly available software engineering literature and industry best practices.

## Additional Resources

- [The 7 Most Important Software Design Patterns](https://learningdaily.dev/the-7-most-important-software-design-patterns-d60e546afb0e)
- [Refactoring Guru - Design Patterns](https://refactoring.guru/design-patterns)
- [SOLID Principles](https://en.wikipedia.org/wiki/SOLID)

## Version

1.0.0 - Initial release
