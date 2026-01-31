#!/bin/bash
set -e

echo "Building deployment package..."

# Cleanup
rm -rf dist
mkdir -p dist

# Install dependencies
echo "Installing dependencies..."
python3 -m pip install -r backend/requirements.txt --target dist/

# Copy Code
echo "Copying code..."
cp backend/handler.py dist/
cp -r backend/utils dist/
cp backend/cert.pem dist/

# Cleanup unnecessary files from dist (optional but good)
find dist -name "*.dist-info" -type d -exec rm -rf {} +
find dist -name "__pycache__" -type d -exec rm -rf {} +

echo "Package ready in dist/"
