# Maintainability & Best Practices

## Boy Scout Rule

**Definition:** "Leave the code better than you found it." Make small improvements whenever you touch existing code.

**Supported by:** *Clean Code*, *The Pragmatic Programmer*

### Examples

```python
# Before - Existing code you're modifying
def calc(a, b):
    return a + b

# After - Improved while making your change
def calculate_sum(a, b):
    """Return the sum of two numbers."""
    return a + b
```

```python
# Before - Adding a feature to messy code
def processUser(u):
    # Check age
    if u.age<18:return False
    db.save(u)
    return True

# After - Clean up while you're here
def process_user(user):
    """Register an eligible user."""
    if not is_eligible_user(user):
        return False
    save_user(user)
    return True

def is_eligible_user(user):
    return user.age >= 18
```

### Do
- Improve variable names
- Extract magic numbers to constants
- Add missing docstrings
- Fix formatting inconsistencies
- Remove dead code
- Simplify complex conditions

### Don't
- Make unrelated large refactors
- Change behavior without tests
- Add hacks or workarounds
- Ignore obvious issues ("not my code")

### AI Pitfalls
- Regenerating dirty code without improvements
- Not suggesting cleanup opportunities
- Adding to technical debt instead of reducing it

---

## Continuous Refactoring

**Definition:** Improve code structure regularly through small, safe changes backed by tests. Refactoring should be ongoing, not a separate phase.

**Supported by:** *Refactoring*, *Code Complete*, *Clean Code*

### Common Refactorings

**Extract Method**
```python
# Before
def process_order(order):
    # Validate
    if not order.items:
        raise ValueError("Empty order")
    
    # Calculate total
    total = 0
    for item in order.items:
        total += item.price * item.quantity
    
    # Apply discount
    if order.customer.is_premium:
        total *= 0.9
    
    return total

# After
def process_order(order):
    validate_order(order)
    total = calculate_total(order)
    return apply_discount(total, order.customer)

def validate_order(order):
    if not order.items:
        raise ValueError("Empty order")

def calculate_total(order):
    return sum(item.price * item.quantity for item in order.items)

def apply_discount(total, customer):
    if customer.is_premium:
        return total * 0.9
    return total
```

**Extract Variable**
```python
# Before
if (user.age >= 18 and user.has_verified_email and user.account_status == 'active'):
    grant_access()

# After
is_adult = user.age >= 18
has_verified_email = user.has_verified_email
is_active = user.account_status == 'active'

if is_adult and has_verified_email and is_active:
    grant_access()
```

**Rename**
```python
# Before
def fn(x, y):
    return x * y

# After
def calculate_area(width, height):
    return width * height
```

**Replace Magic Numbers**
```python
# Before
def calculate_price(quantity):
    if quantity > 100:
        return quantity * 9.99 * 0.85
    return quantity * 9.99

# After
UNIT_PRICE = 9.99
BULK_DISCOUNT = 0.85
BULK_THRESHOLD = 100

def calculate_price(quantity):
    price = quantity * UNIT_PRICE
    if quantity > BULK_THRESHOLD:
        price *= BULK_DISCOUNT
    return price
```

### Refactoring Workflow

1. **Ensure tests pass** - Start with green tests
2. **Make one change** - Small, focused refactor
3. **Run tests** - Verify behavior unchanged
4. **Commit** - Save working state
5. **Repeat** - Iterate on improvements

### Do
- Refactor in small steps
- Run tests after each change
- Commit frequently
- Use IDE refactoring tools
- Keep behavior identical

### Don't
- Refactor without tests
- Mix refactoring with feature work
- Make multiple changes at once
- Skip running tests
- Delay commits

### AI Pitfalls
- Suggesting large refactors without incremental steps
- Omitting test runs between changes
- Changing behavior during refactoring

---

## Version Control & Incremental Work

**Definition:** Commit code in logical, testable chunks. Each commit should represent a complete, working unit of change.

**Supported by:** *Refactoring*, *The Pragmatic Programmer*, Agile practices

### Good Commit Practices

**Atomic Commits**
```
✓ "Add user email validation"
✓ "Extract payment processing to service"
✓ "Fix off-by-one error in pagination"

✗ "Fixed stuff"
✗ "WIP"
✗ "Updated files"
```

**Commit Messages**
```
# Good - Imperative mood, clear intent
Add password strength validation

Implement validation rules:
- Minimum 8 characters
- At least one uppercase letter
- At least one number
- At least one special character

Closes #123

# Bad
fixed login
```

### Commit Workflow

```bash
# 1. Make a focused change
# 2. Run tests
pytest

# 3. Review changes
git diff

# 4. Stage related files
git add user_validator.py tests/test_validator.py

# 5. Commit with clear message
git commit -m "Add email format validation"

# 6. Repeat for next logical change
```

### Do
- Commit working, tested code
- Write descriptive commit messages
- Keep commits focused and atomic
- Use branches for features
- Commit frequently

### Don't
- Commit broken code
- Mix unrelated changes in one commit
- Skip commit messages
- Commit sensitive data (API keys, passwords)
- Leave uncommitted changes overnight

### AI Pitfalls
- Generating large changes without guiding commit boundaries
- Not suggesting logical commit points
- Creating code that can't be committed incrementally

---

## Code Reviews

**Definition:** Systematic examination of code changes by peers to catch issues, share knowledge, and maintain quality.

### Review Checklist

**Correctness**
- Does it solve the stated problem?
- Are edge cases handled?
- Is error handling appropriate?
- Are there off-by-one errors or race conditions?

**Design**
- Is it in the right place?
- Does it follow existing patterns?
- Is complexity warranted?
- Could it be simpler?

**Readability**
- Are names clear?
- Is logic easy to follow?
- Are comments helpful (not redundant)?
- Is formatting consistent?

**Testing**
- Are tests included?
- Do tests cover edge cases?
- Are tests readable and maintainable?

**Security**
- Is input validated?
- Are secrets hardcoded?
- Are SQL queries parameterized?
- Is authentication/authorization correct?

### Review Etiquette

**As Reviewer**
```
✓ "Consider extracting this to a helper function for reusability"
✓ "Could we add a test for the empty list case?"
✓ "This is clever! Can we add a comment explaining the algorithm?"

✗ "This is terrible"
✗ "Why didn't you just..."
✗ "Obviously this is wrong"
```

**As Author**
- Respond to all feedback
- Ask for clarification
- Explain non-obvious decisions
- Be open to suggestions
- Thank reviewers

### Do
- Review promptly
- Focus on substance over style
- Suggest improvements, don't demand
- Automate style checks
- Learn from reviews you receive

### Don't
- Approve without reading
- Nitpick trivial issues
- Review your own PRs
- Take criticism personally
- Skip review for "small" changes

---

## Automation and Tooling

**Definition:** Automate repetitive tasks and use tools to maintain consistency and quality.

**Supported by:** *The Pragmatic Programmer*, *Clean Code*

### Essential Tools

**Linters** - Catch common mistakes
```bash
# Python
pylint myapp/
flake8 myapp/

# JavaScript
eslint src/

# Go
golangci-lint run
```

**Formatters** - Maintain consistent style
```bash
# Python
black myapp/

# JavaScript
prettier --write src/

# Rust
rustfmt src/
```

**Type Checkers** - Catch type errors
```bash
# Python
mypy myapp/

# TypeScript
tsc --noEmit

# Flow
flow check
```

**Test Runners** - Verify behavior
```bash
# Python
pytest

# JavaScript
jest

# Go
go test ./...
```

### Continuous Integration

```yaml
# .github/workflows/ci.yml
name: CI
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Lint
        run: flake8 .
      - name: Type check
        run: mypy .
      - name: Test
        run: pytest --cov
      - name: Security scan
        run: bandit -r .
```

### Pre-commit Hooks

```bash
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    hooks:
      - id: black
  - repo: https://github.com/pycqa/flake8
    hooks:
      - id: flake8
  - repo: https://github.com/pre-commit/pre-commit-hooks
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
```

### Do
- Integrate tools into workflow
- Run checks locally before pushing
- Fail builds on violations
- Configure tools consistently
- Update tools regularly

### Don't
- Rely on manual checks
- Ignore tool warnings
- Skip tools for "quick fixes"
- Disable checks without good reason

### AI Pitfalls
- Producing code that doesn't pass linting
- Ignoring type annotations
- Generating code incompatible with project tools

---

## Documentation

**Definition:** Provide context and explanations where code alone isn't sufficient.

### What to Document

**APIs and Public Interfaces**
```python
def calculate_shipping_cost(weight_kg: float, destination: str) -> float:
    """Calculate shipping cost based on weight and destination.
    
    Args:
        weight_kg: Package weight in kilograms (must be positive)
        destination: ISO 3166-1 alpha-2 country code
    
    Returns:
        Shipping cost in USD
    
    Raises:
        ValueError: If weight is negative or destination is invalid
    
    Example:
        >>> calculate_shipping_cost(2.5, 'US')
        12.50
    """
```

**Complex Algorithms**
```python
def dijkstra(graph, start):
    """Find shortest paths using Dijkstra's algorithm.
    
    Time complexity: O((V + E) log V) where V is vertices, E is edges
    Space complexity: O(V)
    
    See: https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm
    """
```

**Non-Obvious Decisions**
```python
# Using MD5 for cache keys only - NOT for security
# MD5 is fast and collision-resistant enough for this use case
cache_key = hashlib.md5(url.encode()).hexdigest()
```

**Setup and Configuration**
```markdown
# README.md

## Installation

pip install -r requirements.txt

## Configuration

Set environment variables:
- `DATABASE_URL`: PostgreSQL connection string
- `API_KEY`: Third-party service API key

## Running

python app.py
```

### Don't Document

- Obvious code (let code be self-documenting)
- Implementation details that change frequently
- Duplicated information available elsewhere

### Do
- Keep docs close to code
- Update docs with code changes
- Use examples liberally
- Link to external references

### Don't
- Let docs become stale
- Over-document simple code
- Duplicate info across files

---

## Summary

Maintainable code:
- **Improves incrementally** - Boy Scout Rule
- **Refactors continuously** - Small, safe improvements
- **Commits logically** - Atomic, tested changes
- **Automates quality** - Linters, formatters, CI/CD
- **Documents appropriately** - Context where needed

When maintaining code, ask:
- Can I improve this while I'm here?
- Is this change small and safe?
- Should I commit now?
- Are my tools catching issues?
- Does this need documentation?
