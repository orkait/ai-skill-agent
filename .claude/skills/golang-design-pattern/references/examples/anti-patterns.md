# Go Anti-Patterns — What NOT to Do

## Don't Simulate OOP Inheritance

```go
// ❌ BAD: Embedding as inheritance is confusing
type Animal struct { Name string }
func (a *Animal) Speak() string { return "..." }

type Dog struct {
    Animal
}
func (d *Dog) Speak() string { return "Woof" }  // Overrides parent — confusing!

// ✅ GOOD: Explicit composition
type Dog struct { name string }
func (d *Dog) Speak() string { return "Woof" }
```

## Don't Create Global State

```go
// ❌ BAD
var db *sql.DB
func init() { db, _ = sql.Open("postgres", dsn) }

// ✅ GOOD: Dependency injection
type Service struct { db *sql.DB }
func NewService(db *sql.DB) *Service { return &Service{db: db} }
```

## Don't Ignore Errors

```go
// ❌ BAD
file, _ := os.Open("data.txt")

// ✅ GOOD
file, err := os.Open("data.txt")
if err != nil {
    return fmt.Errorf("failed to open file: %w", err)
}
defer file.Close()
```

## Don't Create Goroutine Leaks

```go
// ❌ BAD: No cancellation
func worker() {
    for { /* runs forever */ }
}

// ✅ GOOD: Context-aware
func worker(ctx context.Context) {
    for {
        select {
        case <-ctx.Done():
            return
        default:
            // work
        }
    }
}
```

## Don't Use Premature Abstraction

```go
// ❌ BAD: Interface with single implementation
type UserRepo interface { Get(id string) (*User, error) }
type PostgresUserRepo struct {}  // Only implementation

// ✅ GOOD: Start concrete, extract when 2+ implementations exist
type UserStore struct { db *sql.DB }
func (s *UserStore) Get(id string) (*User, error) { /* ... */ }
```
