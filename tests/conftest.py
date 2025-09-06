"""
Pytest configuration and fixtures for Loadcell component tests.
"""

import pytest
from unittest.mock import patch, MagicMock
from typing import Mapping, Any

# Import the mock HX711 class
from tests.mock_hx711 import MockHX711, MockHX711Factory, SimulationMode


@pytest.fixture
def mock_hx711():
    """Fixture providing a basic MockHX711 instance."""
    return MockHX711(dout_pin=5, pd_sck_pin=6, channel='A', gain=64)


@pytest.fixture
def mock_hx711_normal():
    """Fixture providing a normal operating MockHX711."""
    return MockHX711Factory.create_normal(dout_pin=5, pd_sck_pin=6, gain=64)


@pytest.fixture
def mock_hx711_noisy():
    """Fixture providing a noisy MockHX711 for testing noise handling."""
    return MockHX711Factory.create_noisy(dout_pin=5, pd_sck_pin=6, gain=64)


@pytest.fixture
def mock_hx711_error_prone():
    """Fixture providing an error-prone MockHX711 for testing error handling."""
    return MockHX711Factory.create_error_prone(dout_pin=5, pd_sck_pin=6, gain=64)


@pytest.fixture
def mock_hx711_timeout_prone():
    """Fixture providing a timeout-prone MockHX711 for testing timeout handling."""
    return MockHX711Factory.create_timeout_prone(dout_pin=5, pd_sck_pin=6, gain=64)


@pytest.fixture
def mock_hx711_drifting():
    """Fixture providing a drifting MockHX711 for testing drift handling."""
    return MockHX711Factory.create_drifting(dout_pin=5, pd_sck_pin=6, gain=64)


@pytest.fixture
def loadcell_with_mock_hx711(mock_hx711):
    """Fixture providing Loadcell instance with mocked HX711."""
    with patch('main.HX711') as mock_hx711_class:
        mock_hx711_class.return_value = mock_hx711
        
        # Import here to avoid circular imports
        from main import Loadcell
        
        loadcell = Loadcell(name="test_loadcell")
        loadcell.doutPin = 5
        loadcell.sckPin = 6
        loadcell.gain = 64
        loadcell.numberOfReadings = 3
        loadcell.tare_offset = 0.0
        loadcell.logger = MagicMock()  # Mock logger
        
        yield loadcell


@pytest.fixture
def loadcell_with_normal_hx711(mock_hx711_normal):
    """Fixture providing Loadcell instance with normal MockHX711."""
    with patch('main.HX711') as mock_hx711_class:
        mock_hx711_class.return_value = mock_hx711_normal
        
        from main import Loadcell
        
        loadcell = Loadcell(name="test_loadcell")
        loadcell.doutPin = 5
        loadcell.sckPin = 6
        loadcell.gain = 64
        loadcell.numberOfReadings = 3
        loadcell.tare_offset = 0.0
        loadcell.logger = MagicMock()  # Mock logger
        
        yield loadcell


@pytest.fixture
def loadcell_with_error_prone_hx711(mock_hx711_error_prone):
    """Fixture providing Loadcell instance with error-prone MockHX711."""
    with patch('main.HX711') as mock_hx711_class:
        mock_hx711_class.return_value = mock_hx711_error_prone
        
        from main import Loadcell
        
        loadcell = Loadcell(name="test_loadcell")
        loadcell.doutPin = 5
        loadcell.sckPin = 6
        loadcell.gain = 64
        loadcell.numberOfReadings = 3
        loadcell.tare_offset = 0.0
        loadcell.logger = MagicMock()  # Mock logger
        
        yield loadcell


@pytest.fixture
def mock_gpio():
    """Fixture mocking RPi.GPIO."""
    with patch('main.GPIO') as mock_gpio:
        yield mock_gpio


@pytest.fixture
def mock_logger():
    """Fixture mocking Viam logger."""
    with patch('main.LOGGER') as mock_logger:
        yield mock_logger


@pytest.fixture
def valid_config():
    """Fixture providing a valid ComponentConfig."""
    config = MagicMock()
    config.attributes.fields = {
        "gain": MagicMock(HasField=lambda x: x == "number_value", number_value=64),
        "doutPin": MagicMock(HasField=lambda x: x == "number_value", number_value=5),
        "sckPin": MagicMock(HasField=lambda x: x == "number_value", number_value=6),
        "numberOfReadings": MagicMock(HasField=lambda x: x == "number_value", number_value=3),
        "tare_offset": MagicMock(HasField=lambda x: x == "number_value", number_value=0.0)
    }
    return config


@pytest.fixture
def invalid_config():
    """Fixture providing an invalid ComponentConfig."""
    config = MagicMock()
    config.attributes.fields = {
        "gain": MagicMock(HasField=lambda x: False)
    }
    return config


@pytest.fixture
def empty_config():
    """Fixture providing an empty ComponentConfig."""
    config = MagicMock()
    config.attributes.fields = {}
    return config


@pytest.fixture
def mock_dependencies():
    """Fixture providing empty dependencies mapping."""
    return {}


@pytest.fixture
def weight_scenarios():
    """Fixture providing various weight scenarios for testing."""
    return {
        "zero_weight": 0.0,
        "light_weight": 0.1,
        "normal_weight": 1.0,
        "heavy_weight": 10.0,
        "negative_weight": -0.5,
        "very_heavy_weight": 100.0
    }


@pytest.fixture
def noise_scenarios():
    """Fixture providing various noise scenarios for testing."""
    return {
        "no_noise": 0.0,
        "low_noise": 0.01,
        "medium_noise": 0.05,
        "high_noise": 0.1,
        "extreme_noise": 0.5
    }


@pytest.fixture
def error_scenarios():
    """Fixture providing various error scenarios for testing."""
    return {
        "initialization_error": Exception("Hardware initialization failed"),
        "communication_error": Exception("Communication timeout"),
        "data_error": Exception("Invalid data received"),
        "hardware_error": Exception("Hardware malfunction"),
        "timeout_error": TimeoutError("Operation timed out")
    }


# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on test names."""
    for item in items:
        # Add unit marker to all tests by default
        item.add_marker(pytest.mark.unit)
        
        # Add integration marker to integration tests
        if "integration" in item.name.lower():
            item.add_marker(pytest.mark.integration)
        
        # Add slow marker to slow tests
        if "slow" in item.name.lower() or "performance" in item.name.lower():
            item.add_marker(pytest.mark.slow)
