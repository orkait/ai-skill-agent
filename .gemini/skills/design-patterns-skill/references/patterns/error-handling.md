# Error Handling & Input Validation

## Handle Errors Clearly

**Definition:** Use exceptions for unexpected states and provide clear error messages. Fail early and explicitly rather than allowing silent failures.

**Supported by:** *Code Complete*, *Clean Code*, *The Pragmatic Programmer*

### Examples

```python
# Bad - Silent failure
def divide(a, b):
    if b == 0:
        return None  # Caller has to check for None
    return a / b

# Good - Explicit error
def divide(a, b):
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b
```

```python
# Bad - Vague error message
def process_user(user):
    if not user:
        raise Exception("Error")

# Good - Descriptive error message
def process_user(user):
    if user is None:
        raise ValueError("User object cannot be None")
    if not user.email:
        raise ValueError(f"User {user.id} must have a valid email address")
```

### Do
- Use exceptions for exceptional conditions
- Provide descriptive error messages
- Include context (what failed, why, what was expected)
- Fail fast - validate inputs early
- Use specific exception types
- Document what exceptions can be raised

### Don't
- Return None or -1 as error codes
- Swallow exceptions silently
- Use exceptions for control flow
- Provide generic error messages ("Error occurred")
- Catch exceptions you can't handle

### AI Pitfalls
- Skipping edge-case validation
- Empty except blocks: `except: pass`
- Returning default values instead of raising errors
- Generic exception types instead of specific ones

---

## Validate Inputs Early

**Definition:** Check preconditions at the entry point of functions. Reject invalid input before processing.

**Supported by:** *Code Complete*, *Clean Code*

### Examples

```python
# Bad - Late validation, partial processing
def register_user(username, email, age):
    user = User(username, email, age)
    save_to_database(user)
    if age < 18:  # Too late - already saved!
        raise ValueError("User must be 18 or older")

# Good - Early validation
def register_user(username, email, age):
    if not username or len(username) < 3:
        raise ValueError("Username must be at least 3 characters")
    if not email or '@' not in email:
        raise ValueError("Invalid email address")
    if age < 18:
        raise ValueError("User must be 18 or older")
    
    user = User(username, email, age)
    save_to_database(user)
```

### Guard Clauses

Use guard clauses to validate and exit early:

```python
# Bad - Nested conditions
def process_order(order):
    if order is not None:
        if order.items:
            if order.total > 0:
                # Main logic here
                charge_payment(order)
                ship_order(order)

# Good - Guard clauses
def process_order(order):
    if order is None:
        raise ValueError("Order cannot be None")
    if not order.items:
        raise ValueError("Order must contain at least one item")
    if order.total <= 0:
        raise ValueError("Order total must be positive")
    
    # Main logic - no nesting
    charge_payment(order)
    ship_order(order)
```

### Do
- Validate at function entry
- Use guard clauses to reduce nesting
- Check preconditions explicitly
- Validate types and ranges
- Use type hints and runtime validation

### Don't
- Defer validation until deep in the logic
- Assume inputs are valid
- Mix validation with business logic

---

## Exception Hierarchy

**Definition:** Use specific exception types to allow targeted error handling.

### Examples

```python
# Bad - Generic exceptions
def fetch_user(user_id):
    if user_id < 0:
        raise Exception("Invalid ID")
    user = db.get(user_id)
    if not user:
        raise Exception("Not found")
    return user

# Good - Specific exceptions
class InvalidUserIdError(ValueError):
    pass

class UserNotFoundError(LookupError):
    pass

def fetch_user(user_id):
    if user_id < 0:
        raise InvalidUserIdError(f"User ID must be positive, got {user_id}")
    user = db.get(user_id)
    if not user:
        raise UserNotFoundError(f"User with ID {user_id} not found")
    return user

# Caller can handle specifically
try:
    user = fetch_user(user_id)
except InvalidUserIdError as e:
    return {"error": "bad_request", "message": str(e)}
except UserNotFoundError as e:
    return {"error": "not_found", "message": str(e)}
```

### Do
- Create custom exception classes for domain errors
- Inherit from appropriate built-in exceptions
- Use exception hierarchies for related errors
- Document exception types in docstrings

### Don't
- Raise generic `Exception` or `RuntimeError`
- Create exceptions for every possible error
- Use exceptions for non-exceptional cases

---

## Error Recovery Strategies

### Retry with Backoff

```python
import time

def fetch_with_retry(url, max_attempts=3):
    for attempt in range(max_attempts):
        try:
            return http.get(url)
        except TransientError as e:
            if attempt == max_attempts - 1:
                raise
            wait_time = 2 ** attempt  # Exponential backoff
            time.sleep(wait_time)
```

### Fallback Mechanisms

```python
def get_user_avatar(user_id):
    try:
        return cdn.fetch_avatar(user_id)
    except CDNError:
        # Fallback to default avatar
        return DEFAULT_AVATAR_URL
```

### Circuit Breaker

```python
class CircuitBreaker:
    def __init__(self, failure_threshold=5):
        self.failure_count = 0
        self.threshold = failure_threshold
        self.state = "closed"  # closed, open, half-open
    
    def call(self, func, *args):
        if self.state == "open":
            raise CircuitOpenError("Service is temporarily unavailable")
        
        try:
            result = func(*args)
            self.on_success()
            return result
        except Exception as e:
            self.on_failure()
            raise
    
    def on_success(self):
        self.failure_count = 0
        self.state = "closed"
    
    def on_failure(self):
        self.failure_count += 1
        if self.failure_count >= self.threshold:
            self.state = "open"
```

---

## Logging vs. Exceptions

**Definition:** Log for diagnostics, use exceptions for control flow.

### When to Log

```python
# Log operational info
logger.info(f"Processing order {order_id}")

# Log warnings for recoverable issues
logger.warning(f"Slow query detected: {duration}ms")

# Log errors with context
try:
    process_payment(order)
except PaymentError as e:
    logger.error(f"Payment failed for order {order.id}", exc_info=True)
    raise  # Re-raise after logging
```

### When to Raise Exceptions

```python
# Invalid input - exception
def set_age(age):
    if age < 0 or age > 150:
        raise ValueError(f"Invalid age: {age}")

# Business rule violation - exception
def withdraw(account, amount):
    if account.balance < amount:
        raise InsufficientFundsError(f"Balance: {account.balance}, requested: {amount}")

# Operational issue - log + exception
def connect_to_database():
    try:
        return db.connect()
    except ConnectionError as e:
        logger.error("Database connection failed", exc_info=True)
        raise DatabaseUnavailableError("Cannot connect to database") from e
```

### Do
- Log context before re-raising
- Include exception traceback in logs
- Use structured logging for searchability
- Set appropriate log levels

### Don't
- Log and swallow exceptions
- Log sensitive data (passwords, tokens)
- Over-log routine operations

---

## Error Messages Best Practices

### Good Error Messages

**What went wrong:**
```
"Invalid email address: 'user@domain' - missing top-level domain"
```

**What was expected:**
```
"Order total must be positive, got -50.00"
```

**How to fix it:**
```
"File not found: '/data/input.csv'. Check that the file exists and path is correct."
```

**Actionable context:**
```
"User authentication failed: Invalid API key. Please check your credentials in the dashboard."
```

### Bad Error Messages

```
"Error"  # Too vague
"Something went wrong"  # Unhelpful
"Invalid input"  # Missing details
"Error code: 42"  # No explanation
```

### Do
- Explain what failed and why
- Include actual vs. expected values
- Suggest corrective actions
- Avoid technical jargon for user-facing errors
- Use clear, plain language

### Don't
- Expose internal implementation details to end users
- Include stack traces in user-facing messages
- Use codes without explanations
- Be condescending ("You entered invalid data")

---

## Summary

Effective error handling:
- **Fails fast** - Validates early and explicitly
- **Provides clarity** - Error messages explain what and why
- **Uses exceptions correctly** - For exceptional conditions only
- **Enables recovery** - Appropriate retry and fallback strategies

When handling errors, ask:
- Have I validated all inputs?
- Will the error message help someone fix the issue?
- Am I using the right exception type?
- Should this be logged, raised, or both?
