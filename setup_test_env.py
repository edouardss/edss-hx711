#!/usr/bin/env python3
"""
Setup script for test environment
Creates virtual environment and installs dependencies
"""

import argparse
import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, description):
    """Run a command and return success status"""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(cmd)}")
    print(f"{'='*60}")
    
    result = subprocess.run(cmd)
    return result.returncode == 0

def setup_virtual_environment(force_recreate=False):
    """Set up Python virtual environment"""
    venv_path = Path(".venv")
    
    if force_recreate and venv_path.exists():
        print("Removing existing virtual environment...")
        import shutil
        shutil.rmtree(venv_path)
    
    if not venv_path.exists():
        print("Creating virtual environment...")
        if not run_command([sys.executable, "-m", "venv", ".venv"], "Creating virtual environment"):
            return False
    
    return True

def install_dependencies():
    """Install project dependencies"""
    # Determine the correct pip path based on OS
    if os.name == 'nt':  # Windows
        pip_path = ".venv/Scripts/pip"
    else:  # Unix-like (Linux, macOS)
        pip_path = ".venv/bin/pip"
    
    # Upgrade pip first
    if not run_command([pip_path, "install", "--upgrade", "pip"], "Upgrading pip"):
        return False
    
    # Install production dependencies
    if not run_command([pip_path, "install", "-r", "requirements.txt"], "Installing production dependencies"):
        return False
    
    # Install development dependencies
    if not run_command([pip_path, "install", "-r", "requirements-dev.txt"], "Installing development dependencies"):
        return False
    
    return True

def main():
    parser = argparse.ArgumentParser(description="Set up test environment")
    parser.add_argument("--force-recreate", action="store_true", 
                       help="Force recreation of virtual environment")
    
    args = parser.parse_args()
    
    print("Setting up test environment...")
    
    # Set up virtual environment
    if not setup_virtual_environment(force_recreate=args.force_recreate):
        print("❌ Failed to set up virtual environment")
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Failed to install dependencies")
        sys.exit(1)
    
    print(f"\n{'='*60}")
    print("✅ Test environment setup complete!")
    print("Virtual environment: .venv/")
    print("To activate: source .venv/bin/activate (Linux/macOS) or .venv\\Scripts\\activate (Windows)")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
