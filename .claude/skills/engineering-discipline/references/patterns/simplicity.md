# Simplicity & Efficiency Principles

## KISS (Keep It Simple, Stupid)

**Definition:** Use the simplest solution that solves the problem. Avoid unnecessary complexity, over-engineering, or premature optimization.

**Supported by:** *Clean Code*, *The Pragmatic Programmer*

### Examples

```javascript
// Bad - Unnecessary abstraction
class SingleValueContainer {
    constructor(value) {
        this.values = [value];
    }
    add(value) {
        this.values.push(value);
    }
    getValue() {
        return this.values[0];
    }
}

// Good - Use built-in features
let numbers = [5];
numbers.push(7);
let firstNumber = numbers[0];
```

```python
# Bad - Over-complicated
def is_even(n):
    return True if n % 2 == 0 else False

# Good - Direct and clear
def is_even(n):
    return n % 2 == 0
```

### Do
- Use language built-ins and standard libraries
- Choose clear, direct solutions
- Optimize only when profiling shows need
- Prefer composition of simple parts
- Write code for the current requirement

### Don't
- Create abstractions without clear benefit
- Add complexity for hypothetical future needs
- Use clever tricks that obscure intent
- Build custom solutions when standard ones exist

### AI Pitfalls
- Using classes or design patterns unnecessarily
- Creating abstractions for single-use code
- Over-complicating simple conditional logic
- Generating enterprise patterns for simple scripts

---

## DRY (Don't Repeat Yourself)

**Definition:** Eliminate duplicated code and logic. Every piece of knowledge should have a single, authoritative representation.

**Supported by:** *The Pragmatic Programmer*, *Clean Code*

### Examples

```python
# Bad - Duplicated logic
def circle_area(radius):
    return 3.14159 * radius * radius

def quarter_circle_area(radius):
    return 3.14159 * radius * radius / 4

def sphere_volume(radius):
    return (4/3) * 3.14159 * radius * radius * radius

# Good - Extracted constant and reused logic
PI = 3.14159

def circle_area(radius):
    return PI * radius ** 2

def quarter_circle_area(radius):
    return circle_area(radius) / 4

def sphere_volume(radius):
    return (4/3) * PI * radius ** 3
```

```javascript
// Bad - Repeated validation
function createUser(name, email) {
    if (!email.includes('@')) throw Error('Invalid email');
    // ...
}

function updateEmail(userId, email) {
    if (!email.includes('@')) throw Error('Invalid email');
    // ...
}

// Good - Extracted validation
function validateEmail(email) {
    if (!email.includes('@')) {
        throw Error('Invalid email');
    }
}

function createUser(name, email) {
    validateEmail(email);
    // ...
}

function updateEmail(userId, email) {
    validateEmail(email);
    // ...
}
```

### Do
- Extract common logic into functions
- Use constants for repeated values
- Abstract similar patterns
- Share code across modules appropriately
- Keep abstractions at the right level

### Don't
- Copy-paste code blocks
- Duplicate business rules
- Repeat validation logic
- Hard-code the same values multiple times
- Create premature abstractions (see Rule of Three)

### Rule of Three
Wait until you see duplication **three times** before abstracting. Two instances might be coincidental; three suggests a pattern.

### AI Pitfalls
- Producing repeated code structures from pattern prediction
- Duplicating similar functions instead of parameterizing
- Repeating validation or error handling logic
- Not recognizing when to extract shared utilities

---

## YAGNI (You Aren't Gonna Need It)

**Definition:** Don't implement features or infrastructure until you actually need them. Avoid speculative development.

**Supported by:** *The Pragmatic Programmer*, Extreme Programming (XP)

### Examples

```python
# Bad - Building for hypothetical futures
def process_order(order):
    prepare_invoice(order)
    apply_future_discount_system(order)  # Not used yet
    schedule_loyalty_rewards(order)       # Not needed now
    prepare_for_blockchain_audit(order)   # Speculative

# Good - Only what's needed now
def process_order(order):
    prepare_invoice(order)
    charge_payment(order)
    ship_order(order)
```

```javascript
// Bad - Over-engineered configuration
class DatabaseConfig {
    constructor() {
        this.primaryHost = 'localhost';
        this.replicaHosts = [];  // Not using replication
        this.shardingStrategy = null;  // Not sharding
        this.cacheLayer = null;  // No cache yet
    }
}

// Good - Current requirements only
class DatabaseConfig {
    constructor(host) {
        this.host = host;
    }
}
```

### Do
- Write code for current, known requirements
- Add features when they're actually requested
- Keep infrastructure minimal
- Refactor when new needs emerge
- Trust that future changes will be manageable

### Don't
- Build "just in case" features
- Create extensibility points without use cases
- Add configuration for hypothetical scenarios
- Implement features before they're specified

### AI Pitfalls
- Generating code for unspecified future features
- Adding unnecessary configuration options
- Creating extensibility hooks without current need
- Building infrastructure beyond MVP scope

---

## Premature Optimization

**Definition:** Don't optimize until you have evidence of a performance problem. Clarity and correctness come first.

**Supported by:** *The Pragmatic Programmer*, Donald Knuth's famous quote

> "Premature optimization is the root of all evil" — Donald Knuth

### Examples

```python
# Bad - Premature optimization
def find_user(user_id):
    # Using complex caching before knowing if it's needed
    cache_key = f"user:{user_id}:v2"
    if cache_key in cache:
        return deserialize(decompress(cache[cache_key]))
    user = db.query(user_id)
    cache[cache_key] = compress(serialize(user))
    return user

# Good - Start simple, optimize if needed
def find_user(user_id):
    return db.query(user_id)

# Later, if profiling shows this is slow:
def find_user(user_id):
    cached = cache.get(f"user:{user_id}")
    if cached:
        return cached
    user = db.query(user_id)
    cache.set(f"user:{user_id}", user)
    return user
```

### Do
- Write clear, correct code first
- Profile before optimizing
- Optimize only proven bottlenecks
- Measure impact of optimizations
- Document why optimizations were made

### Don't
- Sacrifice readability for unmeasured performance
- Optimize without profiling data
- Use complex algorithms for small datasets
- Cache everything "just in case"

### AI Pitfalls
- Adding caching layers without justification
- Using complex data structures for simple cases
- Micro-optimizing at the expense of clarity

---

## Summary

Simple code is:
- **Direct** - solves the problem at hand
- **DRY** - has no unnecessary duplication
- **Minimal** - contains only what's needed now
- **Clear** - prioritizes readability over premature optimization

When writing code, ask:
- Is this the simplest approach that works?
- Am I repeating myself?
- Do I actually need this now?
- Am I optimizing based on evidence?
