# Testing & Quality Principles

## Write Automated Tests Early

**Definition:** Use tests to guide design, prevent regressions, and validate behavior. Testing should be part of the development process, not an afterthought.

**Supported by:** *Refactoring*, *The Pragmatic Programmer*, Test-Driven Development (TDD)

### Examples

```python
# Test-first approach
def test_calculate_discount():
    # Arrange
    price = 100
    discount_percent = 10
    
    # Act
    result = calculate_discount(price, discount_percent)
    
    # Assert
    assert result == 90

def calculate_discount(price, discount_percent):
    return price * (1 - discount_percent / 100)
```

```python
# Test edge cases
def test_user_age_validation():
    assert is_adult(18) == True
    assert is_adult(17) == False
    assert is_adult(0) == False
    assert is_adult(150) == True  # No upper bound check yet
    
def is_adult(age):
    return age >= 18
```

### Do
- Write tests before or alongside code
- Test edge cases and boundary conditions
- Test business logic thoroughly
- Use descriptive test names
- Keep tests fast and independent
- Use test fixtures and setup/teardown appropriately

### Don't
- Skip tests for "simple" code
- Test implementation details instead of behavior
- Write brittle tests that break on refactoring
- Ignore failing tests
- Write tests that depend on external state

### AI Pitfalls
- Missing tests entirely
- Writing overly broad test functions
- Not testing edge cases or error paths
- Creating tests with vague assertions

---

## One Assert Per Test (Focus)

**Definition:** Keep tests focused on a single behavior or scenario. This makes failures easy to diagnose.

**Supported by:** *Clean Code*, TDD best practices

### Examples

```python
# Bad - Multiple unrelated assertions
def test_user():
    user = User("Alice", 25)
    assert user.name == "Alice"
    assert user.age == 25
    assert user.is_adult() == True
    assert user.can_vote() == True
    assert user.get_greeting() == "Hello, Alice"

# Good - Focused tests
def test_user_name_is_set_correctly():
    user = User("Alice", 25)
    assert user.name == "Alice"

def test_user_age_is_set_correctly():
    user = User("Alice", 25)
    assert user.age == 25

def test_user_is_adult_when_age_18_or_above():
    user = User("Alice", 25)
    assert user.is_adult() == True

def test_user_is_not_adult_when_age_below_18():
    user = User("Bob", 17)
    assert user.is_adult() == False
```

### Guideline Exceptions

Multiple assertions are acceptable when:
- Testing object state after a single operation
- Verifying related properties of one concept
- Testing list/collection contents

```python
# Acceptable - Related assertions on same concept
def test_order_creation():
    order = Order(items=[item1, item2])
    assert len(order.items) == 2
    assert order.total == 50.00
    assert order.status == OrderStatus.PENDING
```

### Do
- Use test names to describe expected behavior
- Group related tests in test classes
- Use parametrized tests for similar scenarios
- Make test intent crystal clear

### Don't
- Group many checks together
- Test multiple behaviors in one test
- Create generic test names like `test_user()`

### AI Pitfalls
- Combining multiple assertions in one test function
- Creating catch-all test functions
- Not using descriptive test names

---

## Test Coverage Guidelines

**Definition:** Aim for meaningful coverage of critical paths, not just high percentages. Focus on business logic, edge cases, and failure modes.

### What to Test

**High Priority:**
- Business logic and algorithms
- Input validation and error handling
- State transitions
- Integration points
- Security-critical code

**Medium Priority:**
- Data transformations
- Configuration handling
- User-facing features

**Low Priority:**
- Trivial getters/setters
- Framework-generated code
- External library wrappers

### Coverage Anti-Patterns

```python
# Bad - Testing for coverage, not correctness
def test_add():
    add(2, 3)  # No assertion!

# Good - Test actual behavior
def test_add_returns_sum():
    result = add(2, 3)
    assert result == 5
```

### Do
- Focus on critical code paths
- Test public interfaces, not private methods
- Use code coverage as a guide, not a goal
- Write tests that catch real bugs

### Don't
- Aim for 100% coverage blindly
- Test trivial code just for metrics
- Ignore untested critical paths

---

## Test Pyramid

**Definition:** Balance different types of tests - many unit tests, fewer integration tests, even fewer end-to-end tests.

```
       /\
      /  \     Few E2E tests (slow, brittle)
     /____\
    /      \   More integration tests (moderate speed)
   /________\
  /          \ Many unit tests (fast, isolated)
```

### Unit Tests
- Test individual functions/classes in isolation
- Fast execution (milliseconds)
- Mock external dependencies
- High count (hundreds to thousands)

### Integration Tests
- Test interactions between components
- Moderate speed (seconds)
- Use real dependencies where practical
- Medium count (dozens to hundreds)

### End-to-End Tests
- Test complete user workflows
- Slow execution (minutes)
- Test through actual UI/API
- Low count (handful to dozens)

### Do
- Rely primarily on unit tests
- Use integration tests for critical paths
- Reserve E2E tests for key user journeys

### Don't
- Over-rely on E2E tests
- Skip unit tests in favor of integration tests
- Test everything through the UI

---

## Test Quality Checklist

Good tests are:

- **Fast** - Run in milliseconds
- **Isolated** - No shared state or order dependency
- **Repeatable** - Same result every time
- **Self-validating** - Pass/fail is clear
- **Timely** - Written close to code

### Do
- Use test fixtures for setup
- Clean up resources in teardown
- Use meaningful test data
- Avoid test interdependence

### Don't
- Rely on external services without mocks
- Use production data
- Write flaky tests
- Commit commented-out tests

---

## Mocking & Test Doubles

**Definition:** Use test doubles (mocks, stubs, fakes) to isolate the code under test.

### Types of Test Doubles

**Stub** - Returns canned responses
```python
class StubPaymentGateway:
    def charge(self, amount):
        return {"status": "success", "transaction_id": "123"}
```

**Mock** - Verifies interactions
```python
def test_order_charges_payment():
    mock_gateway = Mock()
    processor = OrderProcessor(mock_gateway)
    processor.process(order)
    mock_gateway.charge.assert_called_once_with(100.00)
```

**Fake** - Simplified working implementation
```python
class FakeDatabase:
    def __init__(self):
        self.data = {}
    
    def save(self, key, value):
        self.data[key] = value
    
    def get(self, key):
        return self.data.get(key)
```

### Do
- Mock external dependencies (APIs, databases, file systems)
- Use dependency injection to enable mocking
- Verify behavior, not implementation
- Keep mocks simple

### Don't
- Mock everything (test real code when possible)
- Create complex mock hierarchies
- Over-specify mock expectations

---

## Summary

Effective testing:
- **Guides design** - Tests drive better architecture
- **Prevents regressions** - Catches bugs early
- **Documents behavior** - Tests are living specifications
- **Enables refactoring** - Confidence to improve code

When writing tests, ask:
- Does this test verify actual behavior?
- Will this test catch real bugs?
- Is this test easy to understand and maintain?
- Can this test run quickly and reliably?
