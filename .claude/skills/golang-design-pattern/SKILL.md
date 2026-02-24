---
name: golang-design-pattern
description: Design patterns adapted for Go's philosophy. Use when writing Go code, reviewing Go architecture, translating OOP patterns to idiomatic Go, or applying design patterns in a non-OOP language.
triggers:
  - "Go design pattern"
  - "Go architecture"
  - "idiomatic Go"
  - "OOP to Go"
  - "Go interface"
  - "Go concurrency pattern"
  - "Go struct pattern"
  - "Go anti-pattern"
activation:
  mode: fuzzy
  priority: normal
  triggers:
    - "Go design pattern"
    - "Go architecture"
    - "idiomatic Go"
    - "OOP to Go"
    - "Go interface"
    - "Go concurrency pattern"
    - "Go struct pattern"
    - "Go anti-pattern"
compatibility: "Go 1.18+"
metadata:
  version: "1.0.0"
references:
  - references/patterns/anti-patterns.md
  - references/patterns/full-patterns-guide.md
  - references/examples/creational-patterns.md
  - references/examples/structural-behavioral-patterns.md
  - references/examples/concurrency-error-testing.md
  - references/examples/anti-patterns.md
---

# Go Design Patterns & Principles

Apply design patterns idiomatically in Go by respecting composition over inheritance, implicit interfaces, and simplicity over abstraction.

## When to Use This Skill

- Writing or reviewing Go code that needs structural patterns
- Translating OOP design patterns to Go
- Architecting Go services with clean patterns
- Avoiding common anti-patterns from OOP backgrounds

---

## Core Philosophy

Go rejects traditional OOP in favor of:

1. **Composition over Inheritance** — No class hierarchies. Use embedding and interfaces.
2. **Implicit Interfaces** — Types satisfy interfaces automatically. No `implements` keyword.
3. **Small Interfaces** — Prefer single-method interfaces (`io.Reader`, `http.Handler`, `error`).
4. **Explicit Dependencies** — Dependency injection over globals. No magic.
5. **Concurrency via Communication** — Use channels, not shared memory locks.

---

## Pattern Quick Reference

### Creational
| Pattern | When to Use | Reference |
|---------|-------------|-----------|
| Constructor `New()` | Any struct needing validation | `references/examples/creational-patterns.md` |
| Functional Options | 5+ optional config params | `references/examples/creational-patterns.md` |
| Factory Function | Conditional object creation | `references/examples/creational-patterns.md` |
| Avoid Singleton | Use dependency injection | `references/examples/creational-patterns.md` |

### Structural
| Pattern | When to Use | Reference |
|---------|-------------|-----------|
| Adapter | Wrap external/legacy types | `references/examples/structural-behavioral-patterns.md` |
| Decorator (Middleware) | Add behavior without changing type | `references/examples/structural-behavioral-patterns.md` |
| Composition/Embedding | Promote methods, NOT inheritance | `references/examples/structural-behavioral-patterns.md` |
| Consumer-Side Interface | Define interface where consumed | `references/examples/structural-behavioral-patterns.md` |

### Behavioral
| Pattern | When to Use | Reference |
|---------|-------------|-----------|
| Strategy | Interchangeable algorithms | `references/examples/structural-behavioral-patterns.md` |
| Observer | Decouple event producers/consumers | `references/examples/structural-behavioral-patterns.md` |
| Command | Job queues, undo, task pipelines | `references/examples/structural-behavioral-patterns.md` |

### Concurrency
| Pattern | When to Use | Reference |
|---------|-------------|-----------|
| Worker Pool | Bounded parallelism | `references/examples/concurrency-error-testing.md` |
| Pipeline | Stage-by-stage stream processing | `references/examples/concurrency-error-testing.md` |
| Fan-Out/Fan-In | Parallel work + result collection | `references/examples/concurrency-error-testing.md` |

---

## Go Idioms vs OOP

| Traditional OOP | Go Idiom |
|-----------------|----------|
| Inheritance | Composition via embedding |
| Abstract classes | Interfaces with multiple implementations |
| Factory classes | Constructor functions (`NewX()`) |
| Singletons | Dependency injection + `sync.Once` (avoid) |
| Template method | Function/interface injection |
| Observer | Channels or callback functions |
| Decorator | Middleware functions |
| Strategy | Interfaces or function types |

---

## Best Practices

**DO:**
- Use small, focused interfaces (1–3 methods max)
- Define interfaces at consumer side (where used)
- Accept interfaces, return concrete structs
- Use table-driven tests for all test cases
- Pass `context.Context` for cancellation
- Wrap errors with `fmt.Errorf("...: %w", err)`
- Close channels to signal completion
- Use `defer` for cleanup

**DON'T:**
- Create class hierarchies with embedding
- Use `init()` for dependency setup
- Create global mutable state
- Ignore errors with `_` blank identifier
- Use `panic` for business logic errors
- Create interfaces before having 2+ implementations
- Start goroutines without cancellation mechanism

---

## Critical Anti-Patterns

See `references/examples/anti-patterns.md` for code examples of:
- OOP inheritance simulation
- Global state
- Ignored errors
- Goroutine leaks
- Premature abstraction
