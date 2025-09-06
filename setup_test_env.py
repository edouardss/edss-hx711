#!/usr/bin/env python3
"""
Virtual environment setup script for HX711 Loadcell component tests.
Creates and configures a virtual environment with all necessary dependencies.
"""

import os
import sys
import subprocess
import venv
from pathlib import Path
import argparse


def run_command(cmd, description, check=True, shell=False):
    """Run a command and handle errors."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(cmd) if isinstance(cmd, list) else cmd}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(
            cmd, 
            check=check, 
            capture_output=True, 
            text=True, 
            shell=shell
        )
        if result.stdout:
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


def create_virtual_environment(venv_path: Path, python_executable: str = None):
    """Create a virtual environment."""
    print(f"Creating virtual environment at: {venv_path}")
    
    if venv_path.exists():
        print(f"Virtual environment already exists at {venv_path}")
        return True
    
    try:
        venv.create(venv_path, with_pip=True, clear=True)
        print(f"✅ Virtual environment created successfully at {venv_path}")
        return True
    except Exception as e:
        print(f"❌ Failed to create virtual environment: {e}")
        return False


def get_venv_python(venv_path: Path) -> Path:
    """Get the Python executable path in the virtual environment."""
    if sys.platform == "win32":
        return venv_path / "Scripts" / "python.exe"
    else:
        return venv_path / "bin" / "python"


def get_venv_pip(venv_path: Path) -> Path:
    """Get the pip executable path in the virtual environment."""
    if sys.platform == "win32":
        return venv_path / "Scripts" / "pip.exe"
    else:
        return venv_path / "bin" / "pip"


def upgrade_pip(venv_path: Path):
    """Upgrade pip in the virtual environment."""
    python_exe = get_venv_python(venv_path)
    return run_command(
        [str(python_exe), "-m", "pip", "install", "--upgrade", "pip"],
        "Upgrading pip in virtual environment"
    )


def install_dependencies(venv_path: Path, requirements_files: list = None):
    """Install dependencies in the virtual environment."""
    if requirements_files is None:
        requirements_files = [
            "requirements.txt",
            "tests/requirements.txt"
        ]
    
    python_exe = get_venv_python(venv_path)
    
    # Raspberry Pi optimization: use --no-cache-dir for stability
    pip_args = ["-m", "pip", "install", "--no-cache-dir", "--upgrade"]
    
    for req_file in requirements_files:
        if Path(req_file).exists():
            print(f"Installing dependencies from {req_file}")
            cmd = [str(python_exe)] + pip_args + ["-r", req_file]
            success = run_command(
                cmd,
                f"Installing dependencies from {req_file}"
            )
            if not success:
                return False
        else:
            print(f"⚠️  Requirements file {req_file} not found, skipping")
    
    # Also install the package in development mode if pyproject.toml exists
    if Path("pyproject.toml").exists():
        cmd = [str(python_exe)] + pip_args + ["-e", "."]
        return run_command(
            cmd,
            "Installing package in development mode"
        )
    
    return True


def verify_installation(venv_path: Path):
    """Verify that the installation was successful."""
    python_exe = get_venv_python(venv_path)
    
    # Test imports
    test_imports = [
        "pytest",
        "pytest_asyncio", 
        "pytest_cov",
        "unittest.mock"
    ]
    
    for module in test_imports:
        success = run_command(
            [str(python_exe), "-c", f"import {module}; print(f'{module} imported successfully')"],
            f"Testing import of {module}",
            check=False
        )
        if not success:
            print(f"⚠️  Warning: {module} import test failed")
    
    # Test pytest version
    return run_command(
        [str(python_exe), "-m", "pytest", "--version"],
        "Verifying pytest installation"
    )


def create_activation_script(venv_path: Path):
    """Create activation script for easy environment activation."""
    if sys.platform == "win32":
        script_name = "activate_test_env.bat"
        script_content = f"""@echo off
echo Activating test environment...
call "{venv_path}\\Scripts\\activate.bat"
echo Test environment activated!
echo.
echo To run tests:
echo   pytest tests/
echo   python tests/run_tests.py
echo.
echo To deactivate:
echo   deactivate
"""
    else:
        script_name = "activate_test_env.sh"
        script_content = f"""#!/bin/bash
echo "Activating test environment..."
source "{venv_path}/bin/activate"
echo "Test environment activated!"
echo ""
echo "To run tests:"
echo "  pytest tests/"
echo "  python tests/run_tests.py"
echo ""
echo "To deactivate:"
echo "  deactivate"
"""
    
    script_path = Path(script_name)
    script_path.write_text(script_content)
    
    if not sys.platform == "win32":
        # Make executable on Unix systems
        os.chmod(script_path, 0o755)
    
    print(f"✅ Created activation script: {script_path}")
    return script_path


def main():
    """Main setup function."""
    parser = argparse.ArgumentParser(description="Set up test virtual environment")
    parser.add_argument(
        "--venv-path", 
        type=str, 
        default=".venv",
        help="Path for virtual environment (default: .venv)"
    )
    parser.add_argument(
        "--python", 
        type=str,
        help="Python executable to use for virtual environment"
    )
    parser.add_argument(
        "--skip-install", 
        action="store_true",
        help="Skip dependency installation"
    )
    parser.add_argument(
        "--force-recreate", 
        action="store_true",
        help="Force recreation of existing virtual environment"
    )
    
    args = parser.parse_args()
    
    # Get project root
    project_root = Path(__file__).parent.absolute()
    os.chdir(project_root)
    
    venv_path = Path(args.venv_path).resolve()
    
    print(f"Setting up test environment for HX711 Loadcell component")
    print(f"Project root: {project_root}")
    print(f"Virtual environment path: {venv_path}")
    
    # Force recreate if requested
    if args.force_recreate and venv_path.exists():
        print(f"Removing existing virtual environment at {venv_path}")
        import shutil
        shutil.rmtree(venv_path)
    
    # Create virtual environment
    if not create_virtual_environment(venv_path, args.python):
        return 1
    
    # Upgrade pip
    if not upgrade_pip(venv_path):
        print("⚠️  Warning: Failed to upgrade pip")
    
    # Install dependencies
    if not args.skip_install:
        if not install_dependencies(venv_path):
            print("❌ Failed to install dependencies")
            return 1
    
    # Verify installation
    if not args.skip_install:
        if not verify_installation(venv_path):
            print("⚠️  Warning: Installation verification failed")
    
    # Create activation script
    create_activation_script(venv_path)
    
    print(f"\n{'='*60}")
    print("✅ Test environment setup complete!")
    print(f"{'='*60}")
    print(f"Virtual environment location: {venv_path}")
    print(f"Python executable: {get_venv_python(venv_path)}")
    print(f"Pip executable: {get_venv_pip(venv_path)}")
    print(f"\nTo activate the environment:")
    if sys.platform == "win32":
        print(f"  {venv_path}\\Scripts\\activate.bat")
        print(f"  .\\activate_test_env.bat")
    else:
        print(f"  source {venv_path}/bin/activate")
        print(f"  source ./activate_test_env.sh")
    print(f"\nTo run tests:")
    print(f"  pytest tests/")
    print(f"  python tests/run_tests.py")
    print(f"{'='*60}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

