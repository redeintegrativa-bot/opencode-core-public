#!/bin/bash
# Pre-commit hook - Security validation before every commit
# Install: cp pre-commit-security.sh .git/hooks/pre-commit && chmod +x .git/hooks/pre-commit

set -e

echo "🔒 Pre-commit Security Check..."
echo ""

# Run security gatekeeper on staged files only
STAGED_FILES=$(git diff --cached --name-only --diff-filter=ACM 2>/dev/null)

if [ -z "$STAGED_FILES" ]; then
  echo "No files to check."
  exit 0
fi

ERRORS=0

# 1. Check staged files for secrets
echo "[1/3] Scanning staged files for secrets..."
for FILE in $STAGED_FILES; do
  if [ -f "$FILE" ]; then
    SECRETS=$(grep -n -E "(api_key|apikey|secret|password|token|sk-|ghp_|AKIA[A-Z0-9]{16})" "$FILE" \
      2>/dev/null | grep -v "example\|template\|placeholder\|YOUR_\|xxx\|changeme" || true)
    
    if [ -n "$SECRETS" ]; then
      echo "  ❌ Secrets in $FILE:"
      echo "$SECRETS"
      ERRORS=$((ERRORS + 1))
    fi
  fi
done

# 2. Check for .env files
echo ""
echo "[2/3] Checking for .env files..."
for FILE in $STAGED_FILES; do
  if echo "$FILE" | grep -qE "\.env$"; then
    echo "  ❌ .env file staged: $FILE"
    ERRORS=$((ERRORS + 1))
  fi
done

# 3. Check for dangerous patterns in new code
echo ""
echo "[3/3] Scanning for dangerous patterns..."
for FILE in $STAGED_FILES; do
  if [ -f "$FILE" ] && echo "$FILE" | grep -qE "\.(py|js|ts)$"; then
    DANGEROUS=$(grep -n -E "(eval\(|exec\(|os\.system\(|subprocess\.call\(.*shell=True)" "$FILE" 2>/dev/null || true)
    if [ -n "$DANGEROUS" ]; then
      echo "  ⚠️  Dangerous pattern in $FILE:"
      echo "$DANGEROUS"
    fi
  fi
done

echo ""
echo "=== Pre-commit Results ==="
if [ $ERRORS -gt 0 ]; then
  echo "❌ BLOCKED: $ERRORS security issues found"
  echo "Commit aborted. Fix issues first."
  exit 1
else
  echo "✓ PASSED: Security check passed"
  exit 0
fi
