#!/bin/bash
# Test script for Purevent2HA addon

set -e

echo "Running tests for Purevent2HA..."

# Install test dependencies
pip install pytest pytest-cov pytest-asyncio aiohttp

# Run tests
pytest purevent2ha/tests/ -v --cov=purevent2ha/rootfs/app --cov=purevent2ha/custom_components

echo "Tests complete!"
