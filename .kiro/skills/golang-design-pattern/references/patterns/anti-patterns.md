# Go Anti-Patterns: What NOT to Do

Common mistakes when coming from OOP languages or misapplying design patterns in Go.

---

## 1. Inheritance via Embedding

**Problem:** Treating embedding as inheritance/polymorphism.

```go
// ❌ BAD: Simulating inheritance
type Animal struct {
    Name string
}

func (a *Animal) Speak() string {
    return "generic sound"
}

type Dog struct {
    Animal  // Embedded to "inherit"
}

func (d *Dog) Speak() string {
    return "Woof"  // Trying to "override"
}

// Confusing behavior:
var animal Animal = Dog{Animal{Name: "Rex"}}  // Compile error!
// Embedding doesn't create an "is-a" relationship

// ✅ GOOD: Explicit composition
type Dog struct {
    name string
}

func (d *Dog) Speak() string {
    return "Woof"
}

type Cat struct {
    name string
}

func (c *Cat) Speak() string {
    return "Meow"
}

// Use interface for polymorphism
type Speaker interface {
    Speak() string
}

func MakeNoise(s Speaker) {
    fmt.Println(s.Speak())
}
```

**Why it's bad:**
- Embedding is for field/method promotion, not inheritance
- Creates confusion about method resolution
- Violates Go's composition philosophy

---

## 2. Global Mutable State

**Problem:** Using global variables for shared state.

```go
// ❌ BAD: Global database connection
var db *sql.DB

func init() {
    var err error
    db, err = sql.Open("postgres", os.Getenv("DSN"))
    if err != nil {
        log.Fatal(err)
    }
}

func GetUser(id string) (*User, error) {
    // Hidden dependency on global db
    return queryUser(db, id)
}

// Testing is nightmare:
// - Can't run tests in parallel
// - Must mock global state
// - Hidden dependencies

// ✅ GOOD: Explicit dependency injection
type UserService struct {
    db *sql.DB
}

func NewUserService(db *sql.DB) *UserService {
    return &UserService{db: db}
}

func (s *UserService) GetUser(id string) (*User, error) {
    return queryUser(s.db, id)
}

// Testing:
func TestUserService_GetUser(t *testing.T) {
    mockDB := &MockDB{}
    service := NewUserService(mockDB)
    // Easy to test with mock
}

// Main:
func main() {
    db, _ := sql.Open("postgres", dsn)
    defer db.Close()
    
    userService := NewUserService(db)
    orderService := NewOrderService(db)
    // Explicit dependencies visible
}
```

**Why it's bad:**
- Makes testing difficult (can't run parallel tests)
- Creates hidden dependencies
- Violates single responsibility (init does too much)
- Hard to trace data flow

---

## 3. Init() Abuse

**Problem:** Using `init()` for complex setup or dependency initialization.

```go
// ❌ BAD: Complex init
var (
    config *Config
    logger *Logger
    cache  *Cache
)

func init() {
    config = loadConfig()  // File I/O
    logger = setupLogger(config)
    cache = newCache(config.CacheSize)
    // Hard to control initialization order
    // Can't handle errors properly
    // Creates global state
}

// ✅ GOOD: Explicit initialization
type App struct {
    config *Config
    logger *Logger
    cache  *Cache
}

func NewApp() (*App, error) {
    config, err := loadConfig()
    if err != nil {
        return nil, fmt.Errorf("load config: %w", err)
    }
    
    logger, err := setupLogger(config)
    if err != nil {
        return nil, fmt.Errorf("setup logger: %w", err)
    }
    
    cache := newCache(config.CacheSize)
    
    return &App{
        config: config,
        logger: logger,
        cache:  cache,
    }, nil
}

func main() {
    app, err := NewApp()
    if err != nil {
        log.Fatal(err)
    }
    defer app.Close()
    
    app.Run()
}
```

**Legitimate uses of init():**
- Registering drivers: `database/sql`
- Setting up package-level constants
- One-time computations with no side effects

---

## 4. Ignoring Errors

**Problem:** Using blank identifier `_` for errors or not checking them.

```go
// ❌ BAD: Ignoring errors
file, _ := os.Open("config.json")
defer file.Close()
json.NewDecoder(file).Decode(&config)

// Potential panic if file is nil!

// ❌ BAD: Silent failures
func saveUser(user *User) {
    _ = db.Save(user)  // Error lost
}

// ✅ GOOD: Always check errors
file, err := os.Open("config.json")
if err != nil {
    return fmt.Errorf("failed to open config: %w", err)
}
defer file.Close()

if err := json.NewDecoder(file).Decode(&config); err != nil {
    return fmt.Errorf("failed to decode config: %w", err)
}

// ✅ GOOD: At minimum, log errors
func saveUser(user *User) error {
    if err := db.Save(user); err != nil {
        log.Printf("WARNING: failed to save user %s: %v", user.ID, err)
        return err
    }
    return nil
}
```

**Exception:** Explicitly documented intentional ignore
```go
// Ignore error because fallback is acceptable
_ = cache.Set(key, value)  // Cache miss is acceptable

// But better:
if err := cache.Set(key, value); err != nil {
    log.Printf("cache set failed (non-critical): %v", err)
}
```

---

## 5. Goroutine Leaks

**Problem:** Starting goroutines without termination mechanism.

```go
// ❌ BAD: No way to stop
func streamData() <-chan Data {
    ch := make(chan Data)
    go func() {
        for {
            ch <- fetchData()  // Runs forever
            time.Sleep(time.Second)
        }
    }()
    return ch
}

// If consumer stops reading, goroutine blocks forever

// ✅ GOOD: Context-aware cancellation
func streamData(ctx context.Context) <-chan Data {
    ch := make(chan Data)
    go func() {
        defer close(ch)
        ticker := time.NewTicker(time.Second)
        defer ticker.Stop()
        
        for {
            select {
            case <-ticker.C:
                select {
                case ch <- fetchData():
                case <-ctx.Done():
                    return
                }
            case <-ctx.Done():
                return
            }
        }
    }()
    return ch
}

// Usage
ctx, cancel := context.WithTimeout(context.Background(), 5*time.Minute)
defer cancel()

for data := range streamData(ctx) {
    process(data)
}
```

**Common leak patterns:**
```go
// ❌ Unbuffered channel with no receiver
ch := make(chan int)
go func() {
    ch <- 1  // Blocks forever if no receiver
}()

// ❌ Infinite loop with no exit
go func() {
    for {
        work()  // No way to stop
    }
}()

// ❌ Blocked on channel send
go func() {
    for item := range input {
        output <- process(item)  // Blocks if output is full
    }
}()
```

---

## 6. Panic for Control Flow

**Problem:** Using `panic` for business logic errors.

```go
// ❌ BAD: Panic for expected errors
func GetUser(id string) *User {
    user := db.Find(id)
    if user == nil {
        panic("user not found")  // Don't use panic!
    }
    return user
}

// ✅ GOOD: Return errors
func GetUser(id string) (*User, error) {
    user := db.Find(id)
    if user == nil {
        return nil, ErrUserNotFound
    }
    return user, nil
}

// Panic is only for:
// 1. Unrecoverable programmer errors
func validateConfig(cfg *Config) {
    if cfg == nil {
        panic("nil config")  // Programmer error
    }
}

// 2. Init-time failures
func init() {
    if err := loadCriticalData(); err != nil {
        panic(fmt.Sprintf("failed to load critical data: %v", err))
    }
}
```

---

## 7. Premature Interface Abstraction

**Problem:** Creating interfaces before they're needed.

```go
// ❌ BAD: Interface with single implementation
package user

type Repository interface {
    Get(id string) (*User, error)
    Create(user *User) error
    Update(user *User) error
    Delete(id string) error
}

type PostgresRepository struct {
    db *sql.DB
}
// Only implementation in entire codebase

// ✅ GOOD: Start with concrete type
package user

type Repository struct {
    db *sql.DB
}

func (r *Repository) Get(id string) (*User, error) { ... }
func (r *Repository) Create(user *User) error { ... }

// Extract interface when you have 2+ implementations
// or when consumer package needs to define it
```

**When to create interfaces:**
- Consumer package needs to mock dependency (testing)
- 2+ implementations exist
- Defining contract between packages
- Standard library interfaces (`io.Reader`, `http.Handler`)

---

## 8. Large Interfaces

**Problem:** Creating interfaces with many methods.

```go
// ❌ BAD: God interface
type UserManager interface {
    Create(user *User) error
    Update(user *User) error
    Delete(id string) error
    Get(id string) (*User, error)
    List(filters Filters) ([]*User, error)
    Authenticate(email, password string) (*User, error)
    ResetPassword(id string) error
    SendWelcomeEmail(id string) error
    UpdatePreferences(id string, prefs Preferences) error
}

// Hard to mock, violates interface segregation

// ✅ GOOD: Small, focused interfaces
type UserReader interface {
    Get(id string) (*User, error)
    List(filters Filters) ([]*User, error)
}

type UserWriter interface {
    Create(user *User) error
    Update(user *User) error
    Delete(id string) error
}

type Authenticator interface {
    Authenticate(email, password string) (*User, error)
}

// Services depend only on what they need
type ProfileService struct {
    users UserReader  // Only needs read access
}

type AdminService struct {
    users UserWriter  // Only needs write access
}
```

**Go's guideline:** Interfaces should have 1-3 methods

---

## 9. Context Misuse

**Problem:** Not passing context or creating long-lived contexts.

```go
// ❌ BAD: No context
func FetchData() ([]byte, error) {
    resp, err := http.Get("http://api.example.com")
    // Can't cancel, no timeout
}

// ❌ BAD: Creating context in function
func FetchData() ([]byte, error) {
    ctx := context.Background()  // Should be passed in
    req, _ := http.NewRequestWithContext(ctx, "GET", url, nil)
    // ...
}

// ❌ BAD: Storing context in struct
type Fetcher struct {
    ctx context.Context  // Don't store context
}

// ✅ GOOD: Pass context as first parameter
func FetchData(ctx context.Context) ([]byte, error) {
    req, err := http.NewRequestWithContext(ctx, "GET", url, nil)
    if err != nil {
        return nil, err
    }
    
    resp, err := http.DefaultClient.Do(req)
    if err != nil {
        return nil, err
    }
    defer resp.Body.Close()
    
    return io.ReadAll(resp.Body)
}

// Usage with timeout
ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
defer cancel()

data, err := FetchData(ctx)
```

**Context rules:**
1. First parameter: `func DoSomething(ctx context.Context, ...)`
2. Never store in structs
3. Pass down the call chain
4. Create once at top level (main, HTTP handler)

---

## 10. Mutex in Value Types

**Problem:** Copying structs that contain mutexes.

```go
// ❌ BAD: Mutex in value type
type Cache struct {
    mu    sync.Mutex  // Copied when Cache is copied!
    items map[string]interface{}
}

func (c Cache) Get(key string) interface{} {  // Value receiver
    c.mu.Lock()  // Locking a copy!
    defer c.mu.Unlock()
    return c.items[key]
}

cache := Cache{items: make(map[string]interface{})}
cache2 := cache  // Copies the mutex - breaks thread safety!

// ✅ GOOD: Pointer receiver for types with mutexes
type Cache struct {
    mu    sync.Mutex
    items map[string]interface{}
}

func (c *Cache) Get(key string) interface{} {  // Pointer receiver
    c.mu.Lock()
    defer c.mu.Unlock()
    return c.items[key]
}

// Or use sync.RWMutex for better read performance
type Cache struct {
    mu    sync.RWMutex
    items map[string]interface{}
}

func (c *Cache) Get(key string) interface{} {
    c.mu.RLock()
    defer c.mu.RUnlock()
    return c.items[key]
}
```

**Rule:** Types containing sync primitives must use pointer receivers

---

## 11. String Concatenation in Loops

**Problem:** Using `+` for string building in loops.

```go
// ❌ BAD: O(n²) performance
func buildQuery(columns []string) string {
    query := "SELECT "
    for i, col := range columns {
        query += col  // Creates new string each iteration
        if i < len(columns)-1 {
            query += ", "
        }
    }
    return query + " FROM users"
}

// ✅ GOOD: Use strings.Builder
func buildQuery(columns []string) string {
    var b strings.Builder
    b.WriteString("SELECT ")
    
    for i, col := range columns {
        b.WriteString(col)
        if i < len(columns)-1 {
            b.WriteString(", ")
        }
    }
    
    b.WriteString(" FROM users")
    return b.String()
}

// Or strings.Join for simple cases
func buildQuery(columns []string) string {
    return "SELECT " + strings.Join(columns, ", ") + " FROM users"
}
```

---

## 12. Not Closing Resources

**Problem:** Forgetting to close files, connections, response bodies.

```go
// ❌ BAD: Resource leak
func readConfig() (*Config, error) {
    file, err := os.Open("config.json")
    if err != nil {
        return nil, err
    }
    // Missing: defer file.Close()
    
    var cfg Config
    err = json.NewDecoder(file).Decode(&cfg)
    return &cfg, err
}

// ❌ BAD: Not checking Close error
defer file.Close()  // Error ignored

// ✅ GOOD: Always defer Close
func readConfig() (*Config, error) {
    file, err := os.Open("config.json")
    if err != nil {
        return nil, err
    }
    defer file.Close()  // Guaranteed cleanup
    
    var cfg Config
    if err := json.NewDecoder(file).Decode(&cfg); err != nil {
        return nil, fmt.Errorf("decode config: %w", err)
    }
    
    return &cfg, nil
}

// ✅ GOOD: Check Close error when it matters
func writeData(data []byte) (err error) {
    file, err := os.Create("output.dat")
    if err != nil {
        return err
    }
    
    defer func() {
        if cerr := file.Close(); cerr != nil && err == nil {
            err = cerr  // Return close error if no other error
        }
    }()
    
    _, err = file.Write(data)
    return err
}
```

**Common resources to close:**
- `*os.File`
- `*sql.Rows`
- `http.Response.Body`
- Network connections
- Custom types with `Close()` method

---

## 13. Testing Anti-Patterns

### Not Using Table-Driven Tests

```go
// ❌ BAD: Separate test for each case
func TestAdd_PositiveNumbers(t *testing.T) {
    result := Add(1, 2)
    if result != 3 {
        t.Errorf("expected 3, got %d", result)
    }
}

func TestAdd_NegativeNumbers(t *testing.T) {
    result := Add(-1, -1)
    if result != -2 {
        t.Errorf("expected -2, got %d", result)
    }
}

// ✅ GOOD: Table-driven
func TestAdd(t *testing.T) {
    tests := []struct {
        name string
        a, b int
        want int
    }{
        {"positive", 1, 2, 3},
        {"negative", -1, -1, -2},
        {"zero", 0, 0, 0},
        {"mixed", 5, -3, 2},
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

### Testing Implementation Instead of Behavior

```go
// ❌ BAD: Testing internal implementation
func TestCache_InternalMap(t *testing.T) {
    cache := NewCache()
    cache.items["key"] = "value"  // Accessing internal field
    
    if len(cache.items) != 1 {
        t.Error("expected 1 item in map")
    }
}

// ✅ GOOD: Test public behavior
func TestCache_SetAndGet(t *testing.T) {
    cache := NewCache()
    cache.Set("key", "value")
    
    got, ok := cache.Get("key")
    if !ok {
        t.Fatal("expected key to exist")
    }
    if got != "value" {
        t.Errorf("got %v, want %v", got, "value")
    }
}
```

---

## Quick Anti-Pattern Checklist

❌ **AVOID:**
- Embedding for inheritance
- Global mutable state
- Complex `init()` functions
- Ignoring errors with `_`
- Starting goroutines without cancellation
- Using `panic` for business logic
- Interfaces before you need them
- Large interfaces (>3 methods)
- Not passing `context.Context`
- Storing mutexes in value types
- String concatenation in loops
- Not closing resources
- Separate tests instead of table-driven

✅ **DO:**
- Use composition explicitly
- Inject dependencies
- Return errors from constructors
- Always check errors
- Use `context.Context` for cancellation
- Return errors, not panic
- Extract interfaces when needed
- Keep interfaces small (1-3 methods)
- Pass context as first parameter
- Use pointer receivers for mutex types
- Use `strings.Builder` for loops
- `defer` resource cleanup
- Write table-driven tests

---

This anti-patterns guide helps you avoid common pitfalls when transitioning from OOP to Go or applying design patterns incorrectly.
