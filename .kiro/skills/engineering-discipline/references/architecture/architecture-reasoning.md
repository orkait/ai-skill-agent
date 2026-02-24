# Architecture-First Reasoning

## Core Principle

**Think in layers of abstraction before writing syntax.**

Code is the final output of architectural decisions, not the starting point.

## The Reasoning Ladder (Never Skip Steps)

### 1. Responsibilities

**Question:** What does this component *do*?

Define in terms of:
- Domain concepts (User, Order, Payment)
- Actions (authenticate, validate, process)
- Boundaries (what it does NOT do)

**Example:**
```
UserService responsibilities:
✓ Create user accounts
✓ Authenticate users
✓ Update user profiles
✗ Send emails (NotificationService)
✗ Store data (UserRepository)
```

**Anti-Pattern:** Defining by implementation ("uses database", "calls API")

### 2. Invariants

**Question:** What must *always* be true?

**Types of Invariants:**

**State Invariants:**
```python
# User age must be 0-150
assert 0 <= user.age <= 150

# Order total must equal sum of items
assert order.total == sum(item.price * item.qty for item in order.items)
```

**Ordering Invariants:**
```python
# Payment must occur before shipping
assert order.payment_status == 'paid' before order.ship()
```

**Input Invariants:**
```python
# Email must contain @ symbol
assert '@' in email
```

**Document Early:** Write invariants before code.

### 3. Dependency Direction

**Question:** What depends on what?

**Rules:**
- High-level modules depend on abstractions, not implementations
- Dependencies point inward (toward domain core)
- No circular dependencies

**Dependency Graph Example:**
```
Controller → Service → Repository
    ↓
  DTO/Model
    
NOT:
Repository → Service (wrong direction)
Service ←→ Controller (circular)
```

**Test:** Can you replace a dependency without changing dependents?

### 4. Module Boundaries

**Question:** What is public vs private?

**Public API:**
- Exported functions/classes
- Documented contracts
- Stable interfaces

**Private Implementation:**
- Internal helpers
- Implementation details
- Subject to change

**Example:**
```python
# user_service.py (public API)
def create_user(name: str, email: str) -> User:
    """Public: Create a new user"""
    _validate_email(email)  # private
    return _persist_user(name, email)  # private

# Private helpers (not exported)
def _validate_email(email: str):
    ...

def _persist_user(name: str, email: str):
    ...
```

### 5. Public APIs

**Question:** How do consumers interact with this?

**API Design Checklist:**
- [ ] Clear function names (verbs for actions)
- [ ] Typed parameters (what goes in)
- [ ] Typed returns (what comes out)
- [ ] Error cases documented
- [ ] Idempotency specified (if relevant)
- [ ] Side effects stated

**Example:**
```python
def transfer_funds(
    from_account: AccountId,
    to_account: AccountId,
    amount: Decimal
) -> TransferResult:
    """
    Transfer funds between accounts.
    
    Returns:
        TransferResult with transaction ID
    
    Raises:
        InsufficientFundsError: If from_account balance < amount
        AccountNotFoundError: If either account doesn't exist
        
    Side Effects:
        - Debits from_account
        - Credits to_account
        - Creates transaction record
        
    Idempotency: Safe to retry with same parameters
    """
```

### 6. Folder Structure

**Question:** How is code organized on disk?

**Principles:**
- Structure reflects architecture
- Co-locate related files
- Separate by layer or domain (choose one)

**By Layer:**
```
src/
├── controllers/
├── services/
├── repositories/
└── models/
```

**By Domain (Preferred for larger systems):**
```
src/
├── users/
│   ├── user_controller.py
│   ├── user_service.py
│   ├── user_repository.py
│   └── user_model.py
├── orders/
│   ├── order_controller.py
│   ├── order_service.py
│   └── ...
```

**Anti-Patterns:**
- `utils/` (too vague)
- `common/` (unclear ownership)
- `shared/` (becomes dumping ground)

If you need shared code:
- Create specific modules: `validation/`, `auth/`, `formatting/`

### 7. Files

**Question:** What goes in each file?

**One Reason to Change:**
```
✓ user_repository.py    (changes when data access changes)
✓ user_validator.py     (changes when validation rules change)

✗ user_helpers.py       (changes for multiple unrelated reasons)
```

**Naming:**
- Nouns for classes: `UserRepository`, `PaymentProcessor`
- Verbs for modules: `authenticate.py`, `validate.py`

### 8. Functions

**Question:** What are the atomic operations?

**Function Design:**
- Single responsibility
- One level of abstraction
- Clear inputs/outputs
- Minimal side effects

**Abstraction Levels:**
```python
# High level (orchestration)
def process_order(order):
    validate_order(order)
    charge_payment(order)
    ship_order(order)
    send_confirmation(order)

# Mid level (business logic)
def validate_order(order):
    check_inventory(order.items)
    verify_address(order.shipping_address)

# Low level (implementation)
def check_inventory(items):
    for item in items:
        if stock[item.id] < item.quantity:
            raise OutOfStockError(item)
```

**Don't mix levels:**
```python
# Bad - mixing levels
def process_order(order):
    # High level
    validate_order(order)
    # Low level - doesn't belong here
    for item in order.items:
        if stock[item.id] < item.quantity:
            raise OutOfStockError(item)
```

### 9. Syntax

**Question:** How is this expressed in code?

**Only now** do you write actual implementation.

If you start here, you'll build the wrong thing correctly.

## Reasoning Example: Payment System

**1. Responsibilities**
- PaymentService: Process payments
- PaymentGateway: Communicate with external processor
- PaymentRepository: Store payment records

**2. Invariants**
- Payment amount must be positive
- Payment must have valid payment method
- Payment cannot be processed twice (idempotency)

**3. Dependency Direction**
```
PaymentController → PaymentService → PaymentGateway (interface)
                                   → PaymentRepository
```

**4. Module Boundaries**
- Public: `PaymentService.process_payment()`
- Private: Gateway communication details, retry logic

**5. Public API**
```python
def process_payment(
    amount: Decimal,
    payment_method: PaymentMethod
) -> PaymentResult
```

**6. Folder Structure**
```
payments/
├── payment_service.py
├── payment_gateway.py
├── payment_repository.py
└── payment_models.py
```

**7. Files**
- `payment_service.py` - Business logic
- `payment_gateway.py` - External integration
- `payment_repository.py` - Data persistence

**8. Functions**
```python
def process_payment(...)
def validate_payment_method(...)
def charge_payment_gateway(...)
def record_payment(...)
```

**9. Syntax**
*Now* write the Python code.

## Forcing Function: Can You Answer These?

Before writing code, answer:

1. **What responsibilities does each component have?**
2. **What invariants must hold?**
3. **What depends on what? (Draw the graph)**
4. **What's public vs private?**
5. **How do consumers use this?**
6. **Where does this live in the folder structure?**
7. **What files exist and why?**
8. **What functions are needed?**

If any answer is "I don't know" → **Stop. Don't guess.**

## Anti-Pattern: Bottom-Up Thinking

```python
# Wrong: Starting with syntax
def process_payment(amount, method):
    # Wait, what should this do?
    # Who calls this?
    # What if amount is negative?
    # Where does this go?
```

## Correct: Top-Down Thinking

1. Responsibility: Process payment transactions
2. Invariant: amount > 0, method is valid
3. Depends on: PaymentGateway, PaymentRepository
4. Public API: `process_payment(amount, method) -> result`
5. Returns: Success/failure with transaction ID
6. Now write the code

## Verification Questions

After designing, ask:

- **Can I explain this to a team member?**
- **Are dependencies testable/mockable?**
- **Can I change implementation without breaking consumers?**
- **Is the folder structure obvious?**
- **Would a new developer know where to add features?**

If "no" to any → redesign before coding.

## Summary

**Architecture First = Correctness**

Syntax is cheap. Wrong architecture is expensive.

Spend time thinking before writing.

**Ladder Enforcement:**
```
Responsibilities → Invariants → Dependencies → Boundaries → APIs → 
Folders → Files → Functions → Syntax
```

Skip a step = wrong design.
