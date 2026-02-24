# Go Design Patterns Skill

A Kiro skill for applying design patterns idiomatically in Go, respecting composition over inheritance and Go's minimalist philosophy.

## Structure

```
golang-design-patterns/
├── SKILL.md                          # Main skill definition (load this)
├── references/
│   ├── full-patterns-guide.md        # Comprehensive pattern catalog
│   └── anti-patterns.md              # What NOT to do
├── scripts/
│   └── detect-antipatterns.sh        # Scan code for common issues
└── README.md                          # This file
```

## Usage

### As a Kiro Skill

This skill activates when you:
- Mention "Go design patterns"
- Ask about translating OOP patterns to Go
- Request architectural guidance for Go services
- Need to review Go code for pattern usage

### Manual Reference

Read `SKILL.md` for quick guidance on:
- When to use each pattern category
- Go-idiomatic implementations
- Quick anti-pattern checklist

Consult `references/` for:
- **full-patterns-guide.md**: Detailed explanations with examples
- **anti-patterns.md**: Common mistakes and corrections

### Anti-Pattern Detection

Run the provided script to scan your codebase:

```bash
# Scan current directory
./scripts/detect-antipatterns.sh

# Scan specific directory
./scripts/detect-antipatterns.sh /path/to/project
```

The script detects:
- Global mutable state
- init() function usage
- Ignored errors (`_ = err`)
- panic() in non-init code
- Goroutines without context
- Large interfaces (>5 methods)

## Key Principles

1. **No Inheritance**: Go doesn't have class hierarchies. Use composition.
2. **Implicit Interfaces**: Types automatically satisfy interfaces.
3. **Small Interfaces**: Prefer 1-3 methods per interface.
4. **Consumer-Side Interfaces**: Define interfaces where used, not implemented.
5. **Explicit Dependencies**: Inject dependencies, avoid globals.
6. **Context Everywhere**: Pass `context.Context` for cancellation.
7. **Return Errors**: Don't use `panic` for business logic.

## Pattern Categories

### Creational
- Constructor Pattern (`New()` functions)
- Functional Options (flexible configuration)
- Factory Functions (conditional creation)

### Structural
- Adapter (interface wrapping)
- Decorator (middleware, io wrappers)
- Composite (recursive structures)

### Behavioral
- Strategy (interchangeable algorithms)
- Observer (channels, callbacks)
- Command (job queues)

### Concurrency
- Worker Pool (bounded goroutines)
- Pipeline (staged processing)
- Fan-Out/Fan-In (parallel processing)

### Error Handling
- Sentinel Errors (predefined constants)
- Error Wrapping (`%w` format)
- Custom Error Types (structured data)

### Testing
- Table-Driven Tests (data-driven)
- Interface Mocking (hand-written mocks)
- Testable Constructors (accept interfaces)

## Integration

This skill complements:
- **golang.md**: Core language standards
- **Clean Architecture**: Domain-driven design in Go
- **Standard Library**: Following stdlib patterns

## Version

1.0.0 - Initial release

## License

Public domain / CC0

## Contributing

To extend this skill:
1. Add new patterns to `references/full-patterns-guide.md`
2. Update `SKILL.md` summary
3. Add detection rules to `scripts/detect-antipatterns.sh`
4. Keep examples simple and idiomatic
