# Concurrency, Error Handling & Testing Patterns — Go Examples

## Concurrency Patterns

### Worker Pool — Bounded goroutine execution

```go
type WorkerPool struct {
    workers int
    jobs    chan Job
    wg      sync.WaitGroup
}

func (p *WorkerPool) Start(ctx context.Context) {
    for i := 0; i < p.workers; i++ {
        p.wg.Add(1)
        go p.worker(ctx)
    }
}
```

### Pipeline — Chain processing stages with channels

```go
func generator(nums ...int) <-chan int {
    out := make(chan int)
    go func() {
        defer close(out)
        for _, n := range nums { out <- n }
    }()
    return out
}

func square(in <-chan int) <-chan int {
    out := make(chan int)
    go func() {
        defer close(out)
        for n := range in { out <- n * n }
    }()
    return out
}
```

### Fan-Out/Fan-In — Distribute work, collect results

```go
func fanIn(channels ...<-chan int) <-chan int {
    out := make(chan int)
    var wg sync.WaitGroup

    for _, ch := range channels {
        wg.Add(1)
        go func(c <-chan int) {
            defer wg.Done()
            for n := range c { out <- n }
        }(ch)
    }

    go func() { wg.Wait(); close(out) }()
    return out
}
```

## Error Handling Patterns

### Sentinel Errors — Pre-defined error constants

```go
var (
    ErrNotFound     = errors.New("not found")
    ErrUnauthorized = errors.New("unauthorized")
)

if errors.Is(err, ErrNotFound) { /* handle */ }
```

### Error Wrapping — Add context with `%w`

```go
func ProcessOrder(id string) error {
    order, err := fetchOrder(id)
    if err != nil {
        return fmt.Errorf("failed to fetch order %s: %w", id, err)
    }
    return nil
}
```

### Custom Error Types — For structured error data

```go
type ValidationError struct {
    Field string
    Issue string
}

func (e *ValidationError) Error() string {
    return fmt.Sprintf("validation failed: %s - %s", e.Field, e.Issue)
}

var validationErr *ValidationError
if errors.As(err, &validationErr) { /* use fields */ }
```

## Testing Patterns

### Table-Driven Tests

```go
func TestAdd(t *testing.T) {
    tests := []struct {
        name string
        a, b int
        want int
    }{
        {"positive", 1, 2, 3},
        {"negative", -1, -1, -2},
        {"zero", 0, 0, 0},
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            got := Add(tt.a, tt.b)
            if got != tt.want {
                t.Errorf("got %d, want %d", got, tt.want)
            }
        })
    }
}
```

### Interface Mocking — Hand-written mocks with function fields

```go
type MockUserRepo struct {
    GetByIDFunc func(ctx context.Context, id string) (*User, error)
}

func (m *MockUserRepo) GetByID(ctx context.Context, id string) (*User, error) {
    if m.GetByIDFunc != nil {
        return m.GetByIDFunc(ctx, id)
    }
    return nil, errors.New("not implemented")
}

// Verify interface at compile time
var _ UserRepository = (*MockUserRepo)(nil)
```
