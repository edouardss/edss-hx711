#!/bin/bash
# Test runner script for HX711 Loadcell component
# Automatically sets up virtual environment and runs tests

set -e  # Exit on any error

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PATH="$PROJECT_ROOT/.venv"

echo "=========================================="
echo "HX711 Loadcell Component Test Runner"
echo "=========================================="
echo "Project root: $PROJECT_ROOT"
echo "Virtual environment: $VENV_PATH"
echo ""

# Function to check if virtual environment exists and is valid
check_venv() {
    if [ ! -d "$VENV_PATH" ]; then
        return 1
    fi
    
    if [ ! -f "$VENV_PATH/bin/python" ]; then
        return 1
    fi
    
    # Check if pytest is installed
    if ! "$VENV_PATH/bin/python" -c "import pytest" 2>/dev/null; then
        return 1
    fi
    
    return 0
}

# Function to setup virtual environment
setup_venv() {
    echo "Setting up virtual environment..."
    cd "$PROJECT_ROOT"
    
    if ! python3 -c "import venv" 2>/dev/null; then
        echo "❌ Error: venv module not available. Please install python3-venv"
        exit 1
    fi
    
    python3 setup_test_env.py --force-recreate
    
    if ! check_venv; then
        echo "❌ Error: Virtual environment setup failed"
        exit 1
    fi
    
    echo "✅ Virtual environment setup complete"
}

# Function to activate virtual environment
activate_venv() {
    if [ -f "$VENV_PATH/bin/activate" ]; then
        source "$VENV_PATH/bin/activate"
        echo "✅ Virtual environment activated"
    else
        echo "❌ Error: Virtual environment activation script not found"
        exit 1
    fi
}

# Function to run tests
run_tests() {
    cd "$PROJECT_ROOT"
    
    echo "Running tests..."
    echo "Command: python tests/run_tests.py $*"
    echo ""
    
    python tests/run_tests.py "$@"
}

# Main logic
case "${1:-}" in
    "setup")
        echo "Setting up test environment..."
        setup_venv
        echo ""
        echo "Setup complete! You can now run tests with:"
        echo "  ./test.sh"
        echo "  ./test.sh --coverage"
        echo "  ./test.sh --unit"
        ;;
    "clean")
        echo "Cleaning virtual environment..."
        if [ -d "$VENV_PATH" ]; then
            rm -rf "$VENV_PATH"
            echo "✅ Virtual environment removed"
        else
            echo "ℹ️  No virtual environment to clean"
        fi
        ;;
    "shell")
        echo "Activating virtual environment shell..."
        if ! check_venv; then
            echo "Virtual environment not found. Setting up..."
            setup_venv
        fi
        activate_venv
        echo ""
        echo "Virtual environment activated. You can now run commands like:"
        echo "  pytest tests/"
        echo "  python tests/run_tests.py --coverage"
        echo "  deactivate  # to exit the virtual environment"
        echo ""
        exec bash
        ;;
    "help"|"-h"|"--help")
        echo "Usage: $0 [command] [test-options]"
        echo ""
        echo "Commands:"
        echo "  setup    Set up virtual environment"
        echo "  clean    Remove virtual environment"
        echo "  shell    Activate virtual environment shell"
        echo "  help     Show this help message"
        echo ""
        echo "Test Options (passed to run_tests.py):"
        echo "  --unit        Run only unit tests"
        echo "  --integration Run only integration tests"
        echo "  --coverage    Run with coverage reporting"
        echo "  --verbose     Verbose output"
        echo "  --lint        Run linting checks"
        echo "  --format      Run code formatting checks"
        echo "  --all         Run all checks"
        echo ""
        echo "Examples:"
        echo "  $0                    # Run all tests"
        echo "  $0 --coverage         # Run tests with coverage"
        echo "  $0 --unit --verbose   # Run unit tests with verbose output"
        echo "  $0 setup              # Set up virtual environment"
        echo "  $0 shell              # Activate virtual environment shell"
        ;;
    *)
        # Check if virtual environment exists and is valid
        if ! check_venv; then
            echo "⚠️  Virtual environment not found or invalid"
            echo "Setting up virtual environment..."
            setup_venv
            echo ""
        fi
        
        # Run tests with provided arguments
        run_tests "$@"
        ;;
esac

