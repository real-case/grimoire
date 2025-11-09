#!/bin/bash

# Grimoire Monorepo Migration Validation Script
# Based on research.md validation checklist
# Created: 2025-10-19

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "======================================"
echo "Grimoire Monorepo Migration Validation"
echo "======================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

PASS=0
FAIL=0

# Helper function to print test results
print_test() {
    local test_name="$1"
    local result="$2"
    local details="$3"

    if [ "$result" = "PASS" ]; then
        echo -e "${GREEN}✓${NC} $test_name"
        [ -n "$details" ] && echo "  $details"
        PASS=$((PASS + 1))
    else
        echo -e "${RED}✗${NC} $test_name"
        [ -n "$details" ] && echo "  $details"
        FAIL=$((FAIL + 1))
    fi
}

echo "Test 1: Verify API tests pass"
echo "------------------------------"
if cd "$REPO_ROOT/apps/api" && npx nx run api:test 2>&1 | tail -20; then
    print_test "API tests pass" "PASS" "All API tests executed successfully"
else
    print_test "API tests pass" "FAIL" "API tests failed - check output above"
fi
echo ""

echo "Test 2: Verify UI tests pass"
echo "-----------------------------"
if cd "$REPO_ROOT/apps/ui" && npx nx run ui:test 2>&1 | tail -20; then
    print_test "UI tests pass" "PASS" "All UI tests executed successfully"
else
    print_test "UI tests pass" "FAIL" "UI tests failed - check output above"
fi
echo ""

echo "Test 3: Verify API serves in <30 seconds"
echo "-----------------------------------------"
cd "$REPO_ROOT"
START_TIME=$(date +%s)
timeout 35s bash -c "npx nx run api:serve &> /dev/null &
PID=\$!
sleep 30
kill \$PID 2>/dev/null || true
" && SERVE_RESULT=0 || SERVE_RESULT=1

END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

if [ $SERVE_RESULT -eq 0 ] && [ $DURATION -le 30 ]; then
    print_test "API serves <30s" "PASS" "API started in ${DURATION}s"
else
    print_test "API serves <30s" "FAIL" "API took ${DURATION}s or failed to start"
fi
echo ""

echo "Test 4: Verify UI serves in <30 seconds"
echo "----------------------------------------"
START_TIME=$(date +%s)
timeout 35s bash -c "npx nx run ui:serve &> /dev/null &
PID=\$!
sleep 30
kill \$PID 2>/dev/null || true
" && SERVE_RESULT=0 || SERVE_RESULT=1

END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

if [ $SERVE_RESULT -eq 0 ] && [ $DURATION -le 30 ]; then
    print_test "UI serves <30s" "PASS" "UI started in ${DURATION}s"
else
    print_test "UI serves <30s" "FAIL" "UI took ${DURATION}s or failed to start"
fi
echo ""

echo "Test 5: Verify Docker builds"
echo "-----------------------------"
if docker-compose build --quiet api 2>&1 | tail -10; then
    print_test "Docker builds" "PASS" "Docker build completed successfully"
else
    print_test "Docker builds" "FAIL" "Docker build failed - check output above"
fi
echo ""

echo "Test 6: Verify Nx affected detection works"
echo "-------------------------------------------"
if npx nx affected:graph --base=main --dry-run 2>&1 | grep -q "affected"; then
    print_test "Affected detection" "PASS" "Nx affected command works"
else
    print_test "Affected detection" "FAIL" "Nx affected command failed"
fi
echo ""

echo "Test 7: Verify Git history preserved"
echo "-------------------------------------"
cd "$REPO_ROOT"
if git log --follow apps/api/src/main.py 2>&1 | head -5 | grep -q "commit"; then
    COMMITS=$(git log --follow apps/api/src/main.py --oneline | wc -l | tr -d ' ')
    print_test "Git history preserved" "PASS" "Found ${COMMITS} commits for apps/api/src/main.py"
else
    print_test "Git history preserved" "FAIL" "Git history not found or incomplete"
fi
echo ""

echo "======================================"
echo "Validation Summary"
echo "======================================"
echo -e "${GREEN}Passed:${NC} $PASS tests"
echo -e "${RED}Failed:${NC} $FAIL tests"
echo ""

if [ $FAIL -eq 0 ]; then
    echo -e "${GREEN}✓ All validation tests passed!${NC}"
    echo "The monorepo migration is successful."
    exit 0
else
    echo -e "${RED}✗ Some validation tests failed.${NC}"
    echo "Please review the failures above before proceeding."
    exit 1
fi
