# Creational Patterns — Go Examples

## Constructor Pattern

Use `New()` or `NewType()` functions with validation:

```go
func NewClient(timeout time.Duration) (*Client, error) {
    if timeout <= 0 {
        return nil, fmt.Errorf("timeout must be positive")
    }
    return &Client{timeout: timeout}, nil
}
```

## Functional Options

For complex configuration (5+ optional params):

```go
type Option func(*Server)

func WithTimeout(d time.Duration) Option {
    return func(s *Server) { s.timeout = d }
}

func NewServer(addr string, opts ...Option) *Server {
    s := &Server{addr: addr, timeout: 30 * time.Second}
    for _, opt := range opts {
        opt(s)
    }
    return s
}
```

## Factory Functions

Conditional object creation (not factory classes):

```go
func NewLogger(typ string) (Logger, error) {
    switch typ {
    case "file": return &FileLogger{}, nil
    case "console": return &ConsoleLogger{}, nil
    default: return nil, fmt.Errorf("unknown type: %s", typ)
    }
}
```

## Avoid Singleton — Use Dependency Injection

```go
// ❌ BAD: Global singleton
var instance *Database
func GetDB() *Database { return instance }

// ✅ GOOD: Explicit dependency
type Service struct { db *Database }
func NewService(db *Database) *Service { return &Service{db: db} }
```
