#!/bin/bash
# Security Gatekeeper - Validação automática antes de commit
# Usage: ./security-gatekeeper.sh [directory]

set -e

TARGET="${1:-.}"
ERRORS=0

echo "=== Security Gatekeeper ==="
echo "Scanning: $TARGET"
echo ""

# 1. Detect secrets/credentials
echo "[1/5] Detecting secrets and credentials..."
SECRETS=$(grep -rn -E "(api_key|apikey|secret|password|token|sk-|ghp_|AKIA[A-Z0-9]{16})" "$TARGET" \
  --include="*.py" --include="*.js" --include="*.ts" --include="*.json" --include="*.env" \
  --exclude-dir=node_modules --exclude-dir=.git --exclude-dir=__pycache__ \
  2>/dev/null | grep -v "example\|template\|placeholder\|YOUR_\|xxx\|changeme" || true)

if [ -n "$SECRETS" ]; then
  echo "  ❌ SECRETS DETECTED:"
  echo "$SECRETS"
  ERRORS=$((ERRORS + 1))
else
  echo "  ✓ No secrets found"
fi

# 2. Detect .env files not in .gitignore
echo ""
echo "[2/5] Checking .env files..."
ENV_FILES=$(find "$TARGET" -name ".env" -not -path "*/.git/*" 2>/dev/null || true)
for f in $ENV_FILES; do
  if ! grep -q "^\.env$" "$TARGET/.gitignore" 2>/dev/null; then
    echo "  ❌ $f exists but .env not in .gitignore"
    ERRORS=$((ERRORS + 1))
  else
    echo "  ✓ $f (gitignored)"
  fi
done

# 3. Check for hardcoded credentials in config files
echo ""
echo "[3/5] Scanning config files for credentials..."
CONFIGS=$(grep -rn -iE "(password|secret|api_key|token)\s*[:=]\s*['\"][^'\"$]{8,}" "$TARGET" \
  --include="*.json" --include="*.yaml" --include="*.yml" --include="*.toml" \
  --exclude-dir=node_modules --exclude-dir=.git \
  2>/dev/null | grep -v "example\|template\|placeholder\|YOUR_\|xxx" || true)

if [ -n "$CONFIGS" ]; then
  echo "  ❌ Potential credentials in configs:"
  echo "$CONFIGS"
  ERRORS=$((ERRORS + 1))
else
  echo "  ✓ Config files clean"
fi

# 4. Check for dangerous patterns
echo ""
echo "[4/5] Scanning for dangerous patterns..."
DANGEROUS=$(grep -rn -E "(eval\(|exec\(|os\.system\(|subprocess\.call\(.*shell=True)" "$TARGET" \
  --include="*.py" --include="*.js" --include="*.ts" \
  --exclude-dir=node_modules --exclude-dir=.git --exclude-dir=__pycache__ \
  2>/dev/null || true)

if [ -n "$DANGEROUS" ]; then
  echo "  ⚠️  Dangerous patterns found (review recommended):"
  echo "$DANGEROUS"
else
  echo "  ✓ No dangerous patterns"
fi

# 5. Check for sensitive data in logs
echo ""
echo "[5/5] Checking for sensitive data in logs..."
LOGS=$(grep -rn -E "(print\(|console\.log\(|logger\.\w+\().*password|token|secret|credential" "$TARGET" \
  --include="*.py" --include="*.js" --include="*.ts" \
  --exclude-dir=node_modules --exclude-dir=.git --exclude-dir=__pycache__ \
  2>/dev/null || true)

if [ -n "$LOGS" ]; then
  echo "  ❌ Sensitive data in logs:"
  echo "$LOGS"
  ERRORS=$((ERRORS + 1))
else
  echo "  ✓ Logs are clean"
fi

echo ""
echo "=== Results ==="
if [ $ERRORS -gt 0 ]; then
  echo "❌ BLOCKED: $ERRORS security issues found"
  echo "Fix issues before committing."
  exit 1
else
  echo "✓ PASSED: All security checks passed"
  exit 0
fi
