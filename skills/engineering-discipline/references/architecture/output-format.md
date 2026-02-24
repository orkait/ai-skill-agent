# Standard Output Format

Always structure Process Mode responses as:

```markdown
## 1. Task Classification
[Feature | Refactor | Bug | Review | Docs]

## 2. Assumptions
- Input assumptions
- State assumptions
- Environment assumptions

## 3. Architecture / Design
- Responsibilities
- Invariants
- Dependencies
- Module boundaries

## 4. Public APIs
- Function signatures
- Input/output contracts
- Error cases

## 5. Code
[Implementation]

## 6. Tests
[Test cases covering happy path, edge cases, errors]

## 7. Risks & Trade-offs
- What can fail
- Performance considerations
- Maintainability impact

## 8. Negative Doubt Log (Process Mode only)
- Failure modes discovered
- Tests added
- Assumptions changed
- Final decision changes
```

## Quick Reference Mode Format

For direct pattern/principle lookups, respond concisely:
- State the answer directly
- Reference the relevant principle file
- Provide 2–3 supporting points
- Note trade-offs if relevant
