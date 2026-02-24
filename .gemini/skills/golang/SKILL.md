---
name: golang
description: Comprehensive standards for building production-grade Go applications including architecture, concurrency, security, testing, and best practices. Use when writing, reviewing, or architecting Go code.
metadata:
  version: 1.0.0
  labels: [golang, backend, api, clean-architecture, concurrency, security]
  author: Engineering Standards Team
compatibility: Go 1.21+
---

# Golang Engineering Standards

Comprehensive best practices for building production-grade Go applications. This skill covers everything from language fundamentals to production deployment patterns.

## Quick Reference

### When to Use This Skill

- Writing new Go code or projects
- Reviewing Go pull requests
- Architecting Go backend services
- Implementing APIs, databases, or concurrent systems
- Troubleshooting Go applications
- Setting up testing infrastructure

### Priority Levels

- **P0 (CRITICAL)**: Must follow - violations cause bugs, security issues, or production failures
- **P1 (STANDARD)**: Should follow - improves maintainability and team productivity

## Core Topics

### 1. Language Fundamentals (P0)
Core idioms, naming conventions, and Go-specific patterns.

**Key principles:**
- Always run `gofmt`/`goimports` on save
- Use `camelCase` for unexported, `PascalCase` for exported
- Small interfaces (1-2 methods), defined at consumer
- Constructors use `NewType()` pattern
- Options pattern for complex configuration

📄 **[Full Language Guide](references/language/fundamentals.md)**

### 2. Architecture & Project Structure (P0)
Clean architecture, dependency injection, and standard project layout.

**Key principles:**
- Follow standard Go project layout (`cmd/`, `internal/`, `pkg/`)
- Apply Clean Architecture: Domain → Service → Adapter → Handler
- Dependency Rule: dependencies point inward only
- Define interfaces where they're used (consumer side)
- Wire dependencies in `main()`, not globals

📄 **[Architecture Guide](references/architecture/clean-architecture.md)**  
📄 **[Project Layout](references/architecture/project-layout.md)**

### 3. Error Handling (P0)
Error wrapping, checking, and custom error types.

**Key principles:**
- Always wrap errors with context: `fmt.Errorf("context: %w", err)`
- Handle once: Log OR Return, never both
- Use `errors.Is()` for sentinel errors
- Use `errors.As()` for error types
- Only panic for unrecoverable startup errors

📄 **[Error Handling Guide](references/error-handling/patterns.md)**

### 4. Concurrency (P0)
Goroutines, channels, context, and concurrency patterns.

**Key principles:**
- Share memory by communicating (use channels)
- Always pass `context.Context` as first parameter
- Never start a goroutine without knowing how it stops
- Run tests with `go test -race`
- Use `errgroup` over `WaitGroup` when errors matter

📄 **[Concurrency Patterns](references/concurrency/patterns.md)**  
📄 **[Context Usage](references/concurrency/context.md)**

### 5. API Server Development (P0)
HTTP servers, middleware, graceful shutdown.

**Key principles:**
- **MUST** implement graceful shutdown
- Use Echo or Gin for production APIs
- Keep handlers thin - parse, call service, respond
- Middleware for cross-cutting concerns
- Always include `/health` and `/ready` endpoints

📄 **[API Server Guide](references/api-server/patterns.md)**  
📄 **[Graceful Shutdown](references/api-server/graceful-shutdown.md)**

### 6. Database Interaction (P0)
Repository pattern, connection pooling, transactions.

**Key principles:**
- Use repository pattern with interfaces
- Prefer `pgx/v5` for PostgreSQL
- Always configure connection pools
- Use transactions for ACID requirements
- Always use `QueryContext`/`ExecContext` with context

📄 **[Database Guide](references/database/repository-pattern.md)**  
📄 **[Connection Pooling](references/database/connection-pooling.md)**

### 7. Configuration Management (P1)
Environment variables, typed config, secret management.

**Key principles:**
- Store config in environment variables (12-factor)
- Load into typed struct, validate on startup
- Never commit secrets to git
- Use Viper or Koanf for complex configs

📄 **[Configuration Guide](references/configuration/patterns.md)**

### 8. Logging & Observability (P1)
Structured logging with slog, contextual logging.

**Key principles:**
- Use structured logging (JSON in production)
- Include trace IDs in logs
- Use `log/slog` (Go 1.21+)
- Never use `log.Fatal()` in libraries

📄 **[Logging Guide](references/logging/slog.md)**

### 9. Security (P0)
Input validation, cryptography, SQL injection prevention.

**Key principles:**
- **ALWAYS** use `crypto/rand`, never `math/rand` for security
- Use parameterized queries (never string concatenation)
- Use `bcrypt` or `argon2` for password hashing
- Validate JWT claims: `alg`, `iss`, `aud`, `exp`

📄 **[Security Guide](references/security/best-practices.md)**  
📄 **[Crypto Patterns](references/security/cryptography.md)**

### 10. Testing (P0)
Table-driven tests, mocking, integration testing.

**Key principles:**
- Use table-driven test pattern
- Mock dependencies via interfaces
- Define interfaces at consumer (makes mocking easier)
- Run `go test -race` before deployment
- Aim for >80% coverage on critical paths

📄 **[Testing Guide](references/testing/patterns.md)**

## Common Anti-Patterns to Avoid

❌ **Global mutable state** → Use dependency injection  
❌ **Ignoring errors** (`_` assignment) → Always handle  
❌ **Business logic in handlers** → Keep handlers thin  
❌ **String concatenation for SQL** → Use parameterized queries  
❌ **`math/rand` for security** → Use `crypto/rand`  
❌ **Leaking goroutines** → Always know how they stop  
❌ **Missing context** → Pass `context.Context` everywhere  
❌ **Not closing rows** → Always `defer rows.Close()`  
❌ **Log AND Return errors** → Choose one  
❌ **Sleeping in tests** → Use channels/timeouts  

## Quick Start Checklist

Starting a new Go project? Ensure:

- ✅ **Structure**: Follow standard layout (`cmd/`, `internal/`, `pkg/`)
- ✅ **Dependencies**: Use Go modules (`go mod init`)
- ✅ **Formatting**: Set up `gofmt`/`goimports` on save
- ✅ **Linting**: Configure `golangci-lint`
- ✅ **Config**: Load from env vars with validation
- ✅ **Logging**: Set up structured logging with `slog`
- ✅ **Database**: Implement repository pattern with interfaces
- ✅ **API**: Add graceful shutdown and health endpoints
- ✅ **Testing**: Write table-driven tests with mocks
- ✅ **Security**: Use `crypto/rand`, parameterized queries, bcrypt

## Getting Help

Each reference guide contains:
- Detailed explanations of principles
- Complete code examples (good and bad)
- Common pitfalls and how to avoid them
- Production-ready patterns

Start with the topic most relevant to your current task, or read through sequentially for comprehensive understanding.

---

**Last Updated**: 2024  
**Maintainer**: Engineering Standards Team
