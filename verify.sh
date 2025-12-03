#!/bin/bash
# Verify Purevent2HA addon integrity

set -e

echo "Purevent2HA - Integrity Check"
echo "=============================="

ADDON_PATH="./purevent2ha"
ERRORS=0

check_python_syntax() {
    local file=$1
    if python3 -m py_compile "$file" 2>/dev/null; then
        echo "✅ $file"
    else
        echo "❌ $file - Syntax error"
        ERRORS=$((ERRORS + 1))
    fi
}

check_json_syntax() {
    local file=$1
    if python3 -c "import json; json.load(open('$file'))" 2>/dev/null; then
        echo "✅ $file"
    else
        echo "❌ $file - JSON error"
        ERRORS=$((ERRORS + 1))
    fi
}

echo ""
echo "Checking Python syntax..."
find "$ADDON_PATH" -name "*.py" -type f | while read f; do
    check_python_syntax "$f"
done

echo ""
echo "Checking JSON syntax..."
find "$ADDON_PATH" -name "*.json" -type f | while read f; do
    check_json_syntax "$f"
done

echo ""
echo "Checking required files..."

required_files=(
    "$ADDON_PATH/addon.yaml"
    "$ADDON_PATH/Dockerfile"
    "$ADDON_PATH/rootfs/requirements.txt"
    "$ADDON_PATH/custom_components/purevent2ha/manifest.json"
)

for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file"
    else
        echo "❌ $file - MISSING"
        ERRORS=$((ERRORS + 1))
    fi
done

echo ""
if [ $ERRORS -eq 0 ]; then
    echo "✅ All checks passed!"
    exit 0
else
    echo "❌ Found $ERRORS errors"
    exit 1
fi
