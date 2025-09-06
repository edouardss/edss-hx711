# Testing Guide for HX711 Loadcell Component

This guide covers testing the HX711 Loadcell component on Raspberry Pi systems.

## System Requirements

- **Hardware**: Raspberry Pi 4 (tested on aarch64)
- **OS**: Raspberry Pi OS (Debian-based Linux)
- **Python**: 3.8+ (tested with Python 3.11.2)
- **Architecture**: ARM64 (aarch64)

## Quick Start

### Option 1: Automated Setup (Recommended)
```bash
# Set up virtual environment and run tests
./test.sh

# Or with specific options
./test.sh --coverage
./test.sh --unit --verbose
```

### Option 2: Manual Setup
```bash
# Set up virtual environment
python3 setup_test_env.py

# Run tests
python3 tests/run_tests.py
```

## Virtual Environment Setup

The testing framework automatically manages virtual environments to ensure:
- Isolated dependency management
- Consistent Python versions
- Clean test environments
- Raspberry Pi optimizations

### Automatic Setup
```bash
# Set up virtual environment
python3 setup_test_env.py

# Set up and run tests in one command
python3 tests/run_tests.py --setup-venv
```

### Manual Virtual Environment
```bash
# Create virtual environment
python3 -m venv .venv

# Activate
source .venv/bin/activate  # Linux/macOS
# or
.venv\Scripts\activate.bat  # Windows

# Install dependencies
pip install --no-cache-dir -r requirements.txt
pip install --no-cache-dir -r tests/requirements.txt
```

## Raspberry Pi Specific Considerations

### Dependencies
- **RPi.GPIO**: Only available on Raspberry Pi systems
- **hx711**: Hardware-specific library for load cell communication
- **Version pinning**: Dependencies are pinned for stability on ARM architecture

### Performance Optimizations
- Uses `--no-cache-dir` for pip installations to avoid storage issues
- Pinned dependency versions to prevent ARM compilation issues
- Optimized test execution for single-core ARM processors

### Hardware Dependencies
The component requires:
- HX711 load cell amplifier
- Proper GPIO connections (DOUT and SCK pins)
- Raspberry Pi GPIO access

**Note**: Tests use mock hardware to avoid requiring actual load cell hardware.

## Test Categories

### Unit Tests (`--unit`)
- Component configuration validation
- HX711 object management
- GPIO cleanup functionality
- Sensor reading calculations
- Tare operations
- Error handling

### Integration Tests (`--integration`)
- Complete workflow testing
- Error recovery scenarios
- State consistency checks
- Hardware simulation

### Coverage Testing (`--coverage`)
- Code coverage analysis
- HTML coverage reports
- Missing test identification

## Running Tests

### Basic Test Execution
```bash
# Run all tests
./test.sh

# Run with coverage
./test.sh --coverage

# Run only unit tests
./test.sh --unit

# Run only integration tests
./test.sh --integration

# Verbose output
./test.sh --verbose
```

### Advanced Options
```bash
# Run tests in parallel (limited on Pi)
./test.sh --parallel 2

# Run linting checks
./test.sh --lint

# Run code formatting checks
./test.sh --format

# Run all checks
./test.sh --all
```

### Direct pytest Usage
```bash
# Activate virtual environment
source .venv/bin/activate

# Run specific test file
pytest tests/test_loadcell.py

# Run specific test class
pytest tests/test_loadcell.py::TestLoadcellReadings

# Run with coverage
pytest --cov=main tests/

# Run in parallel (use 1-2 workers on Pi)
pytest -n 2 tests/
```

## Mock Hardware Testing

The test suite includes comprehensive mock hardware simulation:

### MockHX711 Features
- Realistic 24-bit load cell readings
- Configurable weight simulation
- Noise and drift simulation
- Error condition simulation
- Performance testing capabilities

### Simulation Modes
- **Normal**: Standard operation with minimal noise
- **Noisy**: High noise conditions
- **Error-prone**: Simulated hardware failures
- **Timeout-prone**: Communication timeout simulation
- **Drifting**: Temperature and time-based drift

### Example Usage
```python
from tests.mock_hx711 import MockHX711, SimulationMode

# Create mock with specific weight
mock = MockHX711(dout_pin=5, pd_sck_pin=6, gain=64)
mock.set_simulated_weight(1.0)  # 1kg

# Get readings
readings = mock.get_raw_data(times=3)
```

## Continuous Integration

### GitHub Actions
The project includes GitHub Actions workflows for:
- Multi-Python version testing (3.8, 3.9, 3.10, 3.11)
- Cross-platform testing (Linux, Windows, macOS)
- Security scanning
- Coverage reporting

### Local CI Simulation
```bash
# Run all CI checks locally
./test.sh --all

# Run security scans
pip install safety bandit
safety check -r requirements.txt -r tests/requirements.txt
bandit -r src/
```

## Troubleshooting

### Common Issues

#### Virtual Environment Problems
```bash
# Clean and recreate virtual environment
rm -rf .venv
python3 setup_test_env.py --force-recreate
```

#### Dependency Installation Issues
```bash
# Install with verbose output
pip install -v --no-cache-dir -r tests/requirements.txt

# Install system dependencies first
sudo apt-get update
sudo apt-get install python3-dev build-essential
```

#### Permission Issues
```bash
# Fix script permissions
chmod +x test.sh
chmod +x setup_test_env.py
```

#### Memory Issues on Pi
```bash
# Increase swap space
sudo dphys-swapfile swapoff
sudo nano /etc/dphys-swapfile
# Set CONF_SWAPSIZE=2048
sudo dphys-swapfile setup
sudo dphys-swapfile swapon
```

### Performance Tips

1. **Use SSD storage** for faster test execution
2. **Limit parallel workers** to 1-2 on Pi 4
3. **Close unnecessary applications** during testing
4. **Use `--no-cache-dir`** for pip installations
5. **Consider running tests overnight** for large test suites

### Debugging Tests

```bash
# Run specific test with debugging
pytest -v -s tests/test_loadcell.py::TestLoadcellReadings::test_get_readings_success

# Run with pdb debugger
pytest --pdb tests/

# Run with maximum verbosity
pytest -vvv tests/

# Run with logging
pytest --log-cli-level=DEBUG tests/
```

## Test Data and Scenarios

### Weight Scenarios
- Zero weight (0.0 kg)
- Light weight (0.1 kg)
- Normal weight (1.0 kg)
- Heavy weight (10.0 kg)
- Negative weight (-0.5 kg)
- Very heavy weight (100.0 kg)

### Error Scenarios
- Hardware initialization failures
- Communication timeouts
- Invalid data conditions
- GPIO access errors
- Resource cleanup failures

### Performance Scenarios
- High-frequency readings
- Long-running operations
- Memory usage patterns
- CPU utilization

## Contributing

When adding new tests:

1. **Follow naming conventions**: `test_*` for functions, `Test*` for classes
2. **Use appropriate fixtures**: Leverage existing mock objects
3. **Add docstrings**: Explain test purpose and scenarios
4. **Test edge cases**: Include error conditions and boundary values
5. **Consider Pi performance**: Avoid resource-intensive tests
6. **Update documentation**: Keep this guide current

## Support

For issues specific to Raspberry Pi testing:
- Check system logs: `journalctl -u python3`
- Monitor system resources: `htop` or `top`
- Verify GPIO permissions: `groups $USER`
- Check Python version: `python3 --version`

For general testing issues, refer to the main project documentation.
