# Complete Go Design Patterns Reference

This document provides comprehensive explanations, examples, and use cases for all design patterns adapted to Go.

**Note:** This is reference material. For quick guidance, see the main `../SKILL.md`.

---

## Table of Contents

1. [Creational Patterns](#creational-patterns)
2. [Structural Patterns](#structural-patterns)
3. [Behavioral Patterns](#behavioral-patterns)
4. [Concurrency Patterns](#concurrency-patterns)
5. [Error Handling Patterns](#error-handling-patterns)
6. [Testing Patterns](#testing-patterns)

---

## Creational Patterns

### Constructor Pattern

**Purpose:** Create instances with validation and initialization logic.

**When to use:**
- Object requires validation during creation
- Default values need to be set
- Resource allocation needed (connections, files)

**Implementation:**

```go
// Basic constructor
func NewClient(timeout time.Duration) (*Client, error) {
    if timeout <= 0 {
        return nil, fmt.Errorf("timeout must be positive")
    }
    
    return &Client{
        timeout: timeout,
        client:  &http.Client{Timeout: timeout},
    }, nil
}

// Constructor with compile-time interface check
var _ http.Handler = (*MyHandler)(nil)

func NewHandler(logger Logger) *MyHandler {
    return &MyHandler{logger: logger}
}
```

**Common pitfalls:**
- Using `panic` instead of returning errors
- Not validating inputs
- Creating constructors for zero-value-useful types unnecessarily

---

### Functional Options Pattern

**Purpose:** Provide flexible configuration without telescoping constructors.

**When to use:**
- 5+ optional configuration parameters
- Need backward-compatible API evolution
- Clear default values exist

**Implementation:**

```go
type Server struct {
    addr    string
    timeout time.Duration
    maxConn int
    logger  Logger
}

type Option func(*Server)

func WithTimeout(d time.Duration) Option {
    return func(s *Server) { s.timeout = d }
}

func WithMaxConnections(n int) Option {
    return func(s *Server) { s.maxConn = n }
}

func WithLogger(l Logger) Option {
    return func(s *Server) { s.logger = l }
}

func NewServer(addr string, opts ...Option) *Server {
    s := &Server{
        addr:    addr,
        timeout: 30 * time.Second,  // Sensible defaults
        maxConn: 100,
        logger:  defaultLogger,
    }
    
    for _, opt := range opts {
        opt(s)
    }
    
    return s
}

// Usage
srv := NewServer(":8080",
    WithTimeout(60 * time.Second),
    WithMaxConnections(200),
)
```

**Advanced: Options with validation**

```go
func WithTimeout(d time.Duration) Option {
    return func(s *Server) error {
        if d <= 0 {
            return fmt.Errorf("timeout must be positive")
        }
        s.timeout = d
        return nil
    }
}

// Signature changes to return error
type Option func(*Server) error

func NewServer(addr string, opts ...Option) (*Server, error) {
    s := &Server{/* defaults */}
    
    for _, opt := range opts {
        if err := opt(s); err != nil {
            return nil, fmt.Errorf("option failed: %w", err)
        }
    }
    
    return s, nil
}
```

**When NOT to use:**
- Simple constructors with <3 parameters
- When all parameters are required
- Struct literal initialization works fine

---

### Factory Pattern

**Purpose:** Create objects based on runtime conditions without exposing creation logic.

**Traditional OOP vs Go:**

```go
// ❌ Traditional OOP style (don't do this in Go)
type LoggerFactory struct{}

func (f *LoggerFactory) CreateLogger(typ string) Logger {
    // Factory class is unnecessary
}

// ✅ Go style: simple function
func NewLogger(typ string) (Logger, error) {
    switch typ {
    case "file":
        return &FileLogger{}, nil
    case "console":
        return &ConsoleLogger{}, nil
    case "remote":
        return &RemoteLogger{}, nil
    default:
        return nil, fmt.Errorf("unknown logger type: %s", typ)
    }
}

// ✅ Factory with configuration
func NewDatabase(cfg Config) (Database, error) {
    switch cfg.Driver {
    case "postgres":
        return postgres.New(cfg.DSN)
    case "mysql":
        return mysql.New(cfg.DSN)
    default:
        return nil, fmt.Errorf("unsupported driver: %s", cfg.Driver)
    }
}
```

**Registry pattern variation:**

```go
type Factory func(config Config) (Plugin, error)

var registry = make(map[string]Factory)

func Register(name string, factory Factory) {
    registry[name] = factory
}

func Create(name string, cfg Config) (Plugin, error) {
    factory, ok := registry[name]
    if !ok {
        return nil, fmt.Errorf("unknown plugin: %s", name)
    }
    return factory(cfg)
}

// Plugins register themselves
func init() {
    Register("aws", newAWSPlugin)
    Register("gcp", newGCPPlugin)
}
```

---

### Builder Pattern

**Purpose:** Construct complex objects step-by-step with validation.

**When to use:**
- Object construction requires multiple steps
- Need to enforce construction order
- Want to validate intermediate states

**Implementation:**

```go
type QueryBuilder struct {
    table   string
    columns []string
    where   []string
    orderBy string
    limit   int
    err     error  // Accumulate errors
}

func NewQueryBuilder(table string) *QueryBuilder {
    return &QueryBuilder{table: table}
}

func (b *QueryBuilder) Select(columns ...string) *QueryBuilder {
    if b.err != nil {
        return b
    }
    if len(columns) == 0 {
        b.err = fmt.Errorf("no columns specified")
        return b
    }
    b.columns = columns
    return b
}

func (b *QueryBuilder) Where(condition string) *QueryBuilder {
    if b.err != nil {
        return b
    }
    if condition == "" {
        b.err = fmt.Errorf("empty where condition")
        return b
    }
    b.where = append(b.where, condition)
    return b
}

func (b *QueryBuilder) OrderBy(column string) *QueryBuilder {
    if b.err != nil {
        return b
    }
    b.orderBy = column
    return b
}

func (b *QueryBuilder) Limit(n int) *QueryBuilder {
    if b.err != nil {
        return b
    }
    if n <= 0 {
        b.err = fmt.Errorf("limit must be positive")
        return b
    }
    b.limit = n
    return b
}

func (b *QueryBuilder) Build() (string, error) {
    if b.err != nil {
        return "", b.err
    }
    
    if b.table == "" {
        return "", fmt.Errorf("table name required")
    }
    
    // Build query string
    cols := "*"
    if len(b.columns) > 0 {
        cols = strings.Join(b.columns, ", ")
    }
    
    query := fmt.Sprintf("SELECT %s FROM %s", cols, b.table)
    
    if len(b.where) > 0 {
        query += " WHERE " + strings.Join(b.where, " AND ")
    }
    
    if b.orderBy != "" {
        query += " ORDER BY " + b.orderBy
    }
    
    if b.limit > 0 {
        query += fmt.Sprintf(" LIMIT %d", b.limit)
    }
    
    return query, nil
}

// Usage
query, err := NewQueryBuilder("users").
    Select("id", "email", "name").
    Where("age > 18").
    Where("active = true").
    OrderBy("created_at DESC").
    Limit(10).
    Build()

if err != nil {
    log.Fatal(err)
}
fmt.Println(query)
```

**When to use Builder vs Functional Options:**
- **Builder:** Complex construction with validation at each step
- **Functional Options:** Configuration with independent optional parameters

---

### Singleton Pattern (Avoid!)

**Purpose:** Ensure only one instance exists.

**Why to avoid:** Global state makes testing difficult and creates hidden dependencies.

**If you must use it:**

```go
// Thread-safe lazy initialization
var (
    instance *Config
    once     sync.Once
)

func GetConfig() *Config {
    once.Do(func() {
        instance = &Config{
            // Load from file/env
        }
    })
    return instance
}

// ✅ BETTER: Dependency injection
type Service struct {
    config *Config
}

func NewService(cfg *Config) *Service {
    return &Service{config: cfg}
}

// In main()
func main() {
    cfg := loadConfig()  // Create once
    
    userService := NewUserService(cfg)
    orderService := NewOrderService(cfg)
    // Explicit dependencies
}
```

**Legitimate use cases:**
- Application configuration loaded once at startup
- Global logger (though context-based logging is better)

---

## Structural Patterns

### Adapter Pattern

**Purpose:** Convert one interface to another to make incompatible interfaces work together.

**When to use:**
- Integrating third-party libraries
- Wrapping legacy code
- Converting between different data representations

**Implementation:**

```go
// Your interface
type Storage interface {
    Save(ctx context.Context, key string, value []byte) error
    Load(ctx context.Context, key string) ([]byte, error)
    Delete(ctx context.Context, key string) error
}

// External library (Redis client)
type RedisClient struct {
    client *redis.Client
}

func (r *RedisClient) Set(key string, val []byte, ttl time.Duration) error {
    return r.client.Set(context.Background(), key, val, ttl).Err()
}

func (r *RedisClient) Get(key string) ([]byte, error) {
    return r.client.Get(context.Background(), key).Bytes()
}

func (r *RedisClient) Del(key string) error {
    return r.client.Del(context.Background(), key).Err()
}

// Adapter
type RedisStorageAdapter struct {
    client *RedisClient
    ttl    time.Duration
}

func NewRedisStorageAdapter(client *RedisClient, ttl time.Duration) *RedisStorageAdapter {
    return &RedisStorageAdapter{
        client: client,
        ttl:    ttl,
    }
}

func (a *RedisStorageAdapter) Save(ctx context.Context, key string, value []byte) error {
    return a.client.Set(key, value, a.ttl)
}

func (a *RedisStorageAdapter) Load(ctx context.Context, key string) ([]byte, error) {
    return a.client.Get(key)
}

func (a *RedisStorageAdapter) Delete(ctx context.Context, key string) error {
    return a.client.Del(key)
}

// Compile-time interface verification
var _ Storage = (*RedisStorageAdapter)(nil)

// Usage
storage := NewRedisStorageAdapter(redisClient, 5*time.Minute)
err := storage.Save(ctx, "user:123", userData)
```

**Best practices:**
- Keep adapters thin - only translation, no business logic
- Use compile-time interface checks: `var _ Interface = (*Adapter)(nil)`
- Document what's being adapted and why

---

### Decorator Pattern

**Purpose:** Add behavior to objects dynamically without modifying them.

**Go's most common use:** HTTP middleware

**Implementation:**

```go
// Handler signature
type Handler func(http.ResponseWriter, *http.Request)

// Decorator: Logging
func WithLogging(next Handler) Handler {
    return func(w http.ResponseWriter, r *http.Request) {
        start := time.Now()
        log.Printf("Started %s %s", r.Method, r.URL.Path)
        
        next(w, r)
        
        log.Printf("Completed %s in %v", r.URL.Path, time.Since(start))
    }
}

// Decorator: Authentication
func WithAuth(next Handler) Handler {
    return func(w http.ResponseWriter, r *http.Request) {
        token := r.Header.Get("Authorization")
        if token == "" {
            http.Error(w, "Unauthorized", http.StatusUnauthorized)
            return
        }
        
        // Validate token
        if !isValidToken(token) {
            http.Error(w, "Invalid token", http.StatusForbidden)
            return
        }
        
        next(w, r)
    }
}

// Decorator: Rate limiting (with state)
func WithRateLimit(limit int) func(Handler) Handler {
    limiter := rate.NewLimiter(rate.Limit(limit), limit)
    
    return func(next Handler) Handler {
        return func(w http.ResponseWriter, r *http.Request) {
            if !limiter.Allow() {
                http.Error(w, "Rate limit exceeded", http.StatusTooManyRequests)
                return
            }
            next(w, r)
        }
    }
}

// Decorator: Error recovery
func WithRecovery(next Handler) Handler {
    return func(w http.ResponseWriter, r *http.Request) {
        defer func() {
            if err := recover(); err != nil {
                log.Printf("Panic: %v\n%s", err, debug.Stack())
                http.Error(w, "Internal Server Error", http.StatusInternalServerError)
            }
        }()
        
        next(w, r)
    }
}

// Stack decorators (applied bottom-up)
handler := WithRecovery(
    WithLogging(
        WithAuth(
            WithRateLimit(100)(
                actualHandler,
            ),
        ),
    ),
)

// Execution order: Recovery → Logging → Auth → RateLimit → Handler
```

**io.Reader/Writer decorators:**

```go
// Counting decorator
type CountingReader struct {
    reader io.Reader
    count  int64
}

func (r *CountingReader) Read(p []byte) (n int, err error) {
    n, err = r.reader.Read(p)
    atomic.AddInt64(&r.count, int64(n))
    return n, err
}

func (r *CountingReader) BytesRead() int64 {
    return atomic.LoadInt64(&r.count)
}

// Compression decorator
type GzipReader struct {
    reader io.Reader
    gzReader *gzip.Reader
}

func NewGzipReader(r io.Reader) (*GzipReader, error) {
    gr, err := gzip.NewReader(r)
    if err != nil {
        return nil, err
    }
    return &GzipReader{reader: r, gzReader: gr}, nil
}

func (g *GzipReader) Read(p []byte) (n int, err error) {
    return g.gzReader.Read(p)
}

func (g *GzipReader) Close() error {
    return g.gzReader.Close()
}

// Usage: Stack decorators
file, _ := os.Open("data.txt.gz")
gzipReader, _ := NewGzipReader(file)
counter := &CountingReader{reader: gzipReader}

io.Copy(os.Stdout, counter)
fmt.Printf("Read %d bytes\n", counter.BytesRead())
```

---

### Proxy Pattern

**Purpose:** Control access to an object through a surrogate.

**Use cases:**
- Lazy initialization
- Access control
- Caching
- Logging

**Implementation: Caching Proxy**

```go
type Database interface {
    Query(ctx context.Context, sql string) ([]Row, error)
    Execute(ctx context.Context, sql string) error
}

type CachingDatabaseProxy struct {
    db    Database
    cache map[string]cachedResult
    mu    sync.RWMutex
    ttl   time.Duration
}

type cachedResult struct {
    data      []Row
    timestamp time.Time
}

func NewCachingProxy(db Database, ttl time.Duration) *CachingDatabaseProxy {
    return &CachingDatabaseProxy{
        db:    db,
        cache: make(map[string]cachedResult),
        ttl:   ttl,
    }
}

func (p *CachingDatabaseProxy) Query(ctx context.Context, sql string) ([]Row, error) {
    // Try cache first
    p.mu.RLock()
    if cached, ok := p.cache[sql]; ok {
        if time.Since(cached.timestamp) < p.ttl {
            p.mu.RUnlock()
            return cached.data, nil  // Cache hit
        }
    }
    p.mu.RUnlock()
    
    // Cache miss - query database
    rows, err := p.db.Query(ctx, sql)
    if err != nil {
        return nil, err
    }
    
    // Update cache
    p.mu.Lock()
    p.cache[sql] = cachedResult{
        data:      rows,
        timestamp: time.Now(),
    }
    p.mu.Unlock()
    
    return rows, nil
}

func (p *CachingDatabaseProxy) Execute(ctx context.Context, sql string) error {
    // Invalidate cache on writes
    p.mu.Lock()
    p.cache = make(map[string]cachedResult)  // Simple invalidation
    p.mu.Unlock()
    
    return p.db.Execute(ctx, sql)
}

// Verify interface
var _ Database = (*CachingDatabaseProxy)(nil)
```

**Implementation: Lazy Loading Proxy**

```go
type ConnectionProxy struct {
    once sync.Once
    conn *sql.DB
    err  error
    dsn  string
}

func NewConnectionProxy(dsn string) *ConnectionProxy {
    return &ConnectionProxy{dsn: dsn}
}

func (p *ConnectionProxy) getConnection() (*sql.DB, error) {
    p.once.Do(func() {
        p.conn, p.err = sql.Open("postgres", p.dsn)
    })
    return p.conn, p.err
}

func (p *ConnectionProxy) Query(ctx context.Context, query string) (*sql.Rows, error) {
    conn, err := p.getConnection()
    if err != nil {
        return nil, fmt.Errorf("connection failed: %w", err)
    }
    return conn.QueryContext(ctx, query)
}
```

---

### Composite Pattern

**Purpose:** Treat individual objects and compositions uniformly.

**Go adaptation:** Interfaces with recursive structures

```go
// Component interface
type FileSystemNode interface {
    Name() string
    Size() int64
    IsDir() bool
}

// Leaf: File
type File struct {
    name string
    size int64
}

func (f *File) Name() string  { return f.name }
func (f *File) Size() int64   { return f.size }
func (f *File) IsDir() bool   { return false }

// Composite: Directory
type Directory struct {
    name     string
    children []FileSystemNode
}

func (d *Directory) Name() string { return d.name }
func (d *Directory) IsDir() bool  { return true }

func (d *Directory) Size() int64 {
    var total int64
    for _, child := range d.children {
        total += child.Size()
    }
    return total
}

func (d *Directory) Add(node FileSystemNode) {
    d.children = append(d.children, node)
}

// Usage
root := &Directory{name: "/"}
home := &Directory{name: "home"}
root.Add(home)

home.Add(&File{name: "doc.txt", size: 1024})
home.Add(&File{name: "image.png", size: 2048})

fmt.Printf("Total size: %d bytes\n", root.Size())  // 3072
```

---

[Content continues with Behavioral Patterns, Concurrency Patterns, Error Handling, and Testing sections - truncated for length]

This reference is meant to be comprehensive. For day-to-day work, use the quick reference in `../SKILL.md`.
