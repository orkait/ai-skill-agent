# Structural & Behavioral Patterns — Go Examples

## Structural Patterns

### Adapter — Wrap external types to match your interface

```go
type Storage interface {
    Save(ctx context.Context, key string, data []byte) error
}

type RedisAdapter struct { client *RedisClient }

func (a *RedisAdapter) Save(ctx context.Context, key string, data []byte) error {
    return a.client.Set(key, data, 5*time.Minute)
}
```

### Decorator — Middleware pattern for HTTP handlers

```go
func WithLogging(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        log.Printf("%s %s", r.Method, r.URL.Path)
        next.ServeHTTP(w, r)
    })
}
```

### Composition — Embed structs to promote fields/methods

```go
type Logger struct { mu sync.Mutex; file *os.File }

type Service struct {
    Logger  // Embedded — promotes Logger's methods
    db *sql.DB
}
```

### Consumer-Side Interfaces — Define where used, not where implemented

```go
// ✅ GOOD: Interface in consumer package
package service

type UserGetter interface {
    GetByID(ctx context.Context, id string) (*User, error)
}

type UserService struct {
    users UserGetter  // Only needs GetByID
}
```

## Behavioral Patterns

### Strategy — Interface or function type

```go
type CompressionStrategy interface {
    Compress([]byte) ([]byte, error)
}

type FileStorage struct { compression CompressionStrategy }

// Or simpler: function type for stateless strategies
type CompressFunc func([]byte) ([]byte, error)
```

### Observer — Use channels (more idiomatic than callbacks)

```go
type EventBus struct {
    subscribers []chan Event
}

func (b *EventBus) Subscribe() <-chan Event {
    ch := make(chan Event, 10)
    b.subscribers = append(b.subscribers, ch)
    return ch
}
```

### Command — Function closures for job queues

```go
type Job func(context.Context) error

type Worker struct { jobs chan Job }

func (w *Worker) Submit(job Job) { w.jobs <- job }
```

### Template Method — Injected functions (no inheritance)

```go
type ProcessingSteps struct {
    Load      func() ([]byte, error)
    Transform func([]byte) ([]byte, error)
    Save      func([]byte) error
}

type Processor struct { steps ProcessingSteps }
```
