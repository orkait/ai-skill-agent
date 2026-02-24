#!/bin/bash
# Pattern Detector: Scan Go files for common anti-patterns

set -euo pipefail

# Colors for output
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET_DIR="${1:-.}"

echo "🔍 Scanning Go files in: $TARGET_DIR"
echo ""

# Initialize counters
issues_found=0

# Check for global variables
echo "Checking for global mutable state..."
if grep -rn --include="*.go" "^var.*=.*\(sql.DB\|http.Client\|redis.Client\)" "$TARGET_DIR" 2>/dev/null; then
    echo -e "${RED}⚠ Found global database/client connections${NC}"
    echo "  Consider dependency injection instead"
    ((issues_found++))
fi

# Check for init() usage
echo ""
echo "Checking for init() functions..."
init_count=$(grep -rn --include="*.go" "^func init()" "$TARGET_DIR" 2>/dev/null | wc -l)
if [ "$init_count" -gt 0 ]; then
    echo -e "${YELLOW}⚠ Found $init_count init() functions${NC}"
    grep -rn --include="*.go" "^func init()" "$TARGET_DIR" 2>/dev/null || true
    echo "  Consider explicit initialization in constructors"
    ((issues_found++))
fi

# Check for ignored errors
echo ""
echo "Checking for ignored errors..."
if grep -rn --include="*.go" '^\s*_\s*=.*\(Error\|err\)' "$TARGET_DIR" 2>/dev/null; then
    echo -e "${RED}⚠ Found ignored errors with blank identifier${NC}"
    echo "  Always check and handle errors"
    ((issues_found++))
fi

# Check for panic in non-init code
echo ""
echo "Checking for panic usage..."
if grep -rn --include="*.go" 'panic(' "$TARGET_DIR" 2>/dev/null | grep -v "func init()" | head -5; then
    echo -e "${YELLOW}⚠ Found panic() outside init()${NC}"
    echo "  Consider returning errors instead"
    ((issues_found++))
fi

# Check for goroutines without context
echo ""
echo "Checking for goroutines without context..."
if grep -rn --include="*.go" 'go func()' "$TARGET_DIR" 2>/dev/null | grep -v "context.Context" | head -5; then
    echo -e "${YELLOW}⚠ Found goroutines potentially without cancellation${NC}"
    echo "  Pass context.Context for proper cancellation"
    ((issues_found++))
fi

# Check for large interfaces (>5 methods)
echo ""
echo "Checking for large interfaces..."
while IFS= read -r file; do
    awk '
    /^type .* interface {/ {
        interface_name = $2
        method_count = 0
        in_interface = 1
    }
    in_interface && /^[[:space:]]+[A-Z].*\(/ {
        method_count++
    }
    in_interface && /^}/ {
        if (method_count > 5) {
            print FILENAME ":" interface_name " has " method_count " methods (consider splitting)"
        }
        in_interface = 0
    }
    ' "$file"
done < <(find "$TARGET_DIR" -name "*.go" 2>/dev/null)

# Summary
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ $issues_found -eq 0 ]; then
    echo -e "${GREEN}✓ No obvious anti-patterns detected${NC}"
else
    echo -e "${RED}Found $issues_found potential issues${NC}"
    echo ""
    echo "Review the warnings above and consult:"
    echo "  - references/anti-patterns.md for detailed explanations"
    echo "  - SKILL.md for idiomatic alternatives"
fi
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
