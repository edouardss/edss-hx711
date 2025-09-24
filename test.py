#!/usr/bin/env python3
"""
Simple test runner for edss-hx711 module
Replaces multiple test scripts with a single, clean interface
"""

import subprocess
import sys
import os
from pathlib import Path


def check_virtual_environment():
    """Check if we're running in a virtual environment"""
    in_venv = (
        hasattr(sys, 'real_prefix') or 
        (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    )
    
    # Check if we're using a venv in the current project directory
    project_dir = Path(__file__).parent
    venv_dir = project_dir / "venv"
    using_project_venv = str(venv_dir) in sys.prefix
    
    if not in_venv or not using_project_venv:
        print("⚠️  Not using project virtual environment.")
        print("   Run: source venv/bin/activate")
        return False
    
    return True


def install_dev_dependencies():
    """Install development dependencies if needed"""
    try:
        import pytest
        print("✅ Test dependencies already installed")
        return True
    except ImportError:
        print("📦 Installing test dependencies...")
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "-e", ".[test]"
        ])
        return result.returncode == 0


def run_tests():
    """Run the test suite"""
    print("🧪 Running edss-hx711 tests...")
    print("=" * 50)
    
    # Base pytest command
    cmd = [sys.executable, "-m", "pytest"]
    
    # Add arguments based on command line options
    if "--coverage" in sys.argv:
        cmd.extend(["--cov=src", "--cov-report=html", "--cov-report=term"])
        print("📊 Coverage reporting enabled")
    
    if "--verbose" in sys.argv or "-v" in sys.argv:
        cmd.append("-v")
    
    if "--hardware" in sys.argv:
        cmd.extend(["-m", "hardware"])
        print("🔧 Hardware tests enabled")
    else:
        cmd.extend(["-m", "not hardware"])
        print("🔧 Hardware tests disabled (use --hardware to enable)")
    
    # Add specific test files if provided
    test_args = [arg for arg in sys.argv[1:] if arg.startswith("test_") or arg == "tests"]
    if test_args:
        cmd.extend(test_args)
    
    # Run the tests
    print(f"Command: {' '.join(cmd)}")
    print("-" * 50)
    
    result = subprocess.run(cmd)
    
    if result.returncode == 0:
        print("\n✅ All tests passed!")
        if "--coverage" in sys.argv:
            print("📊 Coverage report generated in htmlcov/")
    else:
        print("\n❌ Some tests failed!")
    
    return result.returncode


def show_help():
    """Show usage information"""
    print("""
🧪 edss-hx711 Test Runner

Usage:
    python test.py [options]

Options:
    --coverage     Generate coverage report
    --verbose, -v  Verbose output
    --hardware     Enable hardware tests (requires HARDWARE_TESTS_ENABLED=true)
    --help, -h     Show this help

Examples:
    python test.py                    # Run basic tests
    python test.py --coverage         # Run with coverage
    python test.py --hardware -v      # Run hardware tests verbosely
    python test.py tests/test_loadcell.py  # Run specific test file

Environment Variables:
    HARDWARE_TESTS_ENABLED=true       # Enable hardware tests
""")


def main():
    """Main entry point"""
    if "--help" in sys.argv or "-h" in sys.argv:
        show_help()
        return 0
    
    # Check virtual environment
    if not check_virtual_environment():
        return 1
    
    # Install dependencies if needed
    if not install_dev_dependencies():
        print("❌ Failed to install test dependencies")
        return 1
    
    # Run tests
    return run_tests()


if __name__ == "__main__":
    sys.exit(main())
