# Golang Skill for Kiro

This is a comprehensive Golang engineering standards skill package for Kiro agents.

## Structure

```
golang/
├── SKILL.md              # Main skill definition (Kiro format)
├── README.md             # This file
└── references/           # Detailed documentation
    ├── language/
    ├── architecture/
    ├── concurrency/
    ├── api-server/
    ├── database/
    ├── configuration/
    ├── logging/
    ├── security/
    ├── testing/
    └── error-handling/
```

## Usage

Place this directory in your Kiro skills folder:
- **Workspace**: `.kiro/skills/golang/`
- **Global**: `~/.kiro/skills/golang/`

The skill will automatically activate when you:
- Write or review Go code
- Ask about Go best practices
- Request architecture guidance
- Need help with concurrency, testing, or security

## Coverage

This skill covers all aspects of production Go development:

1. **Language Fundamentals** - Idioms, naming, patterns
2. **Architecture** - Clean architecture, project layout, DI
3. **Error Handling** - Wrapping, sentinel errors, custom types
4. **Concurrency** - Goroutines, channels, context, patterns
5. **API Development** - HTTP servers, middleware, graceful shutdown
6. **Database** - Repository pattern, connection pooling, transactions
7. **Configuration** - Env vars, typed config, secret management
8. **Logging** - Structured logging, slog patterns
9. **Security** - Validation, crypto, SQL injection prevention
10. **Testing** - Table-driven tests, mocking, integration tests

## Priority Levels

- **P0 (CRITICAL)**: Must follow - violations cause bugs or security issues
- **P1 (STANDARD)**: Should follow - improves maintainability

## Quick Reference

See [SKILL.md](SKILL.md) for the quick reference guide with links to detailed documentation in `/references`.

## Contributing

When adding content:
1. Keep SKILL.md concise (index/overview only)
2. Put detailed content in appropriate `/references` subdirectory
3. Use code examples showing both ✅ good and ❌ bad patterns
4. Include rationale and context for each recommendation

## License

This skill is provided as-is for engineering excellence.
