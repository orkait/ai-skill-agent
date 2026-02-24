# Negative Doubt Bias (Self-Verification)

## Purpose

**Actively seek ways the solution can fail** before finalizing.

This is a systematic routine to find bugs, edge cases, and flaws that optimistic reasoning misses.

## When to Run

**After producing any candidate solution, before finalizing.**

This applies to:
- Architecture designs
- Code implementations
- Refactoring plans
- API designs

## The Routine (8 Steps)

### Step 1: Fail-Seeking Pass

**Goal:** List concrete failure modes.

**Process:**
Generate 5 ways the solution can fail:
1. **Bugs** - Logic errors, off-by-one, null pointers
2. **Edge Cases** - Empty input, max values, special characters
3. **Performance** - O(n²) when n is large, memory leaks
4. **Security** - SQL injection, XSS, unauthorized access
5. **Maintainability** - Hard to change, tight coupling, unclear intent

**For each failure mode, produce a minimal counterexample:**

```python
# Solution: Calculate average
def average(numbers):
    return sum(numbers) / len(numbers)

# Fail-seeking:
# 1. Empty list → ZeroDivisionError
# 2. Non-numeric values → TypeError
# 3. Very large list → Memory overflow (unlikely but possible)
# 4. List with None values → TypeError in sum()
# 5. Integer division issues (Python 2) → Not applicable in Python 3

# Counterexamples:
average([])           # Fails: ZeroDivisionError
average([1, "two"])   # Fails: TypeError
average([1, None, 3]) # Fails: TypeError
```

### Step 2: Assumption Falsification

**Goal:** Challenge every assumption.

**Process:**
For each assumption:
1. Identify the assumption
2. Try to falsify it mentally
3. Find input/ordering/environment that breaks it

**Example:**

```python
def process_user(user):
    """
    Assumptions:
    1. user is not None
    2. user.email is a string
    3. user.email contains '@'
    4. Database is available
    """

# Falsification:
# Assumption 1: What if user=None? → Add guard
# Assumption 2: What if user.email=123? → Add type check
# Assumption 3: What if email="invalid"? → Add validation
# Assumption 4: What if DB is down? → Add retry/error handling

# Updated code:
def process_user(user):
    if user is None:
        raise ValueError("User cannot be None")
    if not isinstance(user.email, str):
        raise TypeError("Email must be string")
    if '@' not in user.email:
        raise ValueError("Invalid email format")
    
    try:
        save_to_db(user)
    except DatabaseError as e:
        log_error(e)
        raise ProcessingError("Failed to save user") from e
```

### Step 3: Invariant Check

**Goal:** Verify invariants are enforced.

**Process:**
For each declared invariant:
1. Check if code enforces it
2. Add guards if missing
3. Add tests to verify

**Example:**

```python
# Invariant: Order total must equal sum of item prices

class Order:
    def __init__(self, items):
        self.items = items
        self.total = self._calculate_total()
    
    def _calculate_total(self):
        return sum(item.price * item.quantity for item in self.items)
    
    def add_item(self, item):
        self.items.append(item)
        self.total = self._calculate_total()  # Enforce invariant
    
    def validate(self):
        # Runtime check
        expected = sum(item.price * item.quantity for item in self.items)
        if self.total != expected:
            raise InvariantViolation("Order total mismatch")
```

**Test invariant:**
```python
def test_order_total_matches_items():
    order = Order([Item(price=10, quantity=2)])
    assert order.total == 20
    
    order.add_item(Item(price=5, quantity=1))
    assert order.total == 25  # Invariant still holds
```

### Step 4: Dependency & Boundary Audit

**Goal:** Verify clean architecture.

**Checklist:**
- [ ] No circular dependencies introduced
- [ ] Module public surface is minimal
- [ ] Private internals not exposed
- [ ] Dependencies point in correct direction

**Process:**

**Draw dependency graph:**
```
Module A → Module B
         → Module C
Module C → Module D

Any cycles? (e.g., B → A)
If YES → Refactor to break cycle
```

**Check public API:**
```python
# user_service.py

# Public (should be exported)
def create_user(...): pass
def get_user(...): pass

# Private (should NOT be exported)
def _validate_email(...): pass
def _hash_password(...): pass
```

**If consumers reach internals:**
```python
# WRONG: Consumer importing private function
from user_service import _validate_email

# RIGHT: Add to public API or create facade
from validation import validate_email  # Moved to proper module
```

### Step 5: Simpler-Alternative Challenge

**Goal:** Find simpler solution that preserves behavior.

**Process:**
1. Attempt to rewrite in 2-5 lines
2. If successful and acceptable, prefer it
3. If not, document why complexity is needed

**Example:**

```python
# Original (10 lines)
class UserValidator:
    def __init__(self):
        self.rules = []
    
    def add_rule(self, rule):
        self.rules.append(rule)
    
    def validate(self, user):
        for rule in self.rules:
            rule.check(user)

# Simpler alternative (2 lines)
def validate_user(user, rules):
    for rule in rules:
        rule.check(user)

# Decision: Use simpler version unless:
# - Need to cache rules
# - Need to add/remove rules dynamically
# - Need stateful validation
```

**Document if keeping complexity:**
```python
# Using class instead of function because:
# - Rules need to be cached and reused
# - Validators compose with other validators
# - Need to maintain validation state across calls
```

### Step 6: Test Injection

**Goal:** Add tests for each failure mode.

**Process:**
For each failure mode from Step 1:
1. Write test that would fail before fix
2. Verify test fails
3. Fix code
4. Verify test passes

**Example:**

```python
# Failure mode: Empty list causes ZeroDivisionError

# Test (should fail initially)
def test_average_empty_list():
    with pytest.raises(ValueError):
        average([])

# Fix code
def average(numbers):
    if not numbers:
        raise ValueError("Cannot calculate average of empty list")
    return sum(numbers) / len(numbers)

# Now test passes
```

### Step 7: Decision Revision

**Goal:** Update design based on findings.

**Process:**
If Steps 1-6 found issues:
1. Update architecture
2. Update code
3. Update tests
4. **Run routine again** (one more iteration)

**Stopping Condition:**
- Routine finds no new issues, OR
- Issues are documented as known limitations

### Step 8: Negative Doubt Log

**Goal:** Document verification process.

**Template:**

```markdown
## Negative Doubt Log

### Failure Modes Discovered
1. Empty input causes ZeroDivisionError
2. Non-numeric values cause TypeError
3. Large lists may cause memory issues

### Tests Added
- test_average_empty_list()
- test_average_non_numeric()
- test_average_large_list() (performance test)

### Assumptions Changed
Before: Assumed input is always non-empty
After: Explicitly validate input or document precondition

### Design Changes
- Added input validation
- Added error handling
- Added defensive checks

### Remaining Issues
- Very large lists (>10M items) may be slow
  Decision: Document as known limitation, optimize if needed

### Final Status
✓ All critical issues addressed
⚠ Performance limitation documented
```

---

## Example: Complete Negative Doubt Routine

**Original Code:**
```python
def transfer_funds(from_account, to_account, amount):
    from_account.balance -= amount
    to_account.balance += amount
```

**Step 1: Fail-Seeking**
1. Insufficient funds → Negative balance
2. Concurrent transfers → Race condition
3. Non-existent accounts → AttributeError
4. Negative amount → Allows theft
5. Same account transfer → No-op but still processes

**Step 2: Assumption Falsification**
- Assumption: from_account.balance >= amount
  Falsified: What if balance < amount?
- Assumption: Accounts exist
  Falsified: What if from_account is None?

**Step 3: Invariant Check**
- Invariant: Total money in system stays constant
  Enforcement: Missing! Need transaction or rollback

**Step 4: Dependency Audit**
- Direct balance manipulation → Breaks encapsulation
- Should use account methods

**Step 5: Simpler Alternative**
```python
# No simpler alternative exists while preserving safety
# Complexity needed for atomicity and validation
```

**Step 6: Test Injection**
```python
def test_insufficient_funds():
    account = Account(balance=50)
    with pytest.raises(InsufficientFundsError):
        transfer_funds(account, other, 100)

def test_negative_amount():
    with pytest.raises(ValueError):
        transfer_funds(from_acc, to_acc, -50)
```

**Step 7: Revised Design**
```python
def transfer_funds(from_account, to_account, amount):
    if from_account is None or to_account is None:
        raise ValueError("Accounts cannot be None")
    if amount <= 0:
        raise ValueError("Amount must be positive")
    if from_account == to_account:
        return  # No-op
    if from_account.balance < amount:
        raise InsufficientFundsError()
    
    # Atomic transaction
    with transaction():
        from_account.withdraw(amount)
        to_account.deposit(amount)
```

**Step 8: Negative Doubt Log**
```
Failure Modes: 5 found, all addressed
Tests Added: 6 new tests
Assumptions Changed: Added explicit guards
Design Changes: Added transaction support, validation
Final Status: ✓ Ready
```

---

## Hard Stop Condition

**If any critical issue remains unaddressed:**

**DO NOT finalize.**

Return:
1. Revised design
2. Unmet requirements
3. Why they're unmet
4. What's needed to address them

**Example:**
```
HARD STOP

Issue: Race condition in concurrent transfers
Status: NOT ADDRESSED
Reason: Requires database-level locking or transaction isolation
Needed: Database transaction support or pessimistic locking
Recommendation: Do not deploy without addressing
```

---

## Summary

**Negative Doubt Bias is NOT optional.**

**Default stance:** Your solution has bugs. Find them.

Run this routine:
1. After every design
2. After every implementation
3. Before every review

**It's faster to find bugs now than in production.**

Pessimism in development = Reliability in production.
