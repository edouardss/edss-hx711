"""Simplified test fixtures for HX711 loadcell tests"""

import pytest
from unittest.mock import Mock, patch
from viam.proto.app.robot import ComponentConfig
from google.protobuf.struct_pb2 import Struct


@pytest.fixture
def mock_hx711():
    """Mock the HX711 library with realistic default values"""
    with patch("src.models.loadcell.HX711") as mock_class:
        mock_instance = Mock()
        mock_class.return_value = mock_instance
        
        # Realistic default sensor readings (approximately 10kg)
        mock_instance.get_raw_data.return_value = [82000.0, 82100.0, 81900.0]
        mock_instance.reset.return_value = None
        
        yield mock_instance


@pytest.fixture
def mock_gpio():
    """Mock RPi.GPIO operations"""
    with patch("src.models.loadcell.GPIO") as mock:
        yield mock


@pytest.fixture
def sensor_config():
    """Standard sensor configuration for testing"""
    config = ComponentConfig()
    config.name = "test_loadcell"
    
    attributes = Struct()
    attributes.fields["gain"].number_value = 128
    attributes.fields["doutPin"].number_value = 5
    attributes.fields["sckPin"].number_value = 6
    attributes.fields["numberOfReadings"].number_value = 3
    attributes.fields["tare_offset"].number_value = 0.0
    
    config.attributes.CopyFrom(attributes)
    return config


@pytest.fixture
def loadcell_sensor(sensor_config, mock_hx711, mock_gpio):
    """Pre-configured loadcell sensor with mocked hardware"""
    from src.main import Loadcell
    
    sensor = Loadcell.new(sensor_config, dependencies={})
    sensor.hx711 = mock_hx711
    sensor.reconfigure(sensor_config, dependencies={})
    
    yield sensor
    
    # Cleanup after test
    try:
        sensor.close()
    except:
        pass
