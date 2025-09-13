# Copy the content from the test.sh artifact I provided above
#!/bin/bash
# test.sh - Run tests for Viam HX711 module
# This script uses the same virtual environment as the module

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Use same virtual environment structure as Viam modules
VENV_DIR="venv"
PYTHON="$VENV_DIR/bin/python"

echo "🧪 Setting up HX711 module test environment..."

# Check if virtual environment exists
if [ ! -d "$VENV_DIR" ]; then
    echo "❌ Virtual environment not found. Please run ./setup.sh first."
    exit 1
fi

# Check if virtual environment is activated, if not activate it
if [ -z "${VIRTUAL_ENV:-}" ]; then
    echo "📦 Activating virtual environment..."
    source "$VENV_DIR/bin/activate"
else
    echo "✅ Virtual environment already active"
fi

# Check if pytest is installed, if not install dev dependencies
if ! "$PYTHON" -c "import pytest" 2>/dev/null; then
    echo "📚 Installing test dependencies..."
    "$PYTHON" -m pip install -r requirements-dev.txt -q
else
    echo "✅ Test dependencies already installed"
fi

# Verify imports work
echo "🔍 Verifying module imports..."
if ! "$PYTHON" -c "from src.main import Loadcell; print('✅ Module import successful')" 2>/dev/null; then
    echo "❌ Failed to import module. Check your src/main.py"
    exit 1
fi

# Run tests
echo "🚀 Running tests..."
echo "=================================="

# Default pytest args if none provided
if [ $# -eq 0 ]; then
    set -- "-v"
fi

# Execute pytest with all arguments passed to this script
exec "$PYTHON" -m pytest "$@"