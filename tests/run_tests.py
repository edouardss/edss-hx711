#!/usr/bin/env python3
"""
Test runner script for HX711 Loadcell component tests.
Provides various test execution options and configurations.
"""

import sys
import os
import subprocess
import argparse
from pathlib import Path


def run_command(cmd, description):
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
    
    args = parser.parse_args()
    
    # Get the project root directory
    project_root = Path(__file__).parent.parent
    tests_dir = Path(__file__).parent
    src_dir = project_root / "src"
    
    # Add src to Python path
    sys.path.insert(0, str(src_dir))
    
    success = True
    
    # Code formatting
    if args.format or args.all:
        success &= run_command(
            ["black", "--check", "--diff", str(src_dir)],
            "Code formatting check with black"
        )
        
        if not args.all:  # Only format if not running all checks
            success &= run_command(
                ["black", str(src_dir)],
                "Code formatting with black"
            )
    
    # Linting
    if args.lint or args.all:
        success &= run_command(
            ["flake8", str(src_dir)],
            "Linting with flake8"
        )
        
        success &= run_command(
            ["mypy", str(src_dir)],
            "Type checking with mypy"
        )
    
    # Test execution
    if not (args.lint or args.format) or args.all:
        # Build pytest command
        cmd = ["python", "-m", "pytest"]
        
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
