# HX711 Loadcell Component Tests

This directory contains comprehensive unit tests for the HX711 Loadcell Viam component.

## Test Structure

```
tests/
├── README.md                 # This file
├── conftest.py              # Pytest configuration and fixtures
├── mock_hx711.py            # Mock HX711 simulation class
├── test_loadcell.py         # Main test file
├── requirements.txt         # Test dependencies
└── run_tests.py            # Test runner script
```

## Mock HX711 Simulation

The `MockHX711` class simulates realistic HX711 load cell behavior without requiring actual hardware:

### Features
- **Realistic Data**: Generates realistic 24-bit signed integer readings
- **Multiple Modes**: Normal, noisy, error-prone, timeout-prone, drifting
- **Configurable Parameters**: Weight, noise level, error probability, etc.
- **State Tracking**: Tracks reset state, call counts, and configuration
- **Error Simulation**: Can simulate various hardware failure modes

### Usage Example
```python
from tests.mock_hx711 import MockHX711, SimulationMode

# Create a normal operating mock
mock_hx711 = MockHX711(dout_pin=5, pd_sck_pin=6, channel='A', gain=64)

# Set simulated weight
mock_hx711.set_simulated_weight(1.0)  # 1kg

# Get readings
readings = mock_hx711.get_raw_data(times=3)
```

## Test Categories

### 1. Configuration Tests
- Valid configuration validation
- Invalid parameter handling
- Default value assignment

### 2. HX711 Management Tests
- Object creation and reuse
- Error handling during initialization
- Resource cleanup

### 3. GPIO Tests
- Pin cleanup functionality
- Error handling

### 4. Lifecycle Tests
- Component initialization
- Resource cleanup on close
- State management

### 5. Reading Tests
- Successful reading operations
- Data calculation accuracy
- Tare offset application
- Error handling and recovery

### 6. Tare Tests
- Tare operation success
- Offset calculation accuracy
- Error handling

### 7. Command Tests
- Command processing
- Unknown command handling
- Multiple command support

### 8. Integration Tests
- Complete workflows
- Error recovery
- State consistency

### 9. Edge Case Tests
- Division by zero protection
- Negative measurements
- Extreme values
- Memory management

## Running Tests

### Prerequisites
Install test dependencies:
```bash
pip install -r tests/requirements.txt
```

### Basic Test Execution
```bash
# Run all tests
python tests/run_tests.py

# Run only unit tests
python tests/run_tests.py --unit

# Run with coverage
python tests/run_tests.py --coverage

# Run in parallel
python tests/run_tests.py --parallel 4

# Verbose output
python tests/run_tests.py --verbose
```

### Using pytest directly
```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_loadcell.py

# Run specific test class
pytest tests/test_loadcell.py::TestLoadcellReadings

# Run specific test method
pytest tests/test_loadcell.py::TestLoadcellReadings::test_get_readings_success

# Run with coverage
pytest --cov=main tests/

# Run in parallel
pytest -n 4 tests/
```

### Test Selection
```bash
# Run only unit tests
pytest -m unit tests/

# Run only integration tests
pytest -m integration tests/

# Skip slow tests
pytest -m "not slow" tests/

# Run specific markers
pytest -m "unit and not slow" tests/
```

## Code Quality Checks

### Linting
```bash
# Run linting checks
python tests/run_tests.py --lint

# Or directly
flake8 src/
mypy src/
```

### Code Formatting
```bash
# Check formatting
python tests/run_tests.py --format

# Format code
black src/
```

### All Checks
```bash
# Run all checks (tests, lint, format)
python tests/run_tests.py --all
```

## Test Fixtures

The `conftest.py` file provides several useful fixtures:

- `mock_hx711`: Basic MockHX711 instance
- `mock_hx711_normal`: Normal operating mode
- `mock_hx711_noisy`: Noisy readings mode
- `mock_hx711_error_prone`: Error-prone mode
- `loadcell_with_mock_hx711`: Loadcell with mocked HX711
- `mock_gpio`: Mocked GPIO module
- `valid_config`: Valid ComponentConfig
- `weight_scenarios`: Various weight test scenarios

## Test Data

### Weight Scenarios
- Zero weight (0.0 kg)
- Light weight (0.1 kg)
- Normal weight (1.0 kg)
- Heavy weight (10.0 kg)
- Negative weight (-0.5 kg)
- Very heavy weight (100.0 kg)

### Noise Scenarios
- No noise (0.0)
- Low noise (1%)
- Medium noise (5%)
- High noise (10%)
- Extreme noise (50%)

### Error Scenarios
- Initialization errors
- Communication timeouts
- Invalid data
- Hardware malfunctions

## Coverage

The tests aim for comprehensive coverage of:
- All public methods
- Error handling paths
- Edge cases
- Resource management
- State transitions

Run with coverage to see detailed coverage reports:
```bash
python tests/run_tests.py --coverage
```

## Continuous Integration

These tests are designed to run in CI/CD environments:
- No hardware dependencies
- Fast execution
- Deterministic results
- Comprehensive error coverage

## Debugging Tests

### Verbose Output
```bash
pytest -v tests/
```

### Debug Mode
```bash
pytest --pdb tests/
```

### Specific Test Debugging
```bash
pytest -v -s tests/test_loadcell.py::TestLoadcellReadings::test_get_readings_success
```

## Contributing

When adding new tests:
1. Follow the existing naming conventions
2. Use appropriate fixtures
3. Add docstrings explaining test purpose
4. Include both positive and negative test cases
5. Test edge cases and error conditions
6. Update this README if adding new test categories
