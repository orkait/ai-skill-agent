# Task Classification Framework

## Purpose

Before writing any code, classify the task to determine the appropriate engineering approach. This prevents mismatched solutions and establishes clear success criteria.

## Classification Categories

### 1. New Feature

**Characteristics:**
- Adds new capability to the system
- Introduces new entry points or APIs
- May require new dependencies or infrastructure

**Checklist:**
- [ ] Requirements clearly defined
- [ ] Success criteria established
- [ ] Dependencies identified
- [ ] Architecture impacts assessed
- [ ] Test strategy defined

**Process:**
1. Define public API first
2. Identify module boundaries
3. Plan dependency direction
4. Design data flow
5. Implement with tests
6. Document behavior

---

### 2. Refactor (Behavior Preserved)

**Characteristics:**
- Changes internal structure
- **Zero** behavior change
- Improves maintainability, readability, or performance
- Must have tests locking existing behavior

**Critical Rule:** No refactor without tests. If tests don't exist, the first step is writing them, not refactoring.

**Process:**
1. **Verify tests exist** - If no tests, write them first
2. Make small, safe changes
3. Run tests after each change
4. Commit incrementally
5. Verify no behavior change

---

### 3. Bug Fix

**Characteristics:**
- Corrects incorrect behavior
- Has observable failure mode
- Should have reproduction test
- May require root cause analysis

**Process:**
1. Write failing test that reproduces bug
2. Identify root cause (not just symptom)
3. Implement minimal fix
4. Verify test now passes
5. Check for similar bugs elsewhere
6. Document root cause and fix

---

### 4. Review / Audit

**Characteristics:**
- Evaluates existing code
- Identifies issues, risks, or improvements
- Does not modify code
- Produces recommendations

**Process:**
1. Define review scope and criteria
2. Check against engineering principles
3. Identify risks and violations
4. Assess severity and impact
5. Provide prioritized recommendations
6. Suggest concrete improvements

---

### 5. Documentation Only

**Process:**
1. Identify what needs documentation
2. Determine appropriate level of detail
3. Use examples liberally
4. Link to related docs
5. Keep close to code
6. Verify accuracy

---

## Classification Decision Tree

```
Is code changing?
├─ No → Documentation Only
└─ Yes
   ├─ Does it add new capability?
   │  └─ Yes → New Feature
   └─ No
      ├─ Does it fix incorrect behavior?
      │  └─ Yes → Bug Fix
      └─ No
         └─ Does it change structure without behavior change?
            └─ Yes → Refactor
```

## When Classification is Unclear

**Stop and clarify:**
- Request missing requirements
- Ask about success criteria
- Identify ambiguities
- Confirm behavior expectations
- Define scope boundaries

**Never proceed with unclear classification.**

## Golden Rule

**If you can't classify it, don't start it.**
