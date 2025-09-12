# GitHub Actions CI/CD

This repository uses GitHub Actions for continuous integration and deployment.

## Workflows

### Tests (`tests.yml`)
Runs on every push and pull request to `main` and `develop` branches.

**Features:**
- **Raspberry Pi focused**: Ubuntu Linux only (simulates Raspberry Pi environment)
- **Multi-version Python**: 3.9, 3.10, 3.11, 3.12 (common on Raspberry Pi)
- **Comprehensive test suite**:
  - Unit tests (61 tests)
  - Integration tests (10 tests)
  - Linting checks (flake8)
  - Code formatting checks (black)
- **Coverage reporting** with Codecov integration
- **Security scanning** with safety and bandit

**Test Categories:**
- ✅ **Unit Tests**: Fast, isolated tests with mocks
- ✅ **Integration Tests**: End-to-end functionality tests
- ⏭️ **Hardware Tests**: Skipped (require real HX711 hardware)

### Deploy (`deploy.yml`)
Runs on version tags (e.g., `v1.0.0`) to build and deploy the Viam module.

## Local Development

### Running Tests Locally

```bash
# Set up test environment
python setup_test_env.py --force-recreate

# Activate virtual environment
source .venv/bin/activate  # Linux/macOS
# or
.venv\Scripts\activate     # Windows

# Run all tests
python tests/run_tests.py --all

# Run specific test categories
python tests/run_tests.py --unit --verbose
python tests/run_tests.py --integration --verbose
python tests/run_tests.py --lint
python tests/run_tests.py --format
```

### Test Script Options

- `--unit`: Run unit tests only
- `--integration`: Run integration tests only
- `--lint`: Run linting checks (flake8)
- `--format`: Run code formatting checks (black)
- `--coverage`: Generate coverage report
- `--verbose`: Verbose output
- `--all`: Run all tests and checks

## Raspberry Pi Specific

This module is designed specifically for Raspberry Pi hardware and uses:
- **GPIO pins** for HX711 load cell communication
- **RPi.GPIO library** for hardware control
- **HX711 library** for load cell data acquisition

## Validation Rules

The test suite validates the following configuration constraints:

- **Gain**: Must be exactly 32, 64, or 128
- **GPIO Pins**: Must be valid Raspberry Pi pins (1-40)
- **Number of Readings**: Must be positive integer less than 100
- **Tare Offset**: Must be non-positive (≤ 0.0)

## Coverage

Coverage reports are generated for Python 3.11 and uploaded to Codecov.
