---
name: Golang
description: Comprehensive standards and best practices for building production-grade Go applications
metadata:
  labels: [golang, backend, api, clean-architecture, concurrency, security]
  version: 1.0.0
  triggers:
    files: ['**/*.go', 'go.mod', 'go.sum']
    keywords: [golang, go code, backend, api, database, testing]
---

# Golang Engineering Standards

This document consolidates best practices for building production-grade Go applications across language fundamentals, architecture, concurrency, security, testing, and more.

---

## Table of Contents

1. [Language Fundamentals](#1-language-fundamentals)
2. [Architecture & Project Structure](#2-architecture--project-structure)
3. [Error Handling](#3-error-handling)
4. [Concurrency](#4-concurrency)
5. [API Server Development](#5-api-server-development)
6. [Database Interaction](#6-database-interaction)
7. [Configuration Management](#7-configuration-management)
8. [Logging & Observability](#8-logging--observability)
9. [Security](#9-security)
10. [Testing](#10-testing)

---

## 1. Language Fundamentals

**Priority: P0 (CRITICAL)**

### Core Principles

- **Fmt**: Run `gofmt` or `goimports` on save. No arguments about formatting.
- **Naming Conventions**:
  - Use `camelCase` for unexported, `PascalCase` for exported
  - Packages: Short, lowercase, singular, no underscores (e.g., `net/http` not `net_http`)
  - Getters: `Owner()`, not `GetOwner()`
  - Setters: `SetOwner()`
  - Interfaces: One method → `Reader`, `Writer`, `Listener`
- **Variables**: Short names for small scope (`i`, `ctx`), descriptive for large scope
- **Slices**: Prefer slices over arrays. Use `make()` with capacity when size is known
- **Constants**: Use `iota` for enumerations

### Commentary Standards

- Comments immediately precede the declaration
- `// Package foo implements...` for package documentation
- **Exported names MUST have comments**

### Control Structures

- No parentheses: `if x > 0 {`
- Initialization in if: `if err := file.Chmod(0664); err != nil {`
- Switch handles multiple cases: `case ' ', '?', '&':`

### Allocation

- `new(T)`: Allocates zeroed storage for `T`, returns `*T`
- `make(T, args)`: Creates slices, maps, channels. Returns initialized `T` (not `*T`)

### Idiomatic Patterns

#### Constructors

Use `New` or `New<Type>` pattern:

```go
func NewClient(cfg Config) (*Client, error) {
    if cfg.Timeout == 0 {
        return nil, errors.New("timeout required")
    }
    return &Client{cfg: cfg}, nil
}
```

#### Options Pattern

For complex configuration:

```go
type Option func(*Server)

func WithPort(port int) Option {
    return func(s *Server) { s.port = port }
}

func WithTimeout(timeout time.Duration) Option {
    return func(s *Server) { s.timeout = timeout }
}

func NewServer(opts ...Option) *Server {
    s := &Server{
        port:    8080,
        timeout: 30 * time.Second,
    }
    for _, opt := range opts {
        opt(s)
    }
    return s
}

// Usage
srv := NewServer(
    WithPort(3000),
    WithTimeout(60 * time.Second),
)
```

#### Interface Compile-Time Checks

Verify interface implementation at compile time:

```go
var _ http.Handler = (*MyHandler)(nil)
var _ io.ReadWriter = (*MyReadWriter)(nil)
```

#### Embedding

Use embedding for composition, not inheritance:

```go
type ReaderWriter interface {
    Reader
    Writer
}
```

### Anti-Patterns to Avoid

- ❌ **No `init()`**: Use explicit constructors instead
- ❌ **No Globals**: Use dependency injection, not global mutable state
- ❌ **No `panic`**: Return errors, don't panic (except for unrecoverable startup errors)
- ❌ **No `_` ignored errors**: Always check and handle errors
- ❌ **No stuttering**: `log.Error`, not `log.LogError`

---

## 2. Architecture & Project Structure

**Priority: P0 (CRITICAL)**

### Architectural Principles

- **Clean Architecture**: Separate concerns. Inner layers (Domain) depend on nothing. Outer layers (Adapters) depend on Inner.
- **Dependency Rule**: Dependencies point **inward only**. Inner circles know nothing about outer circles.
- **Dependency Injection**: Explicitly pass dependencies via constructors. Avoid global singletons.
- **Package Oriented Design**: Organize by feature/domain, not by layer
- **Interface Segregation**: Define interfaces where they are **used** (consumer side), not where implemented

### Standard Project Layout

```text
/
├── cmd/
│   └── app/
│       └── main.go              # Entry point. Wire dependencies. Start server.
├── internal/
│   ├── domain/                  # Enterprise business rules (Entities)
│   │   ├── user.go              # Pure Go structs, core business logic
│   │   └── errors.go            # Domain-specific errors
│   ├── port/                    # Interfaces (Inputs and Outputs)
│   │   ├── repository.go        # Repository interfaces
│   │   └── service.go           # Use case interfaces
│   ├── service/                 # Application business rules (Use Cases)
│   │   └── user_service.go      # Orchestrates domain + ports
│   └── adapter/                 # Interface Adapters
│       ├── handler/             # Controllers, Presenters
│       │   └── http/
│       │       └── user_handler.go
│       └── repository/          # Database implementations
│           └── postgres/
│               └── user_repo.go
├── pkg/                         # Public libraries (reusable utils)
│   └── logger/
├── configs/                     # Configuration files
├── api/                         # OpenAPI/Protobuf definitions
├── scripts/                     # Build, deployment scripts
├── migrations/                  # Database migrations
├── go.mod
├── go.sum
└── Makefile
```

### Clean Architecture Layers

#### 1. Domain (Entities)

- **Location**: `internal/domain/`
- **Content**: Pure Go structs. Core business logic.
- **Dependencies**: None. Stdlib only.

```go
// internal/domain/user.go
package domain

import "errors"

var (
    ErrUserNotFound    = errors.New("user not found")
    ErrInvalidEmail    = errors.New("invalid email format")
)

type User struct {
    ID    string
    Email string
    Name  string
}

// Business logic lives here
func (u *User) ChangeEmail(email string) error {
    if !isValidEmail(email) {
        return ErrInvalidEmail
    }
    u.Email = email
    return nil
}
```

#### 2. Port (Interfaces)

- **Location**: `internal/port/`
- **Content**: Abstract interfaces for repositories, external services
- **Dependencies**: Domain only

```go
// internal/port/repository.go
package port

import (
    "context"
    "myapp/internal/domain"
)

type UserRepository interface {
    GetByID(ctx context.Context, id string) (*domain.User, error)
    Create(ctx context.Context, user *domain.User) error
    Update(ctx context.Context, user *domain.User) error
}
```

#### 3. Service (Use Cases)

- **Location**: `internal/service/`
- **Content**: Application-specific business rules. Orchestrates domain objects.
- **Dependencies**: Domain, Port interfaces

```go
// internal/service/user_service.go
package service

import (
    "context"
    "myapp/internal/domain"
    "myapp/internal/port"
)

type UserService struct {
    repo port.UserRepository
}

func NewUserService(repo port.UserRepository) *UserService {
    return &UserService{repo: repo}
}

func (s *UserService) Register(ctx context.Context, email, name string) (*domain.User, error) {
    user := &domain.User{
        ID:    generateID(),
        Email: email,
        Name:  name,
    }
    
    if err := user.ChangeEmail(email); err != nil {
        return nil, err
    }
    
    if err := s.repo.Create(ctx, user); err != nil {
        return nil, err
    }
    
    return user, nil
}
```

#### 4. Adapter (Interface Adapters)

- **Location**: `internal/adapter/`
- **Content**: Converts data formats between use cases and external systems
- **Sub-layers**:
  - **Handlers**: HTTP/gRPC controllers (`adapter/handler/http`)
  - **Repositories**: Database gateways (`adapter/repository/postgres`)

```go
// internal/adapter/handler/http/user_handler.go
package http

import (
    "net/http"
    "myapp/internal/service"
    "github.com/labstack/echo/v4"
)

type UserHandler struct {
    userService *service.UserService
}

func NewUserHandler(userService *service.UserService) *UserHandler {
    return &UserHandler{userService: userService}
}

func (h *UserHandler) Register(c echo.Context) error {
    var req RegisterRequest
    if err := c.Bind(&req); err != nil {
        return c.JSON(http.StatusBadRequest, ErrorResponse{Message: "invalid request"})
    }
    
    user, err := h.userService.Register(c.Request().Context(), req.Email, req.Name)
    if err != nil {
        return c.JSON(http.StatusInternalServerError, ErrorResponse{Message: err.Error()})
    }
    
    return c.JSON(http.StatusCreated, toUserResponse(user))
}
```

#### 5. Main (Entry Point)

- **Location**: `cmd/app/`
- **Content**: Wires all dependencies together

```go
// cmd/app/main.go
package main

import (
    "database/sql"
    "log"
    "myapp/internal/adapter/handler/http"
    "myapp/internal/adapter/repository/postgres"
    "myapp/internal/service"
    _ "github.com/lib/pq"
)

func main() {
    // Initialize DB
    db, err := sql.Open("postgres", "...")
    if err != nil {
        log.Fatal(err)
    }
    defer db.Close()
    
    // Build dependency graph (Dependency Injection)
    userRepo := postgres.NewUserRepository(db)
    userService := service.NewUserService(userRepo)
    userHandler := http.NewUserHandler(userService)
    
    // Start server
    router := setupRouter(userHandler)
    log.Fatal(router.Start(":8080"))
}
```

---

## 3. Error Handling

**Priority: P0 (CRITICAL)**

### Core Principles

- **Errors are Values**: Handle them like any other value
- **Handle Once**: Log OR Return. Never Log AND Return (creates duplicate logs)
- **Add Context**: Don't just bubble up `err`. Wrap it: `fmt.Errorf("failed to open file: %w", err)`
- **Use Standard Lib**: Go 1.13+ `errors` package is sufficient

### Error Wrapping

Always add context when wrapping errors:

```go
func ReadConfig(path string) (*Config, error) {
    file, err := os.Open(path)
    if err != nil {
        return nil, fmt.Errorf("failed to open config at %s: %w", path, err)
    }
    defer file.Close()
    
    var cfg Config
    if err := json.NewDecoder(file).Decode(&cfg); err != nil {
        return nil, fmt.Errorf("failed to parse config: %w", err)
    }
    
    return &cfg, nil
}
```

### Checking Errors

#### Sentinel Errors with `errors.Is`

```go
var (
    ErrNotFound    = errors.New("not found")
    ErrUnauthorized = errors.New("unauthorized")
)

func GetUser(id string) (*User, error) {
    // ... fetch logic
    if notFound {
        return nil, ErrNotFound
    }
    return user, nil
}

// Caller
user, err := GetUser("123")
if errors.Is(err, ErrNotFound) {
    // Handle missing user
}
```

#### Type Assertions with `errors.As`

```go
var pathErr *fs.PathError
if errors.As(err, &pathErr) {
    fmt.Printf("failed at path: %s\n", pathErr.Path)
}

var valErr *ValidationError
if errors.As(err, &valErr) {
    fmt.Printf("validation failed on field: %s\n", valErr.Field)
}
```

### Custom Error Types

```go
type ValidationError struct {
    Field string
    Msg   string
}

func (e *ValidationError) Error() string {
    return fmt.Sprintf("validation error on %s: %s", e.Field, e.Msg)
}

// Usage
func ValidateUser(u *User) error {
    if u.Email == "" {
        return &ValidationError{Field: "email", Msg: "required"}
    }
    if !isValidEmail(u.Email) {
        return &ValidationError{Field: "email", Msg: "invalid format"}
    }
    return nil
}
```

### Anti-Patterns

- ❌ **Check only not nil without context**: `if err != nil { return err }` loses stack/context
- ❌ **String checking**: `err.Error() == "foo"` is brittle
- ❌ **Swallowing errors**: `_ = func()` is dangerous
- ❌ **Panic for recoverable errors**: Only panic for unrecoverable startup errors

---

## 4. Concurrency

**Priority: P0 (CRITICAL)**

### Core Principles

- **Share Memory by Communicating**: Don't communicate by sharing memory. Use channels.
- **Context is King**: Always pass `ctx` to manage cancellation/timeouts
- **Prevent Leaks**: Never start a goroutine without knowing how it will stop
- **Race Detection**: Always run tests with `go test -race`

### Primitives

- **Goroutines**: Lightweight threads - `go func() { ... }()`
- **Channels**: For data passing + synchronization
- **sync.WaitGroup**: Wait for a group of goroutines to finish
- **errgroup.Group**: WaitGroup + Error propagation (Preferred)
- **sync.Mutex**: Protect shared state (simpler than channels for just state)

### Context Usage

**Golden Rule**: `func Foo(ctx context.Context, args ...)` - Context is always the **first parameter**.

#### Timeout/Deadline

```go
func slowOperation(ctx context.Context) error {
    ctx, cancel := context.WithTimeout(ctx, 100*time.Millisecond)
    defer cancel()
    
    select {
    case <-time.After(1 * time.Second):
        return errors.New("operation took too long")
    case <-ctx.Done():
        return ctx.Err() // "context deadline exceeded"
    }
}
```

#### Cancellation

Propagate cancel signal down the call graph:

```go
func main() {
    ctx, cancel := context.WithCancel(context.Background())
    defer cancel()
    
    go func() {
        if err := worker(ctx); err != nil {
            log.Println("worker failed:", err)
            cancel() // Cancel all other workers
        }
    }()
    
    // Wait for interrupt
    quit := make(chan os.Signal, 1)
    signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
    
    select {
    case <-quit:
        cancel()
    case <-ctx.Done():
    }
}
```

### Concurrency Patterns

#### Worker Pool

Process jobs concurrently with limited workers:

```go
func worker(id int, jobs <-chan Job, results chan<- Result) {
    for job := range jobs {
        results <- processJob(job)
    }
}

func main() {
    const numWorkers = 5
    jobs := make(chan Job, 100)
    results := make(chan Result, 100)
    
    // Start workers
    for w := 1; w <= numWorkers; w++ {
        go worker(w, jobs, results)
    }
    
    // Send jobs
    for _, job := range getJobs() {
        jobs <- job
    }
    close(jobs)
    
    // Collect results
    for i := 0; i < len(getJobs()); i++ {
        result := <-results
        handleResult(result)
    }
}
```

#### Pipeline Pattern

Chain processing stages:

```go
func gen(nums ...int) <-chan int {
    out := make(chan int)
    go func() {
        defer close(out)
        for _, n := range nums {
            out <- n
        }
    }()
    return out
}

func sq(in <-chan int) <-chan int {
    out := make(chan int)
    go func() {
        defer close(out)
        for n := range in {
            out <- n * n
        }
    }()
    return out
}

// Usage
nums := gen(2, 3, 4)
squares := sq(nums)
for sq := range squares {
    fmt.Println(sq)
}
```

#### Using errgroup

Preferred over WaitGroup when you need error handling:

```go
import "golang.org/x/sync/errgroup"

func fetchAll(ctx context.Context, urls []string) error {
    g, ctx := errgroup.WithContext(ctx)
    
    for _, url := range urls {
        url := url // Capture for goroutine
        g.Go(func() error {
            return fetch(ctx, url)
        })
    }
    
    // Wait for all goroutines and return first error
    return g.Wait()
}
```

### Channel Guidelines

- **Buffered vs Unbuffered**: 
  - Unbuffered: Strict synchronization, sender blocks until receiver reads
  - Buffered: Use only for async decoupling/burst handling
- **Closed Channels**: 
  - Writing to closed channel → panic
  - Reading from closed channel → returns zero-value immediately
- **Select**: Use to handle multiple channels or timeouts

```go
select {
case msg := <-ch1:
    handleMessage(msg)
case <-ch2:
    handleSignal()
case <-time.After(5 * time.Second):
    handleTimeout()
case <-ctx.Done():
    return ctx.Err()
}
```

---

## 5. API Server Development

**Priority: P0 (CRITICAL)**

### Router Selection

- **Standard Lib (`net/http`)**: Use for simple services or zero-dep requirement. Go 1.22+ has improved routing.
- **Echo (`labstack/echo`)**: **Recommended** for production REST APIs. Excellent middleware, binding, error handling.
- **Gin (`gin-gonic/gin`)**: High-performance alternative.

### Core Guidelines

- **Graceful Shutdown**: **MUST** implement to handle in-flight requests on termination
- **DTOs**: Separate Domain structs from API Request/Response structs. Map between them.
- **Middleware**: Use for cross-cutting concerns (Logging, Recovery, CORS, Auth, Tracing)
- **Health Checks**: Always include `/health` and `/ready` endpoints
- **Content-Type**: Enforce `application/json` for REST APIs

### Graceful Shutdown

Ensure no requests are dropped during deployment:

```go
func main() {
    srv := &http.Server{
        Addr:         ":8080",
        Handler:      setupRouter(),
        ReadTimeout:  10 * time.Second,
        WriteTimeout: 10 * time.Second,
    }
    
    // Start server in goroutine
    go func() {
        if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
            log.Fatalf("listen: %s\n", err)
        }
    }()
    
    // Wait for interrupt signal
    quit := make(chan os.Signal, 1)
    signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
    <-quit
    
    log.Println("Shutting down server...")
    
    // Context with timeout for shutdown
    ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
    defer cancel()
    
    if err := srv.Shutdown(ctx); err != nil {
        log.Fatal("Server forced to shutdown:", err)
    }
    
    log.Println("Server exited")
}
```

### Middleware Patterns

#### Standard Library Pattern

```go
func LoggingMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        start := time.Now()
        
        // Serve request
        next.ServeHTTP(w, r)
        
        // Log after completion
        log.Printf("%s %s %v", r.Method, r.URL.Path, time.Since(start))
    })
}

// Chaining
handler := LoggingMiddleware(AuthMiddleware(finalHandler))
```

#### Echo Middleware

```go
func TrackingMiddleware(next echo.HandlerFunc) echo.HandlerFunc {
    return func(c echo.Context) error {
        start := time.Now()
        req := c.Request()
        
        // Logic before handler
        traceID := req.Header.Get("X-Trace-ID")
        if traceID == "" {
            traceID = generateTraceID()
        }
        
        // Execute handler
        err := next(c)
        
        // Logic after handler
        log.Printf("[%s] %s %s %v", traceID, req.Method, req.URL.Path, time.Since(start))
        
        return err
    }
}

// Usage
e := echo.New()
e.Use(TrackingMiddleware)
```

### Handler Structure

Keep handlers thin - only parse, call service, format response:

```go
type UserHandler struct {
    service *service.UserService
}

func (h *UserHandler) CreateUser(c echo.Context) error {
    // 1. Parse request
    var req CreateUserRequest
    if err := c.Bind(&req); err != nil {
        return c.JSON(http.StatusBadRequest, ErrorResponse{
            Message: "invalid request body",
        })
    }
    
    // 2. Validate
    if err := req.Validate(); err != nil {
        return c.JSON(http.StatusBadRequest, ErrorResponse{
            Message: err.Error(),
        })
    }
    
    // 3. Call service
    user, err := h.service.CreateUser(c.Request().Context(), req.Email, req.Name)
    if err != nil {
        return handleError(c, err)
    }
    
    // 4. Format response
    return c.JSON(http.StatusCreated, toUserResponse(user))
}
```

### Anti-Patterns

- ❌ **Business Logic in Handlers**: Handlers should orchestrate, not implement logic
- ❌ **Global Router**: Don't use global router variables. Pass router instance.

---

## 6. Database Interaction

**Priority: P0 (CRITICAL)**

### Core Principles

- **Prefer Raw SQL/Builders over ORMs**: Go structs map well to SQL. ORMs (like GORM) can obscure performance.
- **Recommended**: `sqlc` for type-safe SQL code generation
- **Repository Pattern**: Abstract DB access behind interfaces in `internal/port/`
- **Connection Pooling**: Always configure `SetMaxOpenConns`, `SetMaxIdleConns`, `SetConnMaxLifetime`
- **Transactions**: Logic requiring ACID **MUST** use transactions
- **Context Everywhere**: Pass `context.Context` for timeout/cancellation

### Recommended Drivers

- **PostgreSQL**: `jackc/pgx/v5` (preferred for performance and features)
- **MySQL**: `go-sql-driver/mysql`
- **SQLite**: `modernc.org/sqlite` (pure Go) or `mattn/go-sqlite3`

### Repository Pattern Implementation

#### Define Interface (Port)

```go
// internal/port/repository.go
package port

import (
    "context"
    "myapp/internal/domain"
)

type UserRepository interface {
    GetByID(ctx context.Context, id string) (*domain.User, error)
    GetByEmail(ctx context.Context, email string) (*domain.User, error)
    Create(ctx context.Context, user *domain.User) error
    Update(ctx context.Context, user *domain.User) error
    Delete(ctx context.Context, id string) error
}
```

#### Implement with PostgreSQL

```go
// internal/adapter/repository/postgres/user_repo.go
package postgres

import (
    "context"
    "database/sql"
    "fmt"
    "myapp/internal/domain"
    "myapp/internal/port"
)

type userRepository struct {
    db *sql.DB
}

func NewUserRepository(db *sql.DB) port.UserRepository {
    return &userRepository{db: db}
}

func (r *userRepository) GetByID(ctx context.Context, id string) (*domain.User, error) {
    query := `SELECT id, email, name, created_at FROM users WHERE id = $1`
    
    var u domain.User
    err := r.db.QueryRowContext(ctx, query, id).Scan(
        &u.ID,
        &u.Email,
        &u.Name,
        &u.CreatedAt,
    )
    
    if err == sql.ErrNoRows {
        return nil, domain.ErrUserNotFound
    }
    if err != nil {
        return nil, fmt.Errorf("failed to get user: %w", err)
    }
    
    return &u, nil
}

func (r *userRepository) Create(ctx context.Context, user *domain.User) error {
    query := `
        INSERT INTO users (id, email, name, created_at)
        VALUES ($1, $2, $3, $4)
    `
    
    _, err := r.db.ExecContext(ctx, query,
        user.ID,
        user.Email,
        user.Name,
        user.CreatedAt,
    )
    
    if err != nil {
        return fmt.Errorf("failed to create user: %w", err)
    }
    
    return nil
}
```

### Connection Pool Configuration

```go
func InitDB(connStr string) (*sql.DB, error) {
    db, err := sql.Open("postgres", connStr)
    if err != nil {
        return nil, err
    }
    
    // Connection pool settings
    db.SetMaxOpenConns(25)                  // Maximum open connections
    db.SetMaxIdleConns(5)                   // Maximum idle connections
    db.SetConnMaxLifetime(5 * time.Minute)  // Maximum connection lifetime
    db.SetConnMaxIdleTime(10 * time.Minute) // Maximum idle time
    
    // Verify connection
    ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
    defer cancel()
    
    if err := db.PingContext(ctx); err != nil {
        return nil, fmt.Errorf("failed to ping database: %w", err)
    }
    
    return db, nil
}
```

### Transaction Handling

```go
func (r *userRepository) TransferCredits(ctx context.Context, fromID, toID string, amount int) error {
    tx, err := r.db.BeginTx(ctx, nil)
    if err != nil {
        return fmt.Errorf("failed to begin transaction: %w", err)
    }
    defer tx.Rollback() // Rollback if not committed
    
    // Deduct from sender
    _, err = tx.ExecContext(ctx,
        "UPDATE users SET credits = credits - $1 WHERE id = $2 AND credits >= $1",
        amount, fromID,
    )
    if err != nil {
        return fmt.Errorf("failed to deduct credits: %w", err)
    }
    
    // Add to receiver
    _, err = tx.ExecContext(ctx,
        "UPDATE users SET credits = credits + $1 WHERE id = $2",
        amount, toID,
    )
    if err != nil {
        return fmt.Errorf("failed to add credits: %w", err)
    }
    
    // Commit transaction
    if err := tx.Commit(); err != nil {
        return fmt.Errorf("failed to commit transaction: %w", err)
    }
    
    return nil
}
```

### Anti-Patterns

- ❌ **Global DB Connection**: Do not use `var db *sql.DB` globally. Inject it.
- ❌ **Ignoring Context**: Always use `QueryContext`/`ExecContext` for timeout handling
- ❌ **Leaking Rows**: **ALWAYS** `defer rows.Close()` and check `rows.Err()`

```go
// ❌ BAD
rows, _ := db.Query("SELECT * FROM users")
for rows.Next() {
    // ...
}

// ✅ GOOD
rows, err := db.QueryContext(ctx, "SELECT * FROM users")
if err != nil {
    return err
}
defer rows.Close() // CRITICAL

for rows.Next() {
    // ...
}

if err := rows.Err(); err != nil {
    return err
}
```

---

## 7. Configuration Management

**Priority: P1 (STANDARD)**

### Principles

- **12-Factor App**: Store config in environment variables
- **Typed Config**: Load config into a struct, validate immediately
- **Secrets**: Never commit secrets. Use env vars or secret managers.
- **No Globals**: Return a Config struct and inject it

### Recommended Libraries

- **Standard Lib**: `os.Getenv` for simple apps
- **Viper**: Industry standard for complex configs (env, files, remote config)
- **Koanf**: Lighter, cleaner alternative to Viper
- **Caarlos0/env**: Good for strict struct tagging

### Configuration Pattern

```go
package config

import (
    "fmt"
    "github.com/spf13/viper"
)

type Config struct {
    Server   ServerConfig
    Database DatabaseConfig
    Redis    RedisConfig
}

type ServerConfig struct {
    Port int    `mapstructure:"PORT"`
    Mode string `mapstructure:"MODE"` // debug, release
    Host string `mapstructure:"HOST"`
}

type DatabaseConfig struct {
    Host     string `mapstructure:"DB_HOST"`
    Port     int    `mapstructure:"DB_PORT"`
    User     string `mapstructure:"DB_USER"`
    Password string `mapstructure:"DB_PASSWORD"`
    Name     string `mapstructure:"DB_NAME"`
}

type RedisConfig struct {
    Host string `mapstructure:"REDIS_HOST"`
    Port int    `mapstructure:"REDIS_PORT"`
}

func Load() (*Config, error) {
    // Set defaults
    viper.SetDefault("PORT", 8080)
    viper.SetDefault("MODE", "debug")
    viper.SetDefault("HOST", "0.0.0.0")
    viper.SetDefault("DB_PORT", 5432)
    viper.SetDefault("REDIS_PORT", 6379)
    
    // Read from environment
    viper.AutomaticEnv()
    
    // Optionally read from config file
    viper.SetConfigName("config")
    viper.SetConfigType("yaml")
    viper.AddConfigPath("./configs")
    viper.AddConfigPath(".")
    
    if err := viper.ReadInConfig(); err != nil {
        // Config file is optional, env vars take precedence
        if _, ok := err.(viper.ConfigFileNotFoundError); !ok {
            return nil, err
        }
    }
    
    var cfg Config
    if err := viper.Unmarshal(&cfg); err != nil {
        return nil, fmt.Errorf("failed to unmarshal config: %w", err)
    }
    
    // Validate required fields
    if cfg.Database.Host == "" {
        return nil, fmt.Errorf("DB_HOST is required")
    }
    if cfg.Database.User == "" {
        return nil, fmt.Errorf("DB_USER is required")
    }
    
    return &cfg, nil
}
```

### Usage in Main

```go
func main() {
    cfg, err := config.Load()
    if err != nil {
        log.Fatalf("Failed to load config: %v", err)
    }
    
    // Use config
    db := initDB(cfg.Database)
    server := initServer(cfg.Server, db)
    server.Start()
}
```

---

## 8. Logging & Observability

**Priority: P1 (STANDARD)**

### Principles

- **Structured Logging**: Use JSON or structured text for machine readability
- **Leveled Logging**: Debug, Info, Warn, Error
- **Contextual**: Include correlation IDs (TraceID, RequestID) in logs
- **No `log.Fatal` in Libraries**: Avoid terminating app. Return error instead. Only `main` should exit.

### Recommended Libraries

- **`log/slog`** (Recommended): Stdlib since Go 1.21. Fast, structured, zero-dep.
- **Zap (`uber-go/zap`)**: High performance, good for extreme throughput
- **Zerolog**: Zero allocation, fast JSON logger

### Slog Patterns

#### Basic Setup

```go
package main

import (
    "log/slog"
    "os"
)

func main() {
    // JSON handler for production
    logger := slog.New(slog.NewJSONHandler(os.Stdout, &slog.HandlerOptions{
        Level: slog.LevelInfo,
    }))
    
    // Set as default logger
    slog.SetDefault(logger)
    
    slog.Info("Starting server",
        "port", 8080,
        "env", "production",
    )
}
```

#### Contextual Logging

Extract TraceID from context and add to all logs:

```go
func handleRequest(ctx context.Context, userID string) {
    // Create logger with context attributes
    logger := slog.With(
        "trace_id", ctx.Value("trace_id"),
        "user_id", userID,
    )
    
    logger.Info("Processing request")
    
    // All subsequent logs will include trace_id and user_id
    if err := processData(); err != nil {
        logger.Error("Failed to process data", "error", err)
    }
    
    logger.Info("Request completed")
}
```

#### Custom Handler for Auto-Context

Implement `slog.Handler` to automatically extract attributes from Context:

```go
type ContextHandler struct {
    handler slog.Handler
}

func (h *ContextHandler) Handle(ctx context.Context, r slog.Record) error {
    // Auto-add context values
    if traceID, ok := ctx.Value("trace_id").(string); ok {
        r.AddAttrs(slog.String("trace_id", traceID))
    }
    if userID, ok := ctx.Value("user_id").(string); ok {
        r.AddAttrs(slog.String("user_id", userID))
    }
    
    return h.handler.Handle(ctx, r)
}
```

---

## 9. Security

**Priority: P0 (CRITICAL)**

### Input Validation

- **Validation**: Use `go-playground/validator` for struct validation
- **Sanitization**: Sanitize user input before processing. Use `bluemonday` for HTML sanitization

```go
import "github.com/go-playground/validator/v10"

type CreateUserRequest struct {
    Email    string `json:"email" validate:"required,email"`
    Password string `json:"password" validate:"required,min=8"`
    Age      int    `json:"age" validate:"gte=0,lte=130"`
}

func validateRequest(req *CreateUserRequest) error {
    validate := validator.New()
    return validate.Struct(req)
}
```

### Cryptography

#### Random Number Generation

```go
// ❌ BAD: math/rand is predictable - NEVER for security
import "math/rand"
token := rand.Intn(1000000)

// ✅ GOOD: crypto/rand is cryptographically secure
import (
    "crypto/rand"
    "encoding/base64"
)

func GenerateSecureToken() (string, error) {
    b := make([]byte, 32)
    _, err := rand.Read(b)
    if err != nil {
        return "", err
    }
    return base64.URLEncoding.EncodeToString(b), nil
}
```

#### Password Hashing

```go
import "golang.org/x/crypto/bcrypt"

// Hash password (use cost 14 for production)
func HashPassword(password string) (string, error) {
    bytes, err := bcrypt.GenerateFromPassword([]byte(password), 14)
    return string(bytes), err
}

// Verify password
func CheckPassword(password, hash string) bool {
    err := bcrypt.CompareHashAndPassword([]byte(hash), []byte(password))
    return err == nil
}
```

### SQL Injection Prevention

```go
// ❌ BAD: String concatenation
query := fmt.Sprintf("SELECT * FROM users WHERE email = '%s'", email)
db.Query(query)

// ✅ GOOD: Parameterized query
db.QueryContext(ctx, "SELECT * FROM users WHERE email = $1", email)
```

### JWT Validation

```go
import (
    "fmt"
    "os"
    "time"
    "github.com/golang-jwt/jwt/v5"
)

func ValidateJWT(tokenString string) (*jwt.Token, error) {
    return jwt.Parse(tokenString, func(token *jwt.Token) (interface{}, error) {
        // 1. Validate algorithm
        if _, ok := token.Method.(*jwt.SigningMethodHMAC); !ok {
            return nil, fmt.Errorf("unexpected signing method: %v", token.Header["alg"])
        }
        
        // 2. Validate claims
        claims, ok := token.Claims.(jwt.MapClaims)
        if !ok {
            return nil, fmt.Errorf("invalid claims")
        }
        
        // Validate issuer
        if !claims.VerifyIssuer("your-issuer", true) {
            return nil, fmt.Errorf("invalid issuer")
        }
        
        // Validate expiration
        if !claims.VerifyExpiresAt(time.Now().Unix(), true) {
            return nil, fmt.Errorf("token expired")
        }
        
        // 3. Return secret
        return []byte(os.Getenv("JWT_SECRET")), nil
    })
}
```

### Secret Management

```go
// ✅ Load from environment
jwtSecret := os.Getenv("JWT_SECRET")
if jwtSecret == "" {
    log.Fatal("JWT_SECRET environment variable required")
}

// ❌ NEVER hardcode
const jwtSecret = "my-secret-key" // NEVER DO THIS
```

### Anti-Patterns

- ❌ **No `math/rand` for Security**: RNG is predictable. Use `crypto/rand`.
- ❌ **No `fmt.Sprintf()` for SQL**: Causes SQL injection. Use placeholders.
- ❌ **No MD5 for Passwords**: Use `bcrypt` or `argon2id`.
- ❌ **No Exposed Error Details**: Don't leak stack traces to clients in production.

---

## 10. Testing

**Priority: P0 (CRITICAL)**

### Principles

- **Table-Driven Tests**: Go's idiomatic testing pattern
- **Mocking**: Mock external dependencies (DB, APIs) using interfaces
- **Coverage**: Aim for >80% coverage on critical paths
- **Race Detection**: Always run `go test -race`

### Table-Driven Test Pattern

```go
func TestAdd(t *testing.T) {
    type args struct {
        a int
        b int
    }
    tests := []struct {
        name string
        args args
        want int
    }{
        {"positive numbers", args{1, 2}, 3},
        {"negative numbers", args{-1, -1}, -2},
        {"mixed signs", args{1, -1}, 0},
        {"zero", args{0, 0}, 0},
    }
    
    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            got := Add(tt.args.a, tt.args.b)
            if got != tt.want {
                t.Errorf("Add() = %v, want %v", got, tt.want)
            }
        })
    }
}
```

### Parallel Test Execution

```go
func TestSomething(t *testing.T) {
    t.Parallel() // Parent runs in parallel
    
    tests := []struct {
        name string
        // ...
    }{
        // test cases
    }
    
    for _, tt := range tests {
        tt := tt // Capture range variable
        t.Run(tt.name, func(t *testing.T) {
            t.Parallel() // Subtests run in parallel
            // Test logic...
        })
    }
}
```

### Mocking Strategies

#### Hand-Written Mocks (Simple)

```go
type MockUserRepository struct {
    GetByIDFunc func(ctx context.Context, id string) (*domain.User, error)
}

func (m *MockUserRepository) GetByID(ctx context.Context, id string) (*domain.User, error) {
    if m.GetByIDFunc != nil {
        return m.GetByIDFunc(ctx, id)
    }
    return nil, errors.New("not implemented")
}

// Usage in test
func TestUserService_GetUser(t *testing.T) {
    mockRepo := &MockUserRepository{
        GetByIDFunc: func(ctx context.Context, id string) (*domain.User, error) {
            return &domain.User{ID: id, Email: "test@example.com"}, nil
        },
    }
    
    service := NewUserService(mockRepo)
    user, err := service.GetUser(context.Background(), "123")
    
    if err != nil {
        t.Fatalf("unexpected error: %v", err)
    }
    if user.ID != "123" {
        t.Errorf("expected ID 123, got %s", user.ID)
    }
}
```

#### Testify Mocks

```go
import (
    "github.com/stretchr/testify/mock"
    "github.com/stretchr/testify/assert"
)

type MockUserRepository struct {
    mock.Mock
}

func (m *MockUserRepository) GetByID(ctx context.Context, id string) (*domain.User, error) {
    args := m.Called(ctx, id)
    if args.Get(0) == nil {
        return nil, args.Error(1)
    }
    return args.Get(0).(*domain.User), args.Error(1)
}

// Usage
func TestUserService_GetUser(t *testing.T) {
    mockRepo := new(MockUserRepository)
    mockRepo.On("GetByID", mock.Anything, "123").
        Return(&domain.User{ID: "123", Email: "test@example.com"}, nil)
    
    service := NewUserService(mockRepo)
    user, err := service.GetUser(context.Background(), "123")
    
    assert.NoError(t, err)
    assert.Equal(t, "123", user.ID)
    mockRepo.AssertExpectations(t)
}
```

### Interface Definition Best Practice

**Always define interfaces at the consumer package** (dependency inversion):

```go
// ✅ GOOD: Define interface where it's used (in service package)
// internal/service/user_service.go
package service

type UserRepository interface {
    GetByID(ctx context.Context, id string) (*User, error)
}

type UserService struct {
    repo UserRepository  // Depends on interface, not concrete implementation
}
```

### Integration Testing

```go
// +build integration

func TestUserRepository_Create(t *testing.T) {
    // Setup test database
    db := setupTestDB(t)
    defer teardownTestDB(t, db)
    
    repo := postgres.NewUserRepository(db)
    
    user := &domain.User{
        ID:    "test-123",
        Email: "test@example.com",
    }
    
    err := repo.Create(context.Background(), user)
    assert.NoError(t, err)
    
    // Verify
    retrieved, err := repo.GetByID(context.Background(), "test-123")
    assert.NoError(t, err)
    assert.Equal(t, user.Email, retrieved.Email)
}
```

### Anti-Patterns

- ❌ **Sleeping in tests**: Use channels/waitgroups or retry logic with timeout
- ❌ **Testing implementation details**: Test public behavior/interface, not internals
- ❌ **Not using subtests**: Use `t.Run()` for better organization and parallel execution

---

## Summary Checklist

When building a Go application, ensure:

- ✅ **Code Formatting**: `gofmt`/`goimports` on save
- ✅ **Project Structure**: Follow standard layout with clean architecture layers
- ✅ **Error Handling**: Always wrap errors with context using `fmt.Errorf(..., %w, err)`
- ✅ **Concurrency**: Pass `context.Context` everywhere, use channels for communication
- ✅ **API Server**: Implement graceful shutdown, use middleware for cross-cutting concerns
- ✅ **Database**: Use repository pattern, configure connection pools, always use contexts
- ✅ **Configuration**: Load from env vars, validate on startup
- ✅ **Logging**: Use structured logging (`slog`), include trace IDs
- ✅ **Security**: Use `crypto/rand`, parameterized queries, `bcrypt` for passwords
- ✅ **Testing**: Write table-driven tests, mock dependencies via interfaces
- ✅ **Race Detection**: Run `go test -race` before deployment

---

**Version**: 1.0.0  
**Last Updated**: 2024  
**Maintainer**: Engineering Standards Team
