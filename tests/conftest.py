# Copy the content from the conftest.py artifact I provided above
# tests/conftest.py
"""Shared test fixtures for HX711 loadcell tests"""

import pytest
from unittest.mock import Mock, patch
from viam.proto.app.robot import ComponentConfig
from google.protobuf.struct_pb2 import Struct


@pytest.fixture
def mock_hx711_library():
    """Mock the HX711 library that your module imports"""
    with patch('src.main.HX711') as mock_class:
        mock_instance = Mock()
        mock_class.return_value = mock_instance
        
        # Default behavior for HX711 instance
        mock_instance.get_raw_data.return_value = [82000.0, 82100.3, 81900.2]
        mock_instance.reset.return_value = None
        
        yield mock_class, mock_instance


@pytest.fixture  
def mock_gpio():
    """Mock RPi.GPIO"""
    with patch('src.main.GPIO') as mock:
        yield mock


@pytest.fixture
def basic_config():
    """Create a basic ComponentConfig for testing"""
    config = ComponentConfig()
    config.name = "test_loadcell"
    
    # Create the protobuf structure that Viam uses
    attributes = Struct()
    attributes.fields["gain"].number_value = 128
    attributes.fields["doutPin"].number_value = 5
    attributes.fields["sckPin"].number_value = 6
    attributes.fields["numberOfReadings"].number_value = 3
    attributes.fields["tare_offset"].number_value = 0.0
    
    config.attributes.CopyFrom(attributes)
    return config


@pytest.fixture
def minimal_config():
    """Create config with minimal attributes (tests defaults)"""
    config = ComponentConfig()
    config.name = "minimal_test_loadcell"
    config.attributes.CopyFrom(Struct())  # Empty attributes
    return config


@pytest.fixture
def loadcell_sensor(basic_config, mock_hx711_library, mock_gpio):
    """Create a Loadcell sensor instance with mocked dependencies"""
    from main import Loadcell
    
    mock_class, mock_instance = mock_hx711_library
    sensor = Loadcell.new(basic_config, dependencies={})
    return sensor


@pytest.fixture(autouse=True)
def reset_module_state():
    """Reset any module-level state between tests"""
    yield
    # Add any cleanup needed between tests
    pass