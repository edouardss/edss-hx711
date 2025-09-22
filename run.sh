#!/bin/sh
cd `dirname $0`

# Create a virtual environment to run our code
VENV_NAME="venv"
PYTHON="$VENV_NAME/bin/python"

sh ./setup.sh

# Check if we have the PyInstaller executable, otherwise fall back to Python
if [ -f "./main" ]; then
    echo "Starting module using PyInstaller executable..."
    exec ./main $@
else
    echo "PyInstaller executable not found, falling back to Python..."
    exec $PYTHON -m src.main $@
fi