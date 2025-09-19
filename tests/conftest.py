# Copy the content from the conftest.py artifact I provided above
# tests/conftest.py
"""Shared test fixtures for HX711 loadcell tests"""

import pytest
from unittest.mock import Mock, patch
from viam.proto.app.robot import ComponentConfig
from google.protobuf.struct_pb2 import Struct
from viam.resource.registry import Registry
import os

# Note: We'll handle registration clearing in fixtures instead


@pytest.fixture(scope="session", autouse=True)
def clear_registry_session():
    """Clear the Viam resource registry at the start of the test session"""
    Registry._REGISTRY.clear()
    yield
    Registry._REGISTRY.clear()


@pytest.fixture(autouse=True)
def prevent_auto_registration():
    """Prevent automatic model registration during tests"""
    # Clear registry before each test to prevent duplicates
    Registry._REGISTRY.clear()
    
    # Patch the registry to ignore duplicate registrations during tests
    original_register = Registry.register
    
    def safe_register(resource_type, resource_class):
        """Register resource but ignore duplicates during tests"""
        try:
            return original_register(resource_type, resource_class)
        except Exception as e:
            if "duplicate" in str(e).lower():
                # Ignore duplicate registration errors during tests
                pass
            else:
                raise e
    
    Registry.register = safe_register
    
    yield
    
    # Restore original register method
    Registry.register = original_register
    # Clear registry after each test
    Registry._REGISTRY.clear()


@pytest.fixture
def mock_hx711_library():
    """Mock the HX711 library that your module imports"""
    with patch("src.models.loadcell.HX711") as mock_class:
        mock_instance = Mock()
        mock_class.return_value = mock_instance

        # Default behavior for HX711 instance
        mock_instance.get_raw_data.return_value = [82000.0, 82100.3, 81900.2]
        mock_instance.reset.return_value = None

        yield mock_class, mock_instance


@pytest.fixture
def mock_gpio():
    """Mock RPi.GPIO"""
    with patch("src.models.loadcell.GPIO") as mock:
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
    from src.main import Loadcell

    mock_class, mock_instance = mock_hx711_library
    sensor = Loadcell.new(basic_config, dependencies={})
    return sensor


