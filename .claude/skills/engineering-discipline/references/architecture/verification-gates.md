# Verification Gates & Safety Checks

## Purpose

Systematic checkpoints that prevent common engineering failures. Each gate must pass before proceeding.

## Gate 0: Environment Verification

**Before any reasoning or code generation.**

### Checklist
- [ ] Runtime/language version specified
- [ ] Package manager identified
- [ ] Dependencies listed
- [ ] Build tool available
- [ ] Test framework present

### Actions

**If missing:**
```bash
# Example: Python project
python --version          # Check runtime
pip list                  # Check installed packages
cat requirements.txt      # Check dependencies
pytest --version          # Check test framework
```

**Do NOT proceed without:**
1. Verified runtime environment
2. Required dependencies installed or listed
3. Build/test tools available

**Output:**
```
Environment Status:
✓ Python 3.11
✓ Dependencies: requirements.txt present
✓ Test framework: pytest installed
✓ Proceed: YES
```

---

## Gate 1: Behavior Lock (Refactors Only)

**Trigger:** Any refactoring task

### Rule

**NO REFACTOR WITHOUT PASSING TESTS**

### Verification

```python
# Step 1: Run existing tests
pytest tests/

# Step 2: Verify they pass
# All tests green? → Proceed
# Tests fail? → Fix first, then refactor
# No tests? → Write tests first
```

### If No Tests Exist

**Write tests that lock current behavior:**

```python
# Test current behavior (even if ugly)
def test_current_user_creation():
    # Lock the current behavior
    user = create_user("Alice", "alice@example.com")
    assert user.name == "Alice"
    assert user.email == "alice@example.com"
    assert user.created_at is not None
```

**Then refactor:**
```python
# Refactor internals
# Tests still pass? Good.
# Tests fail? Rollback and fix.
```

### Anti-Pattern

```python
# WRONG: Refactoring without tests
"Let me clean this up..."
# Changes internal structure
# No tests to verify behavior preserved
# Introduces bugs silently
```

---

## Gate 2: Pattern Justification

**Trigger:** Using any design pattern

### Rule

**Use pattern ONLY if:**
1. The force it resolves is named
2. The invariant it protects is stated
3. Simpler alternatives were rejected

### Template

```
Pattern: [Factory | Strategy | Observer | etc.]

Force Resolved:
- [Specific problem this solves]

Invariant Protected:
- [What must remain true]

Alternatives Rejected:
- Simple function: [Why insufficient]
- [Other alternative]: [Why insufficient]

Justification:
- [Why this pattern is necessary]
```

### Example: Factory Pattern

```
Pattern: Factory

Force Resolved:
- Object creation logic varies by user type (free, premium, enterprise)
- Don't want to expose creation complexity to clients

Invariant Protected:
- All users must have valid email before creation
- Premium users must have payment method

Alternatives Rejected:
- Simple constructor: Insufficient - creation logic too complex
- Multiple constructors: Insufficient - doesn't enforce validation order

Justification:
- Factory centralizes validation and encapsulates creation complexity
```

### No Force → No Pattern

```python
# WRONG: Pattern without justification
class UserFactory:  # Why factory?
    def create(self, name):
        return User(name)  # Just a wrapper

# RIGHT: Simple function
def create_user(name):
    return User(name)
```

---

## Gate 3: Circular Dependency Check

**Trigger:** Adding new dependencies

### Verification

**Draw dependency graph:**
```
A → B → C
     ↓
     D

Is there a cycle? (A → B → ... → A)
If YES → STOP, redesign
If NO → Proceed
```

### Detection

```python
# WRONG: Circular dependency
# user_service.py
from order_service import OrderService

class UserService:
    def get_user_orders(self, user_id):
        return OrderService().get_orders(user_id)

# order_service.py
from user_service import UserService  # CIRCULAR!

class OrderService:
    def get_user_for_order(self, order_id):
        return UserService().get_user(...)
```

### Fix Strategies

**1. Extract common interface:**
```python
# models.py
class User:
    pass

class Order:
    pass

# user_service.py (depends on models)
# order_service.py (depends on models)
# No circular dependency
```

**2. Dependency Inversion:**
```python
# Define interface in high-level module
class IOrderRepository:
    def get_orders(self, user_id): pass

# Inject dependency
class UserService:
    def __init__(self, order_repo: IOrderRepository):
        self.orders = order_repo
```

---

## Gate 4: Public API Minimization

**Trigger:** Before finalizing module interface

### Rule

**Expose only what's necessary.**

### Checklist

- [ ] Every public function has clear purpose
- [ ] Private helpers are actually private
- [ ] No implementation leakage
- [ ] Public API is documented

### Example

```python
# user_service.py

# Public API (exported)
def create_user(name: str, email: str) -> User:
    """Create a new user account."""
    _validate_email(email)
    return _save_user(name, email)

# Private (not exported)
def _validate_email(email: str):
    if '@' not in email:
        raise ValueError("Invalid email")

def _save_user(name: str, email: str):
    # Implementation detail
    pass
```

### Anti-Pattern: Everything Public

```python
# WRONG: Exposing internals
class UserService:
    def create_user(self): pass
    def validate_email(self): pass  # Should be private
    def save_to_db(self): pass      # Should be private
    def format_name(self): pass     # Should be private
```

---

## Gate 5: Assumption Disclosure

**Trigger:** Before finalizing any design/code

### Rule

**All assumptions must be explicit.**

### Categories

**Input Assumptions:**
```python
def calculate_discount(price: float) -> float:
    """
    Assumptions:
    - price is positive
    - price is in USD
    - customer is authenticated
    """
```

**State Assumptions:**
```python
def ship_order(order: Order):
    """
    Assumptions:
    - order.payment_status == 'paid'
    - order.items is non-empty
    - order.shipping_address is valid
    """
```

**Ordering Assumptions:**
```python
def finalize_checkout():
    """
    Assumptions:
    - validate_cart() called first
    - process_payment() called before this
    """
```

**Environment Assumptions:**
```python
def upload_to_s3(file_path: str):
    """
    Assumptions:
    - AWS credentials configured
    - S3 bucket exists
    - Network connectivity available
    """
```

### Verification

Turn assumptions into **guards or tests:**

```python
def calculate_discount(price: float) -> float:
    # Guard against assumptions
    if price <= 0:
        raise ValueError("Price must be positive")
    if not is_authenticated():
        raise AuthError("User must be authenticated")
    
    return price * 0.9
```

---

## Gate 6: Test Coverage

**Trigger:** Before marking code complete

### Requirements

**For each function:**
- [ ] Happy path tested
- [ ] Edge cases tested
- [ ] Error cases tested

### Edge Cases to Test

```python
def divide(a: float, b: float) -> float:
    return a / b

# Tests needed:
# - Normal case: divide(10, 2) == 5
# - Zero divisor: divide(10, 0) → raises error
# - Negative numbers: divide(-10, 2) == -5
# - Very large numbers: divide(1e100, 1e50)
# - Very small numbers: divide(0.0001, 0.0002)
```

### Coverage is NOT Enough

```python
# 100% coverage, but bad test
def test_add():
    add(2, 3)  # No assertion! Test passes but verifies nothing
```

**Good test:**
```python
def test_add_returns_sum():
    result = add(2, 3)
    assert result == 5
```

---

## Gate 7: Code Generation Rules

**Trigger:** When writing implementation

### Rules

**Deletion over Abstraction:**
```python
# Prefer deleting unused code
# over abstracting "just in case"
```

**No Generic Folders:**
```python
# WRONG
utils/
common/
shared/
helpers/

# RIGHT
validation/
authentication/
formatting/
```

**One Reason to Change:**
```python
# user_manager.py
# ✓ Changes when user management logic changes
# ✗ Changes when email logic, DB logic, AND user logic change
```

**Explicit Public API:**
```python
# __init__.py
from .user_service import create_user, get_user
# Only these are public
```

**Flat over Deep:**
```python
# WRONG: Excessive nesting
src/features/users/services/implementations/user_service_impl.py

# RIGHT: Flat structure
src/users/user_service.py
```

**No Global State Without Justification:**
```python
# WRONG: Hidden global state
_cached_users = {}  # Who manages this? When is it invalidated?

# RIGHT: Explicit state management
class UserCache:
    def __init__(self):
        self._cache = {}
    
    def get(self, user_id):
        return self._cache.get(user_id)
```

---

## Gate Enforcement Checklist

Before finalizing any work:

- [ ] **Gate 0:** Environment verified
- [ ] **Gate 1:** Tests pass (if refactoring)
- [ ] **Gate 2:** Patterns justified
- [ ] **Gate 3:** No circular dependencies
- [ ] **Gate 4:** Public API minimal
- [ ] **Gate 5:** Assumptions disclosed
- [ ] **Gate 6:** Tests cover edge cases
- [ ] **Gate 7:** Code generation rules followed

**Any gate fails → Stop and fix.**

---

## Summary

Gates are **hard stops**, not suggestions.

Bypassing gates leads to:
- Broken refactors (no tests)
- Over-engineered code (unjustified patterns)
- Tangled dependencies (circular refs)
- Brittle APIs (exposed internals)
- Hidden bugs (undisclosed assumptions)

**Respect the gates.**
