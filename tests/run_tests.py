
#!/usr/bin/env python3
"""
Test runner script for HX711 Loadcell component tests.
Provides various test execution options and configurations.
Automatically sets up and uses virtual environment if needed.
"""

import sys
import os
import subprocess
import argparse
from pathlib import Path
import venv


def get_venv_python(venv_path: Path) -> Path:
    """Get the Python executable path in the virtual environment."""
    if sys.platform == "win32":
        return venv_path / "Scripts" / "python.exe"
    else:
        return venv_path / "bin" / "python"


def check_venv_setup(project_root: Path) -> Path:
    """Check if virtual environment exists and is properly set up."""
    venv_path = project_root / ".venv"
    
    if not venv_path.exists():
        print(f"⚠️  Virtual environment not found at {venv_path}")
        print("   Run 'python setup_test_env.py' to create it")
        return None
    
    python_exe = get_venv_python(venv_path)
    if not python_exe.exists():
        print(f"⚠️  Python executable not found in virtual environment: {python_exe}")
        print("   Virtual environment may be corrupted")
        return None
    
    # Check if pytest is available in the venv
    try:
        result = subprocess.run(
            [str(python_exe), "-c", "import pytest"],
            capture_output=True,
            text=True,
            check=False
        )
        if result.returncode != 0:
            print("⚠️  pytest not found in virtual environment")
            print("   Run 'python setup_test_env.py' to reinstall dependencies")
            return None
    except Exception as e:
        print(f"⚠️  Error checking virtual environment: {e}")
        return None
    
    return venv_path


def run_command(cmd, description, use_venv_python=None):
    """Run a command and handle errors."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(cmd)}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running {description}:")
        print(f"Return code: {e.returncode}")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        return False


def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(description="Run HX711 Loadcell component tests")
    parser.add_argument(
        "--unit", 
        action="store_true", 
        help="Run only unit tests"
    )
    parser.add_argument(
        "--integration", 
        action="store_true", 
        help="Run only integration tests"
    )
    parser.add_argument(
        "--slow", 
        action="store_true", 
        help="Include slow tests"
    )
    parser.add_argument(
        "--coverage", 
        action="store_true", 
        help="Run with coverage reporting"
    )
    parser.add_argument(
        "--parallel", 
        type=int, 
        default=1, 
        help="Number of parallel workers (default: 1)"
    )
    parser.add_argument(
        "--verbose", 
        action="store_true", 
        help="Verbose output"
    )
    parser.add_argument(
        "--lint", 
        action="store_true", 
        help="Run linting checks"
    )
    parser.add_argument(
        "--format", 
        action="store_true", 
        help="Format code with black"
    )
    parser.add_argument(
        "--all", 
        action="store_true", 
        help="Run all checks (tests, lint, format)"
    )
    parser.add_argument(
        "--setup-venv", 
        action="store_true", 
        help="Set up virtual environment before running tests"
    )
    parser.add_argument(
        "--no-venv", 
        action="store_true", 
        help="Skip virtual environment checks and use system Python"
    )
    
    args = parser.parse_args()
    
    # Get the project root directory
    project_root = Path(__file__).parent.parent
    tests_dir = Path(__file__).parent
    src_dir = project_root / "src"
    
    # Check virtual environment setup
    venv_path = None
    python_exe = sys.executable
    
    if not args.no_venv:
        venv_path = check_venv_setup(project_root)
        if venv_path is None and not args.setup_venv:
            print(f"\n{'='*60}")
            print("❌ Virtual environment not properly set up!")
            print("Run one of the following:")
            print("  python setup_test_env.py")
            print("  python tests/run_tests.py --setup-venv")
            print("  python tests/run_tests.py --no-venv  # (not recommended)")
            print(f"{'='*60}")
            return 1
        elif venv_path:
            python_exe = str(get_venv_python(venv_path))
            print(f"✅ Using virtual environment Python: {python_exe}")
    
    # Set up virtual environment if requested
    if args.setup_venv:
        print("Setting up virtual environment...")
        setup_result = subprocess.run(
            [sys.executable, "setup_test_env.py"],
            cwd=project_root,
            check=False
        )
        if setup_result.returncode != 0:
            print("❌ Failed to set up virtual environment")
            return 1
        
        # Re-check virtual environment
        venv_path = check_venv_setup(project_root)
        if venv_path:
            python_exe = str(get_venv_python(venv_path))
        else:
            print("❌ Virtual environment setup failed")
            return 1
    
    # Add src to Python path
    sys.path.insert(0, str(src_dir))
    
    success = True
    
    # Code formatting
    if args.format or args.all:
        success &= run_command(
            [python_exe, "-m", "black", "--check", "--diff", str(src_dir)],
            "Code formatting check with black"
        )
        
        if not args.all:  # Only format if not running all checks
            success &= run_command(
                [python_exe, "-m", "black", str(src_dir)],
                "Code formatting with black"
            )
    
    # Linting
    if args.lint or args.all:
        success &= run_command(
            [python_exe, "-m", "flake8", str(src_dir)],
            "Linting with flake8"
        )
        
        success &= run_command(
            [python_exe, "-m", "mypy", str(src_dir)],
            "Type checking with mypy"
        )
    
    # Test execution
    if not (args.lint or args.format) or args.all:
        # Build pytest command
        cmd = [python_exe, "-m", "pytest"]
        
        if args.verbose:
            cmd.append("-v")
        
        if args.coverage:
            cmd.extend(["--cov=main", "--cov-report=html", "--cov-report=term"])
        
        if args.parallel > 1:
            cmd.extend(["-n", str(args.parallel)])
        
        # Test selection
        if args.unit and not args.integration:
            cmd.extend(["-m", "unit"])
        elif args.integration and not args.unit:
            cmd.extend(["-m", "integration"])
        elif not args.slow:
            cmd.extend(["-m", "not slow"])
        
        # Add test directory
        cmd.append(str(tests_dir))
        
        success &= run_command(cmd, "Running tests")
    
    # Summary
    print(f"\n{'='*60}")
    if success:
        print("✅ All checks passed!")
    else:
        print("❌ Some checks failed!")
    print(f"{'='*60}")
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
