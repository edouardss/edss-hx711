@echo off
REM Test runner script for HX711 Loadcell component
REM Automatically sets up virtual environment and runs tests

setlocal enabledelayedexpansion

set PROJECT_ROOT=%~dp0
set PROJECT_ROOT=%PROJECT_ROOT:~0,-1%
set VENV_PATH=%PROJECT_ROOT%\.venv

echo ==========================================
echo HX711 Loadcell Component Test Runner
echo ==========================================
echo Project root: %PROJECT_ROOT%
echo Virtual environment: %VENV_PATH%
echo.

REM Function to check if virtual environment exists and is valid
call :check_venv
if errorlevel 1 goto venv_not_found

REM Run tests with provided arguments
echo Running tests...
echo Command: python tests/run_tests.py %*
echo.
cd /d "%PROJECT_ROOT%"
"%VENV_PATH%\Scripts\python.exe" tests/run_tests.py %*
goto end

:venv_not_found
echo ⚠️  Virtual environment not found or invalid
echo Setting up virtual environment...
cd /d "%PROJECT_ROOT%"
python setup_test_env.py --force-recreate
if errorlevel 1 (
    echo ❌ Error: Virtual environment setup failed
    exit /b 1
)
echo ✅ Virtual environment setup complete
echo.
echo Running tests...
"%VENV_PATH%\Scripts\python.exe" tests/run_tests.py %*
goto end

:check_venv
if not exist "%VENV_PATH%" exit /b 1
if not exist "%VENV_PATH%\Scripts\python.exe" exit /b 1
"%VENV_PATH%\Scripts\python.exe" -c "import pytest" >nul 2>&1
if errorlevel 1 exit /b 1
exit /b 0

:end
endlocal

