# Engineering Discipline Skill

A comprehensive Kiro skill combining design patterns, architectural reasoning, and systematic engineering verification for building production-quality software.

## Overview

This skill provides **two complementary modes**:

### 🔍 Quick Reference Mode
Fast lookup for design patterns, principles, and best practices.

**Use when:**
- Looking up specific patterns
- Checking naming conventions
- Quick code review questions
- Learning about principles

### ⚙️ Process Mode  
Full engineering workflow with verification gates for complex systems.

**Use when:**
- Building production features
- Designing critical systems
- Security-sensitive code
- Complex architectures requiring rigor

## Installation

### Workspace Installation (Project-Specific)
```bash
mkdir -p .kiro/skills
cp -r engineering-discipline .kiro/skills/
```

### Global Installation (All Projects)
```bash
mkdir -p ~/.kiro/skills
cp -r engineering-discipline ~/.kiro/skills/
```

## Structure

```
engineering-discipline/
├── SKILL.md                          # Main skill with mode routing
├── README.md                         # This file
└── references/
    ├── principles/                   # Design patterns & best practices
    │   ├── readability.md           # Naming, formatting, documentation
    │   ├── simplicity.md            # KISS, DRY, YAGNI
    │   ├── design-architecture.md   # Patterns, SRP, composition
    │   ├── testing.md               # TDD, test pyramid, mocking
    │   ├── error-handling.md        # Validation, exceptions
    │   └── maintainability.md       # Refactoring, commits, tooling
    └── process/                      # Engineering workflow
        ├── task-classification.md   # Classify before coding
        ├── architecture-reasoning.md # 9-layer thinking hierarchy
        ├── verification-gates.md    # Safety checkpoints
        └── negative-doubt.md        # Adversarial verification
```

## Quick Reference Mode Examples

### Pattern Lookup
```
User: "What pattern should I use for swappable payment processors?"

Response: "Use the Strategy Pattern. It allows you to encapsulate 
different payment algorithms (Stripe, PayPal, etc.) and make them 
interchangeable at runtime..."
```

### Principle Check
```
User: "Is this function too long?"

Response: "Yes. At 45 lines with mixed abstraction levels, it violates 
the Single Responsibility Principle. Consider extracting..."
```

### Best Practice
```
User: "How should I name this variable?"

Response: "Use a descriptive noun that indicates purpose. Instead of 
'data', use 'user_records' or 'payment_transactions'..."
```

## Process Mode Examples

### Building a System
```
User: "Build a rate limiting service for our API"

Response:
**Task Classification:** New Feature

**Architecture:**
Responsibilities:
- RateLimiter: Track request counts per user
- Storage: Persist counter state
- Middleware: Intercept requests and enforce limits

Invariants:
- Counter never negative
- Counter resets at time boundary
- Max requests per window enforced

Dependencies:
RateLimiter → Storage (interface)
Middleware → RateLimiter

[Full 9-layer architecture...]

**Code:** [Implementation]

**Tests:** [Comprehensive test suite]

**Negative Doubt Log:**
- Failure mode: Race condition → Added atomic increment
- Failure mode: Time drift → Used monotonic clock
...
```

## Principle Categories

### 1. Readability & Clarity
**Goal:** Code that reads like natural language

- Descriptive naming (nouns for data, verbs for actions)
- Consistent formatting and style
- Self-documenting code (minimal comments)
- Small, focused functions (< 20 lines ideal)

**Key Quote:** "Code is read 10x more than it's written"

### 2. Simplicity & Efficiency
**Goal:** Minimal viable abstraction

- KISS: Simplest solution that works
- DRY: No duplicated logic
- YAGNI: Build only what's needed now
- Defer optimization until profiling proves need

**Key Quote:** "Premature optimization is the root of all evil"

### 3. Design & Architecture
**Goal:** Modular, flexible, testable systems

- Single Responsibility Principle
- Composition over Inheritance
- Depend on interfaces, not implementations
- 7 Essential Patterns:
  - Factory, Strategy, Observer
  - Decorator, Adapter, Command, Singleton

**Key Quote:** "Architecture enables change velocity"

### 4. Testing & Quality
**Goal:** Behavior locked by tests

- Write tests first or alongside code
- Test pyramid: Many unit, fewer integration, minimal e2e
- One assertion per test (focused)
- Mock external dependencies

**Key Quote:** "No refactor without tests"

### 5. Error Handling
**Goal:** Fail fast and clearly

- Validate inputs at entry points
- Use specific exception types
- Provide actionable error messages
- Guard clauses to reduce nesting

**Key Quote:** "Explicit is better than implicit"

### 6. Maintainability
**Goal:** Code that's easy to change

- Boy Scout Rule: Leave it better
- Continuous small refactors
- Atomic commits with clear messages
- Automate quality checks (linting, formatting)

**Key Quote:** "Technical debt compounds like financial debt"

## Process Mode Workflow

### Step 0: Environment Gate ⚠️
**ALWAYS FIRST**

Verify:
- Language version
- Package manager  
- Dependencies
- Development tools

### Step 1: Task Classification
Classify as ONE of:
- New Feature
- Refactor (behavior preserved)
- Bug Fix
- Review/Audit
- Documentation

**If unclear → STOP**

### Step 2: Load Engineering Constraints
Apply principles as hard rules:
- Single responsibility
- No circular dependencies
- Tests before refactoring
- No speculative features
- Patterns need stated forces

### Step 3: Architecture-First Reasoning
Think in 9 layers (never skip):

1. Responsibilities
2. Invariants  
3. Dependencies
4. Module boundaries
5. Public APIs
6. Folder structure
7. Files
8. Functions
9. Syntax

### Step 4: Behavior & Invariants
Document:
- Observable behavior
- Input/output contracts
- State invariants
- Ordering requirements

### Step 5: Pattern Gate
Use pattern ONLY if:
- Force is stated
- Simpler alternative rejected
- Invariant being protected is clear

### Step 6: Implementation
Generate code following:
- Explicit boundaries
- Minimal public surface
- No utils/common without ownership
- Flat structures over deep nesting

### Step 7: Test-Driven
Include:
- Unit tests for logic
- Integration tests for dependencies
- Edge case coverage
- Error path tests

### Step 8: Negative Doubt Routine
Adversarial verification:

1. List 5 failure modes
2. Falsify assumptions
3. Check invariant enforcement
4. Audit dependencies
5. Try simpler alternative
6. Inject failure tests
7. Revise design
8. Document findings
9. Hard stop if unsafe

### Step 9: Assumptions Disclosure
Always state:
- Input assumptions
- State invariants  
- Ordering guarantees
- Non-goals

## Mode Detection

### Quick Reference Triggers
- "What pattern for...?"
- "How should I...?"
- "Best practice..."
- Pattern/principle names
- Short, focused questions

### Process Mode Triggers
- "Build [system]"
- "Design [architecture]"
- "Production code for..."
- Keywords: critical, secure, complex
- Multi-component systems

## Quick Decision Tables

### When to Use Design Patterns?

| Need | Pattern | Alternative |
|------|---------|-------------|
| Swap implementations | Strategy | If/else (for 2-3 variants) |
| Complex object creation | Factory | Direct constructor (simple objects) |
| Event notification | Observer | Direct calls (1-2 listeners) |
| Add capabilities | Decorator | Subclassing (stable hierarchy) |
| Interface mismatch | Adapter | Refactor interfaces |
| Undo/logging | Command | Direct methods (no history needed) |
| Single instance | Singleton | Dependency injection |

### When to Refactor vs Rewrite?

| Tests Exist? | Code Quality | Action |
|--------------|--------------|--------|
| ✓ Yes | Poor structure | Incremental refactor |
| ✗ No | Poor structure | Write tests → refactor |
| ✗ No | Fundamentally wrong | Rewrite with TDD |
| ✓ Yes | Security flaw | Fix → add regression test |

### When to Add Abstraction?

| Condition | Add? | Reason |
|-----------|------|--------|
| Duplicated in 3+ places | Yes | DRY principle |
| Future variation anticipated | No | YAGNI - wait for actual need |
| 2+ implementations exist | Yes | Interface for polymorphism |
| 1 implementation, simple | No | KISS - keep it simple |

## Anti-Patterns Caught by This Skill

### Common AI Code Generation Issues
- ❌ Generic variable names (`data`, `temp`, `result`)
- ❌ Over-commenting obvious code
- ❌ Skipping input validation
- ❌ Applying patterns without justification
- ❌ Monolithic functions (100+ lines)
- ❌ Copy-pasted code with minor changes
- ❌ Missing error handling

### Engineering Anti-Patterns
- ❌ Coding before defining architecture
- ❌ Refactoring without tests
- ❌ Circular dependencies
- ❌ God objects (do everything)
- ❌ Premature optimization
- ❌ Unclear module boundaries
- ❌ Vague variable names

## Example Usage

### Quick Mode: Pattern Question
```bash
kiro "When should I use the Observer pattern instead of direct callbacks?"

# Response includes:
# - Forces that justify Observer
# - When callbacks are simpler
# - Code example of both
# - Trade-offs
```

### Process Mode: Build Feature
```bash
kiro "Build authentication service with JWT tokens for production API"

# Response includes:
# - Task classification (New Feature)
# - Architecture (9 layers)
# - Dependencies (interfaces)
# - Public API contracts
# - Full implementation
# - Comprehensive tests
# - Negative doubt log
# - Security considerations
```

## Verification Gates

| Gate | Checks | Hard Stop If |
|------|--------|--------------|
| 0. Environment | Runtime, tools, deps | Missing required tools |
| 1. Requirements | Clarity, scope | Ambiguous or vague |
| 2. Architecture | Dependencies, boundaries | Circular deps |
| 3. Patterns | Justified forces | No force stated |
| 4. Tests | Coverage, edge cases | Critical paths untested |
| 5. Quality | Linting, formatting | Violations present |
| 6. Security | Validation, secrets | Vulnerabilities found |
| 7. Performance | Benchmarks (if critical) | Requirements not met |

## Benefits

### For Individual Developers
- Faster pattern selection
- Fewer bugs through verification
- Better architecture decisions
- Clearer code review criteria

### For Teams
- Consistent engineering practices
- Shared vocabulary (patterns)
- Reduced technical debt
- Faster onboarding

### For Production Systems
- Higher reliability (gates catch issues)
- Better maintainability (clear structure)
- Easier debugging (explicit invariants)
- Safer refactoring (tests lock behavior)

## When NOT to Use Full Process Mode

**Use lightweight reference mode for:**
- Prototypes and experiments
- Personal scripts
- Learning exercises
- Throwaway code

**But always state:** "This is a prototype, skipping gates X, Y, Z"

## Sources & Credits

### Design Patterns & Principles
- *Clean Code* - Robert C. Martin
- *The Pragmatic Programmer* - Hunt & Thomas
- *Code Complete* - Steve McConnell
- *Refactoring* - Martin Fowler
- *Design Patterns* - Gang of Four

### Engineering Process
- Senior SDE-3 industry practices
- Production systems methodology
- Safety-critical software engineering

## Philosophy

> **You are not an autocomplete engine.**  
> **You are an engineering constraint solver.**

This skill treats engineering as a discipline of **preserving correctness** through:
- Explicit constraints
- Verifiable invariants
- Systematic reasoning
- Adversarial verification

Code is the output, not the input, of engineering.

## Version

2.0.0 - Combined design patterns + ProCoder engineering process

## License

Based on publicly available software engineering literature and industry best practices.
