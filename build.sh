#!/bin/sh
cd `dirname $0`

# Create a virtual environment to run our code
VENV_NAME="venv"
PYTHON="$VENV_NAME/bin/python"

if ! $PYTHON -m pip install pyinstaller -Uqq; then
    exit 1
fi

# Build the Python executable
$PYTHON -m PyInstaller --onefile --hidden-import="googleapiclient" src/main.py

# Create a comprehensive module package
echo "📦 Creating module package with all necessary files..."

# Create a temporary directory for packaging
TEMP_DIR="temp_module"
rm -rf "$TEMP_DIR"
mkdir -p "$TEMP_DIR"

# Copy essential files for deployment
cp setup.sh "$TEMP_DIR/"
cp run.sh "$TEMP_DIR/"
cp build.sh "$TEMP_DIR/"
cp meta.json "$TEMP_DIR/"
cp requirements.txt "$TEMP_DIR/"
cp README.md "$TEMP_DIR/"

# Copy source code
cp -r src/ "$TEMP_DIR/"

# Copy the built executable
cp dist/main "$TEMP_DIR/"

# Create the final module archive in the dist directory
mkdir -p dist
tar -czvf dist/module.tar.gz -C "$TEMP_DIR" .

# Clean up temporary directory
rm -rf "$TEMP_DIR"

echo "✅ Module package created: dist/module.tar.gz"
echo "📋 Included files:"
tar -tzf dist/module.tar.gz | head -20
echo "... (and more)"