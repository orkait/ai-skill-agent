# Readability & Clarity Principles

## Descriptive Naming

**Definition:** Use clear, meaningful names for variables, functions, classes, etc., so code reads like natural language. Avoid vague, abbreviated, or encoded names. Good names explain intent without requiring comments.

**Supported by:** *Clean Code*, *Code Complete*

### Examples

```python
# Bad
def calc(a, b):
    return a * b + 3

# Good
def calculate_rectangle_area(width, height):
    margin = 3
    return width * height + margin
```

### Do
- Use nouns for data structures and variables
- Use verbs for functions and methods
- Use consistent domain terminology
- Make names pronounceable and searchable
- Use solution/problem domain names

### Don't
- Use single-letter names (except loop counters in small scopes)
- Create misleading names
- Use encodings or prefixes (Hungarian notation)
- Use abbreviations unless universally known
- Mix naming conventions in the same scope

### AI Pitfalls
- Repeating generic names like `data`, `temp`, `foo`, `result`
- Inconsistent naming across similar concepts
- Using placeholder names and forgetting to rename
- Over-shortening meaningful names for brevity

---

## Consistent Style & Formatting

**Definition:** Follow a uniform coding style and project conventions. Consistency aids readability and reduces cognitive load.

**Supported by:** *Clean Code*, *Code Complete*

### Examples

```javascript
// Bad - Inconsistent spacing, braces, indentation
if(x>0){
y= x+10;
    console.log(y);}

// Good - Consistent formatting
if (x > 0) {
    let result = x + 10;
    console.log(result);
}
```

### Do
- Stick to one brace style (K&R, Allman, etc.)
- Use consistent indentation (2 or 4 spaces, never mix tabs/spaces)
- Follow language conventions (PEP 8 for Python, Airbnb for JS)
- Maintain consistent line length (80-120 characters)
- Use automated formatters (Prettier, Black, rustfmt)

### Don't
- Mix different formatting styles in one file
- Ignore project linting rules
- Use inconsistent whitespace
- Create overly long lines

### AI Pitfalls
- Producing inconsistent formatting across code blocks
- Mixing indentation styles
- Ignoring existing project formatting conventions

---

## Self-Documenting Code (Minimize Comments)

**Definition:** Write code so its intent is clear from the code itself. Comments should explain *why*, not *what*.

**Supported by:** *Clean Code*, *Code Complete*

### Examples

```python
# Bad - Redundant comment
# Increment i by 1
i = i + 1

# Good - No comment needed
i = i + 1

# Acceptable - Explains business rule
# Block access for users under minimum age requirement
if user.age < 13:
    block_access()

# Good - Explains non-obvious why
# Using exponential backoff to avoid API rate limits
retry_delay = base_delay * (2 ** attempt_count)
```

### Do
- Use clear naming and logic structure
- Comment complex algorithms or business rules
- Explain performance optimizations
- Document API contracts and side effects
- Add TODO comments for future work (with ticket IDs)

### Don't
- Write comments that restate the code
- Leave commented-out code
- Write misleading or outdated comments
- Use comments to fix bad naming

### AI Pitfalls
- Over-commenting obvious operations
- Leaving stale or contradictory comments
- Using comments instead of refactoring unclear code

---

## Small Functions & Single Responsibility

**Definition:** Functions and methods should do one thing and do it well. Small, cohesive units are easier to understand, test, and maintain.

**Supported by:** *Clean Code*, *Code Complete*

### Examples

```python
# Bad - Function does too many things
def update_user(data):
    validate(data)
    update_database(data)
    send_email(data)
    log_activity(data)
    invalidate_cache(data)

# Good - Separated concerns
def update_user(data):
    validated_data = validate(data)
    save_user(validated_data)
    notify_user(validated_data)

def save_user(data):
    update_database(data)
    invalidate_cache(data)

def notify_user(data):
    send_email(data)
    log_activity(data)
```

### Do
- Keep functions under 20-30 lines when possible
- Extract helper functions for complex logic
- Use descriptive function names that indicate purpose
- Limit function parameters (ideally ≤ 3)
- Make one level of abstraction per function

### Don't
- Combine unrelated operations
- Create deeply nested logic
- Use flag arguments to control behavior
- Write functions that both query and modify state

### AI Pitfalls
- Creating monolithic functions with multiple responsibilities
- Over-fragmenting into excessive tiny functions
- Mixing abstraction levels within one function
- Generating functions that modify global state unexpectedly

---

## Summary

Readable code is:
- **Self-explanatory** through naming
- **Consistent** in style and structure
- **Minimal in comments** - code speaks for itself
- **Small and focused** - easy to understand at a glance

When writing or reviewing code, ask:
- Can I understand this without the author present?
- Would I want to debug this at 2 AM?
- Does this follow the team's conventions?
