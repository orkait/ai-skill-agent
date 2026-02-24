# Security Best Practices

**Priority: P0 (CRITICAL)**

See the [COMPLETE_REFERENCE.md](../COMPLETE_REFERENCE.md) for the full security guide.

## Quick Reference

### Critical Rules

1. **ALWAYS use `crypto/rand`** - Never `math/rand` for security
2. **Parameterized queries only** - Never string concatenation for SQL
3. **bcrypt/argon2 for passwords** - Never MD5/SHA1
4. **Validate JWT claims** - Check `alg`, `iss`, `aud`, `exp`

### Example: Secure Token Generation

```go
import "crypto/rand"
import "encoding/base64"

func GenerateToken() (string, error) {
    b := make([]byte, 32)
    if _, err := rand.Read(b); err != nil {
        return "", err
    }
    return base64.URLEncoding.EncodeToString(b), nil
}
```

For complete examples and patterns, see [../COMPLETE_REFERENCE.md#9-security](../COMPLETE_REFERENCE.md).
