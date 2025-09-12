# Copy the content from the test_loadcell.py artifact I provided above
# tests/test_loadcell.py
"""Unit tests for HX711 Loadcell Viam module"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import asyncio
from viam.proto.app.robot import ComponentConfig
from google.protobuf.struct_pb2 import Struct
from google.protobuf.struct_pb2 import Value
from viam.resource.types import Model, ModelFamily

# Import your module - adjust if your structure is different
from src.main import Loadcell


class TestLoadcellBasics:
    """Test basic functionality and configuration"""
    
    def test_model_definition(self):
        """Test that the model is properly defined"""
        expected_model = Model(ModelFamily("edss", "hx711-loadcell"), "loadcell")
        assert Loadcell.MODEL == expected_model
    
    def test_validate_config_valid(self, basic_config):
        """Test config validation with valid configuration"""
        errors = Loadcell.validate_config(basic_config)
        assert errors == []
    
    @pytest.mark.parametrize("field,expected_error", [
        ("gain", "Gain must be a valid number"),
        ("doutPin", "Data Out pin must be a valid number"), 
        ("sckPin", "Clock pin must be a valid number"),
        ("numberOfReadings", "Number of readings must be a valid number"),
        ("tare_offset", "Tare offset must be a valid number"),
    ])
    def test_validate_config_invalid_type(self, field, expected_error):
        """Test config validation with invalid data types"""
        config = ComponentConfig()
        config.name = "test_loadcell"
        
        attributes = Struct()
        attributes.fields[field].string_value = "invalid_string"  # Wrong type
        config.attributes.CopyFrom(attributes)
        
        with pytest.raises(Exception, match=expected_error):
            Loadcell.validate_config(config)
    
    @pytest.mark.parametrize("gain_value,should_pass", [
        (32, True),
        (64, True), 
        (128, True),
        (16, False),
        (256, False),
        (0, False),
        (-1, False),
    ])
    def test_validate_gain_values(self, gain_value, should_pass):
        """Test gain validation with specific values"""
        config = ComponentConfig()
        config.name = "test_loadcell"
        
        attributes = Struct()
        attributes.fields["gain"].number_value = gain_value
        config.attributes.CopyFrom(attributes)
        
        if should_pass:
            # Should not raise exception
            Loadcell.validate_config(config)
        else:
            with pytest.raises(Exception, match="Gain must be 32, 64, or 128"):
                Loadcell.validate_config(config)
    
    @pytest.mark.parametrize("pin_value,should_pass", [
        (1, True),
        (40, True),
        (5, True),
        (6, True),
        (0, False),
        (41, False),
        (-1, False),
        (100, False),
    ])
    def test_validate_pin_values(self, pin_value, should_pass):
        """Test GPIO pin validation"""
        config = ComponentConfig()
        config.name = "test_loadcell"
        
        # Test doutPin
        attributes = Struct()
        attributes.fields["doutPin"].number_value = pin_value
        config.attributes.CopyFrom(attributes)
        
        if should_pass:
            Loadcell.validate_config(config)
        else:
            with pytest.raises(Exception, match="Data Out pin must be a valid GPIO pin number"):
                Loadcell.validate_config(config)
    
    @pytest.mark.parametrize("num_readings,should_pass", [
        (1, True),
        (50, True),
        (99, True),
        (0, False),
        (100, False),
        (-1, False),
        (200, False),
    ])
    def test_validate_number_of_readings(self, num_readings, should_pass):
        """Test numberOfReadings validation"""
        config = ComponentConfig()
        config.name = "test_loadcell"
        
        attributes = Struct()
        attributes.fields["numberOfReadings"].number_value = num_readings
        config.attributes.CopyFrom(attributes)
        
        if should_pass:
            Loadcell.validate_config(config)
        else:
            with pytest.raises(Exception, match="Number of readings must be a positive integer less than 100"):
                Loadcell.validate_config(config)
    
    @pytest.mark.parametrize("tare_offset,should_pass", [
        (-1.0, True),
        (-100.5, True),
        (-0.1, True),
        (0.0, True),
        (1.0, False),
        (100.0, False),
    ])
    def test_validate_tare_offset(self, tare_offset, should_pass):
        """Test tare_offset validation"""
        config = ComponentConfig()
        config.name = "test_loadcell"
        
        attributes = Struct()
        attributes.fields["tare_offset"].number_value = tare_offset
        config.attributes.CopyFrom(attributes)
        
        if should_pass:
            Loadcell.validate_config(config)
        else:
            with pytest.raises(Exception, match="Tare offset must be a non-positive floating point value \\(≤ 0\\.0\\)"):
                Loadcell.validate_config(config)
    
    def test_reconfigure_with_all_attributes(self, loadcell_sensor):
        """Test sensor reconfiguration with all attributes set"""
        assert loadcell_sensor.gain == 128
        assert loadcell_sensor.doutPin == 5
        assert loadcell_sensor.sckPin == 6
        assert loadcell_sensor.numberOfReadings == 3
        assert loadcell_sensor.tare_offset == 0.0
    
    def test_reconfigure_with_defaults(self, minimal_config, mock_hx711_library, mock_gpio):
        """Test reconfiguration uses default values when attributes missing"""
        mock_class, mock_instance = mock_hx711_library
        sensor = Loadcell.new(minimal_config, dependencies={})
        
        # Should use defaults from your code
        assert sensor.gain == 64.0    # Default from your code
        assert sensor.doutPin == 5     # Default
        assert sensor.sckPin == 6      # Default  
        assert sensor.numberOfReadings == 3  # Default
        assert sensor.tare_offset == 0.0     # Default


class TestHX711Hardware:
    """Test HX711 hardware interaction (mocked)"""
    
    def test_get_hx711_initialization(self, loadcell_sensor, mock_hx711_library):
        """Test HX711 initialization"""
        mock_class, mock_instance = mock_hx711_library
        
        # Reset mock call counts to start fresh
        mock_class.reset_mock()
        mock_instance.reset_mock()
        
        # Force re-initialization by setting hx711 to None
        loadcell_sensor.hx711 = None
        
        hx711 = loadcell_sensor.get_hx711()
        
        # Verify HX711 was created with correct parameters
        mock_class.assert_called_with(
            dout_pin=5,
            pd_sck_pin=6,
            channel='A',
            gain=128
        )
        mock_instance.reset.assert_called_once()
        assert hx711 == mock_instance
    
    def test_get_hx711_reuse_existing(self, loadcell_sensor, mock_hx711_library):
        """Test that get_hx711 reuses existing instance"""
        mock_class, mock_instance = mock_hx711_library
        
        # First call
        hx711_1 = loadcell_sensor.get_hx711()
        # Second call  
        hx711_2 = loadcell_sensor.get_hx711()
        
        # Should be the same instance
        assert hx711_1 == hx711_2 == mock_instance
        # Constructor should only be called once during setup
    
    def test_get_hx711_initialization_failure(self, loadcell_sensor, mock_hx711_library):
        """Test HX711 initialization failure handling"""
        mock_class, mock_instance = mock_hx711_library
        mock_class.side_effect = Exception("Hardware initialization failed")
        
        # Force re-initialization
        loadcell_sensor.hx711 = None
        
        with pytest.raises(Exception, match="Hardware initialization failed"):
            loadcell_sensor.get_hx711()
        
        # Should clean up and set hx711 to None
        assert loadcell_sensor.hx711 is None


class TestWeightReadings:
    """Test weight reading functionality"""
    
    @pytest.mark.asyncio
    async def test_get_readings_success(self, loadcell_sensor, mock_hx711_library):
        """Test successful weight readings"""
        mock_class, mock_instance = mock_hx711_library
        mock_instance.get_raw_data.return_value = [82000, 82100, 81900]
        
        readings = await loadcell_sensor.get_readings()
        
        # Verify the readings structure
        expected_keys = ["doutPin", "sckPin", "gain", "numberOfReadings", 
                        "tare_offset", "measures", "weight"]
        for key in expected_keys:
            assert key in readings
        
        # Check specific values
        assert readings["doutPin"] == 5
        assert readings["sckPin"] == 6  
        assert readings["gain"] == 128
        assert readings["numberOfReadings"] == 3
        
        # Check weight calculation: average of readings converted to kg
        # (82000 - 0) / 8200 ≈ 10.0 kg
        expected_weight = 82000 / 8200  # No tare offset
        assert abs(readings["weight"] - expected_weight) < 0.01
        
        # Check that measures are converted to kg
        assert len(readings["measures"]) == 3
        expected_measures = [82000/8200, 82100/8200, 81900/8200]
        for i, measure in enumerate(readings["measures"]):
            assert abs(measure - expected_measures[i]) < 0.001
        
        # Verify HX711 was called correctly
        mock_instance.get_raw_data.assert_called_with(times=3)
    
    @pytest.mark.asyncio 
    async def test_get_readings_with_tare_offset(self, loadcell_sensor, mock_hx711_library):
        """Test readings with tare offset applied"""
        mock_class, mock_instance = mock_hx711_library
        mock_instance.get_raw_data.return_value = [90000, 90100, 89900]
        
        # Set tare offset (equivalent to 1kg)
        loadcell_sensor.tare_offset = 8200.0
        
        readings = await loadcell_sensor.get_readings()
        
        # Weight should account for tare offset
        # (90000 - 8200) / 8200 ≈ 9.976 kg
        expected_weight = (90000 - 8200) / 8200
        assert abs(readings["weight"] - expected_weight) < 0.01
        
        # Tare offset should be reported in kg for consistency
        assert abs(readings["tare_offset"] - 1.0) < 0.001
    
    @pytest.mark.asyncio
    async def test_get_readings_negative_weight(self, loadcell_sensor, mock_hx711_library):
        """Test handling of negative weight readings"""
        mock_class, mock_instance = mock_hx711_library
        mock_instance.get_raw_data.return_value = [-1000, -1100, -900]
        
        readings = await loadcell_sensor.get_readings()
        
        # Should handle negative values correctly
        expected_weight = -1000 / 8200  # Negative weight
        assert abs(readings["weight"] - expected_weight) < 0.001
        assert readings["weight"] < 0
    
    @pytest.mark.asyncio
    async def test_get_readings_hardware_error(self, loadcell_sensor, mock_hx711_library):
        """Test error handling during readings"""
        mock_class, mock_instance = mock_hx711_library
        mock_instance.get_raw_data.side_effect = Exception("Sensor communication error")
        
        with pytest.raises(Exception, match="Sensor communication error"):
            await loadcell_sensor.get_readings()
        
        # Should clean up HX711 instance on error
        assert loadcell_sensor.hx711 is None


class TestTareFunctionality:
    """Test tare (zero) functionality"""
    
    @pytest.mark.asyncio
    async def test_tare_function(self, loadcell_sensor, mock_hx711_library):
        """Test tare functionality"""
        mock_class, mock_instance = mock_hx711_library
        mock_instance.get_raw_data.return_value = [50000, 50100, 49900]
        
        await loadcell_sensor.tare()
        
        # Tare offset should be set to average of readings
        expected_offset = (50000 + 50100 + 49900) / 3
        assert abs(loadcell_sensor.tare_offset - expected_offset) < 0.1
        
        # Verify get_raw_data was called with correct parameters
        mock_instance.get_raw_data.assert_called_with(times=3)
    
    @pytest.mark.asyncio
    async def test_tare_then_weigh(self, loadcell_sensor, mock_hx711_library):
        """Test tare then get readings"""
        mock_class, mock_instance = mock_hx711_library
        
        # First call for tare
        mock_instance.get_raw_data.return_value = [50000, 50000, 50000]
        await loadcell_sensor.tare()
        
        # Second call for reading after tare
        mock_instance.get_raw_data.return_value = [58200, 58200, 58200]  # +8200 = +1kg
        readings = await loadcell_sensor.get_readings()
        
        # Should show approximately 1kg (58200 - 50000 = 8200, 8200/8200 = 1kg)
        assert abs(readings["weight"] - 1.0) < 0.01
    
    @pytest.mark.asyncio
    async def test_tare_hardware_error(self, loadcell_sensor, mock_hx711_library):
        """Test tare error handling"""
        mock_class, mock_instance = mock_hx711_library
        mock_instance.get_raw_data.side_effect = Exception("Tare communication error")
        
        with pytest.raises(Exception, match="Tare communication error"):
            await loadcell_sensor.tare()
        
        # Should clean up HX711 instance on error
        assert loadcell_sensor.hx711 is None


class TestViamIntegration:
    """Test Viam-specific functionality"""
    
    @pytest.mark.asyncio
    async def test_do_command_tare(self, loadcell_sensor, mock_hx711_library):
        """Test do_command with tare command"""
        mock_class, mock_instance = mock_hx711_library
        mock_instance.get_raw_data.return_value = [60000, 60000, 60000]
        
        command = {"tare": []}  # Empty args for tare
        result = await loadcell_sensor.do_command(command)
        
        # Should return the tare offset in kg
        assert "tare" in result
        expected_tare_kg = 60000 / 8200  # Convert to kg
        assert abs(result["tare"] - expected_tare_kg) < 0.001
    
    @pytest.mark.asyncio
    async def test_do_command_unknown_command(self, loadcell_sensor):
        """Test do_command with unknown command"""
        command = {"unknown_command": [], "another_unknown": []}
        result = await loadcell_sensor.do_command(command)
        
        # Should return False for unknown commands
        assert result["unknown_command"] is False
        assert result["another_unknown"] is False
    
    @pytest.mark.asyncio
    async def test_do_command_multiple_commands(self, loadcell_sensor, mock_hx711_library):
        """Test do_command with multiple commands"""
        mock_class, mock_instance = mock_hx711_library
        mock_instance.get_raw_data.return_value = [45000, 45000, 45000]
        
        command = {"tare": [], "unknown": []}
        result = await loadcell_sensor.do_command(command)
        
        # Tare should work, unknown should return False
        assert abs(result["tare"] - (45000/8200)) < 0.001
        assert result["unknown"] is False


class TestResourceManagement:
    """Test resource cleanup and management"""
    
    def test_cleanup_gpio_pins(self, loadcell_sensor, mock_gpio):
        """Test GPIO cleanup"""
        loadcell_sensor.cleanup_gpio_pins()
        
        # Should call GPIO.cleanup with the specific pins
        mock_gpio.cleanup.assert_called_once_with((5, 6))
    
    def test_cleanup_gpio_error_handling(self, loadcell_sensor, mock_gpio):
        """Test GPIO cleanup error handling"""
        mock_gpio.cleanup.side_effect = Exception("GPIO cleanup failed")
        
        # Should not raise exception, just log warning
        loadcell_sensor.cleanup_gpio_pins()
        
        # Verify it tried to cleanup
        mock_gpio.cleanup.assert_called_once_with((5, 6))
    
    def test_close_cleanup(self, loadcell_sensor, mock_gpio):
        """Test component cleanup on close"""
        # Set up HX711 instance
        loadcell_sensor.hx711 = Mock()
        
        loadcell_sensor.close()
        
        # Should clean up HX711 and GPIO
        assert loadcell_sensor.hx711 is None
        mock_gpio.cleanup.assert_called_once_with((5, 6))
    
    def test_close_with_cleanup_errors(self, loadcell_sensor, mock_gpio):
        """Test close handles cleanup errors gracefully"""
        loadcell_sensor.hx711 = Mock()
        mock_gpio.cleanup.side_effect = Exception("Cleanup error")
        
        # Should not raise exception
        loadcell_sensor.close()
        
        # Should still clean up what it can
        assert loadcell_sensor.hx711 is None


class TestEdgeCasesAndCalculations:
    """Test edge cases and calculation accuracy"""
    
    @pytest.mark.parametrize("raw_readings,tare_offset,expected_weight", [
        ([82000, 82000, 82000], 0, 10.0),           # 82000/8200 = 10kg
        ([0, 0, 0], 0, 0.0),                        # Zero weight
        ([164000, 164000, 164000], 0, 20.0),        # 20kg
        ([90200, 90200, 90200], 8200, 10.0),        # 10kg after 1kg tare
        ([-8200, -8200, -8200], 0, -1.0),           # Negative weight
    ])
    @pytest.mark.asyncio
    async def test_weight_calculations(self, loadcell_sensor, mock_hx711_library, 
                                      raw_readings, tare_offset, expected_weight):
        """Test weight calculation accuracy with various inputs"""
        mock_class, mock_instance = mock_hx711_library
        mock_instance.get_raw_data.return_value = raw_readings
        loadcell_sensor.tare_offset = tare_offset
        
        readings = await loadcell_sensor.get_readings()
        
        assert abs(readings["weight"] - expected_weight) < 0.01
    
    @pytest.mark.asyncio
    async def test_varying_number_of_readings(self, basic_config, mock_hx711_library, mock_gpio):
        """Test different numberOfReadings values"""
        mock_class, mock_instance = mock_hx711_library
        
        # Test with 5 readings
        basic_config.attributes.fields["numberOfReadings"].number_value = 5
        sensor = Loadcell.new(basic_config, dependencies={})
        
        mock_instance.get_raw_data.return_value = [80000, 81000, 82000, 83000, 84000]
        readings = await sensor.get_readings()
        
        assert len(readings["measures"]) == 5
        assert readings["numberOfReadings"] == 5
        
        # Verify get_raw_data called with correct times parameter
        mock_instance.get_raw_data.assert_called_with(times=5)
    
    @pytest.mark.asyncio
    async def test_large_weight_values(self, loadcell_sensor, mock_hx711_library):
        """Test handling of large weight values"""
        mock_class, mock_instance = mock_hx711_library
        large_values = [8200000, 8210000, 8190000]  # ~1000kg
        mock_instance.get_raw_data.return_value = large_values
        
        readings = await loadcell_sensor.get_readings()
        
        # Should handle large values correctly
        expected_weight = 8200000 / 8200  # ~1000kg
        assert abs(readings["weight"] - expected_weight) < 1.0  # Within 1kg tolerance