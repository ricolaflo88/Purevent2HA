#!/bin/bash
# Build script for Purevent2HA addon

set -e

echo "Building Purevent2HA addon..."

ADDON_PATH="./purevent2ha"
DOCKER_IMAGE="purevent2ha"

# Build for different architectures
ARCHS=("amd64" "armv7" "armhf" "aarch64")

for arch in "${ARCHS[@]}"; do
    echo "Building for $arch..."
    
    case "$arch" in
        amd64)
            BUILD_FROM="ghcr.io/home-assistant/amd64-base:3.11"
            ;;
        armv7)
            BUILD_FROM="ghcr.io/home-assistant/armv7-base:3.11"
            ;;
        armhf)
            BUILD_FROM="ghcr.io/home-assistant/armhf-base:3.11"
            ;;
        aarch64)
            BUILD_FROM="ghcr.io/home-assistant/aarch64-base:3.11"
            ;;
    esac
    
    docker build \
        --build-arg BUILD_FROM="$BUILD_FROM" \
        -t "ghcr.io/ricolaflo88/${DOCKER_IMAGE}:${arch}" \
        "$ADDON_PATH"
done

echo "Build complete!"
