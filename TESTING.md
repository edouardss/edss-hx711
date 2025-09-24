# Testing Guide

## Quick Start

```bash
# Clean up PATH if needed (removes duplicates)
./clean_path.sh

# Run all tests
python test.py

# Run with coverage report
python test.py --coverage

# Run hardware tests (requires HARDWARE_TESTS_ENABLED=true)
python test.py --hardware

# Run specific test file
python test.py tests/test_loadcell.py
```

## Test Structure

- **`tests/test_loadcell.py`** - Unit tests for loadcell functionality
- **`tests/conftest.py`** - Shared test fixtures and configuration
- **`test.py`** - Single test runner script

## Test Categories

### Unit Tests (Default)
- Configuration validation
- Weight calculations
- Tare functionality
- Viam interface compliance
- Error handling

### Hardware Tests (Optional)
- Real sensor connectivity
- Physical hardware validation

Enable with: `HARDWARE_TESTS_ENABLED=true python test.py --hardware`

## Configuration

All testing configuration is consolidated in `pyproject.toml`:
- Pytest settings
- Coverage configuration
- Test markers
- Dependencies

## Dependencies

Development dependencies are managed through `pyproject.toml` optional dependencies:
```bash
pip install -e .[test]  # Install test dependencies
```

## Troubleshooting

### PATH Issues
If you have duplicate PATH entries (common after multiple `source venv/bin/activate` calls):
```bash
./clean_path.sh  # Clean up duplicate PATH entries
```

### Virtual Environment
Use the clean activation script to avoid PATH duplication:
```bash
./activate_clean.sh  # Instead of source venv/bin/activate
```

## Coverage

Generate HTML coverage reports:
```bash
python test.py --coverage
```

Reports are saved to `htmlcov/index.html`
