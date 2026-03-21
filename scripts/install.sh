#!/bin/bash
# Install M8 module to Move
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$REPO_ROOT"

if [ ! -d "dist/m8" ]; then
    echo "Error: dist/m8 not found. Run ./scripts/build.sh first."
    exit 1
fi

echo "=== Installing M8 Module ==="

# Deploy to Move - overtake subdirectory (component_type: overtake)
echo "Copying module to Move..."
ssh ableton@move.local "mkdir -p /data/UserData/schwung/modules/overtake/m8"
scp -r dist/m8/* ableton@move.local:/data/UserData/schwung/modules/overtake/m8/

# Set permissions so Module Store can update later
echo "Setting permissions..."
ssh ableton@move.local "chmod -R a+rw /data/UserData/schwung/modules/overtake/m8"

echo ""
echo "=== Install Complete ==="
echo "Module installed to: /data/UserData/schwung/modules/overtake/m8/"
echo ""
echo "Restart Schwung to load the new module."
