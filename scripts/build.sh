#!/usr/bin/env bash
# Build M8 module for Move Anything
# This is a JS-only module, so just package the files.
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$REPO_ROOT"

echo "=== Building M8 Module ==="

# Create dist directory
mkdir -p dist/m8

# Copy files
echo "Packaging..."
cp src/module.json dist/m8/
cp src/ui.js dist/m8/

# Create tarball for release
cd dist
tar -czvf m8-module.tar.gz m8/
cd ..

echo ""
echo "=== Build Complete ==="
echo "Output: dist/m8/"
echo "Tarball: dist/m8-module.tar.gz"
echo ""
echo "To install on Move:"
echo "  ./scripts/install.sh"
