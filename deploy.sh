#!/bin/bash
# Deployment script for Purevent2HA addon

set -e

echo "====================================="
echo "Purevent2HA - Deployment Script"
echo "====================================="

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ADDON_PATH="${REPO_ROOT}/purevent2ha"

echo ""
echo "📁 Repository root: $REPO_ROOT"
echo "📦 Addon path: $ADDON_PATH"

# Function to check file exists
check_file() {
    if [ -f "$1" ]; then
        echo "✅ $1"
        return 0
    else
        echo "❌ $1 - NOT FOUND"
        return 1
    fi
}

# Function to check directory exists
check_dir() {
    if [ -d "$1" ]; then
        echo "✅ $1"
        return 0
    else
        echo "❌ $1 - NOT FOUND"
        return 1
    fi
}

echo ""
echo "=== Checking addon structure ==="

# Check main files
echo ""
echo "Main files:"
check_file "$ADDON_PATH/addon.yaml"
check_file "$ADDON_PATH/Dockerfile"
check_file "$ADDON_PATH/DOCS.md"
check_file "$ADDON_PATH/README.md"
check_file "$ADDON_PATH/DEVELOPMENT.md"

# Check root files
echo ""
echo "Root files:"
check_file "$REPO_ROOT/README.md"
check_file "$REPO_ROOT/SETUP.md"
check_file "$REPO_ROOT/EXAMPLES.md"
check_file "$REPO_ROOT/CHANGELOG.md"
check_file "$REPO_ROOT/LICENSE"
check_file "$REPO_ROOT/repository.json"

# Check directories
echo ""
echo "Directories:"
check_dir "$ADDON_PATH/rootfs/app"
check_dir "$ADDON_PATH/rootfs/etc/purevent2ha"
check_dir "$ADDON_PATH/rootfs/usr/local/bin"
check_dir "$ADDON_PATH/custom_components/purevent2ha"
check_dir "$ADDON_PATH/custom_components/purevent2ha/devices"
check_dir "$ADDON_PATH/custom_components/purevent2ha/translations"

# Check daemon files
echo ""
echo "Daemon files:"
check_file "$ADDON_PATH/rootfs/app/purevent2ha_daemon.py"
check_file "$ADDON_PATH/rootfs/app/enocean_comm.py"
check_file "$ADDON_PATH/rootfs/app/api.py"
check_file "$ADDON_PATH/rootfs/app/utils.py"
check_file "$ADDON_PATH/rootfs/usr/local/bin/startup.sh"

# Check integration files
echo ""
echo "Integration files:"
check_file "$ADDON_PATH/custom_components/purevent2ha/__init__.py"
check_file "$ADDON_PATH/custom_components/purevent2ha/manifest.json"
check_file "$ADDON_PATH/custom_components/purevent2ha/const.py"
check_file "$ADDON_PATH/custom_components/purevent2ha/config_flow.py"
check_file "$ADDON_PATH/custom_components/purevent2ha/coordinator.py"
check_file "$ADDON_PATH/custom_components/purevent2ha/services.py"

# Check platforms
echo ""
echo "Platforms:"
check_file "$ADDON_PATH/custom_components/purevent2ha/sensor.py"
check_file "$ADDON_PATH/custom_components/purevent2ha/switch.py"
check_file "$ADDON_PATH/custom_components/purevent2ha/climate.py"
check_file "$ADDON_PATH/custom_components/purevent2ha/number.py"

# Check device configs
echo ""
echo "Device configurations:"
check_file "$ADDON_PATH/custom_components/purevent2ha/devices/d1079-01-00.json"
check_file "$ADDON_PATH/custom_components/purevent2ha/devices/a5-09-04.json"
check_file "$ADDON_PATH/custom_components/purevent2ha/devices/a5-04-01.json"
check_file "$ADDON_PATH/custom_components/purevent2ha/devices/d1079-00-00.json"

# Check CI/CD
echo ""
echo "CI/CD files:"
check_file "$REPO_ROOT/.github/workflows/build.yml"
check_file "$REPO_ROOT/.github/workflows/lint.yml"
check_file "$REPO_ROOT/.container-build.yaml"

echo ""
echo "=== File statistics ==="
echo "Python files: $(find "$ADDON_PATH" -name '*.py' -type f | wc -l)"
echo "JSON files: $(find "$ADDON_PATH" -name '*.json' -type f | wc -l)"
echo "YAML files: $(find "$ADDON_PATH" -name '*.yaml' -o -name '*.yml' | wc -l)"

echo ""
echo "=== Deployment ready! ==="
echo ""
echo "Next steps:"
echo "1. Push to GitHub:"
echo "   git add ."
echo "   git commit -m 'feat: Initial Purevent2HA addon release'"
echo "   git push origin main"
echo ""
echo "2. Create GitHub release"
echo ""
echo "3. Add to Home Assistant addon stores"
echo ""
echo "4. Users can add repository:"
echo "   https://github.com/ricolaflo88/Purevent2HA"
echo ""
