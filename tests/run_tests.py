#!/usr/bin/env python3
"""
Test runner script for GitHub Actions
Supports unit tests, integration tests, linting, and formatting checks
"""

import argparse
import subprocess
import sys
from pathlib import Path


def run_command(cmd, description):
    """Run a command and return success status"""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(cmd)}")
    print(f"{'='*60}")

    result = subprocess.run(cmd, cwd=Path(__file__).parent.parent)
    return result.returncode == 0


def run_unit_tests(coverage=False, verbose=False):
    """Run unit tests with optional coverage"""
    cmd = [sys.executable, "-m", "pytest", "tests/test_loadcell.py"]

    if verbose:
        cmd.append("-v")

    if coverage:
        cmd.extend(["--cov=src", "--cov-report=html", "--cov-report=xml"])

    return run_command(cmd, "Unit Tests")


def run_integration_tests(verbose=False):
    """Run integration tests"""
    cmd = [sys.executable, "-m", "pytest", "tests/test_integration.py"]

    if verbose:
        cmd.append("-v")

    return run_command(cmd, "Integration Tests")


def run_linting():
    """Run linting checks"""
    cmd = [sys.executable, "-m", "flake8", "src/", "tests/"]
    return run_command(cmd, "Linting Checks")


def run_formatting():
    """Run code formatting checks"""
    cmd = [sys.executable, "-m", "black", "--check", "src/", "tests/"]
    return run_command(cmd, "Code Formatting Checks")


def main():
    parser = argparse.ArgumentParser(description="Run tests and checks")
    parser.add_argument("--unit", action="store_true", help="Run unit tests")
    parser.add_argument(
        "--integration", action="store_true", help="Run integration tests"
    )
    parser.add_argument("--lint", action="store_true", help="Run linting checks")
    parser.add_argument("--format", action="store_true", help="Run formatting checks")
    parser.add_argument(
        "--coverage", action="store_true", help="Generate coverage report"
    )
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--all", action="store_true", help="Run all tests and checks")

    args = parser.parse_args()

    # If no specific tests requested, run all
    if not any([args.unit, args.integration, args.lint, args.format]):
        args.all = True

    success = True

    if args.all or args.unit:
        success &= run_unit_tests(coverage=args.coverage, verbose=args.verbose)

    if args.all or args.integration:
        success &= run_integration_tests(verbose=args.verbose)

    if args.all or args.lint:
        success &= run_linting()

    if args.all or args.format:
        success &= run_formatting()

    if success:
        print(f"\n{'='*60}")
        print("✅ All tests and checks passed!")
        print(f"{'='*60}")
        sys.exit(0)
    else:
        print(f"\n{'='*60}")
        print("❌ Some tests or checks failed!")
        print(f"{'='*60}")
        sys.exit(1)


if __name__ == "__main__":
    main()
