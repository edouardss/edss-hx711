"""Unit tests for HX711 Loadcell Viam module"""

import pytest
from unittest.mock import Mock
from viam.proto.app.robot import ComponentConfig
from google.protobuf.struct_pb2 import Struct
from viam.resource.types import Model, ModelFamily

from src.main import Loadcell


class TestLoadcellBasics:
    """Test basic functionality and configuration"""

    def test_model_definition(self):
        """Test that the model is properly defined"""
        expected_model = Model(ModelFamily("edss", "hx711-loadcell"), "loadcell")
        assert Loadcell.MODEL == expected_model

    def test_validate_config_valid(self, sensor_config):
        """Test config validation with valid configuration"""
        errors = Loadcell.validate_config(sensor_config)
        assert errors == []

    @pytest.mark.parametrize("gain_value,should_pass", [
        (32, True), (64, True), (128, True),
        (16, False), (256, False), (0, False)
    ])
    def test_validate_gain_values(self, gain_value, should_pass):
        """Test gain validation with specific values"""
        config = ComponentConfig()
        config.name = "test_loadcell"
        attributes = Struct()
        attributes.fields["gain"].number_value = gain_value
        config.attributes.CopyFrom(attributes)

        if should_pass:
            Loadcell.validate_config(config)
        else:
            with pytest.raises(Exception, match="Gain must be 32, 64, or 128"):
                Loadcell.validate_config(config)

    def test_reconfigure_with_defaults(self, mock_hx711, mock_gpio):
        """Test reconfiguration uses default values when attributes missing"""
        config = ComponentConfig()
        config.name = "minimal_test_loadcell"
        config.attributes.CopyFrom(Struct())  # Empty attributes
        
        sensor = Loadcell.new(config, dependencies={})
        sensor.hx711 = mock_hx711

        # Should use defaults
        assert sensor.gain == 64.0
        assert sensor.doutPin == 5
        assert sensor.sckPin == 6
        assert sensor.numberOfReadings == 3
        assert sensor.tare_offset == 0.0


class TestWeightReadings:
    """Test weight reading functionality"""

    @pytest.mark.asyncio
    async def test_get_readings_success(self, loadcell_sensor):
        """Test successful weight readings"""
        readings = await loadcell_sensor.get_readings()

        # Verify the readings structure
        expected_keys = ["doutPin", "sckPin", "gain", "numberOfReadings", "tare_offset", "measures", "weight"]
        for key in expected_keys:
            assert key in readings

        # Check specific values
        assert readings["doutPin"] == 5
        assert readings["sckPin"] == 6
        assert readings["gain"] == 128
        assert readings["numberOfReadings"] == 3

        # Check weight calculation (approximately 10kg from mock values)
        assert abs(readings["weight"] - 10.0) < 0.1
        assert len(readings["measures"]) == 3

    @pytest.mark.asyncio
    async def test_get_readings_with_tare_offset(self, loadcell_sensor):
        """Test readings with tare offset applied"""
        # Set tare offset (equivalent to 1kg)
        loadcell_sensor.tare_offset = 8200.0
        readings = await loadcell_sensor.get_readings()

        # Weight should account for tare offset
        expected_weight = (82000 - 8200) / 8200  # ≈ 9.0 kg
        assert abs(readings["weight"] - expected_weight) < 0.1

    @pytest.mark.asyncio
    async def test_get_readings_hardware_error(self, loadcell_sensor, mock_hx711):
        """Test error handling during readings"""
        mock_hx711.get_raw_data.side_effect = Exception("Sensor communication error")

        with pytest.raises(Exception, match="Sensor communication error"):
            await loadcell_sensor.get_readings()

        # Should clean up HX711 instance on error
        assert loadcell_sensor.hx711 is None


class TestTareFunctionality:
    """Test tare (zero) functionality"""

    @pytest.mark.asyncio
    async def test_tare_function(self, loadcell_sensor, mock_hx711):
        """Test tare functionality"""
        mock_hx711.get_raw_data.return_value = [50000, 50100, 49900]

        await loadcell_sensor.tare()

        # Tare offset should be set to average of readings
        expected_offset = (50000 + 50100 + 49900) / 3
        assert abs(loadcell_sensor.tare_offset - expected_offset) < 0.1

    @pytest.mark.asyncio
    async def test_tare_hardware_error(self, loadcell_sensor, mock_hx711):
        """Test tare error handling"""
        mock_hx711.get_raw_data.side_effect = Exception("Tare communication error")

        with pytest.raises(Exception, match="Tare communication error"):
            await loadcell_sensor.tare()

        # Should clean up HX711 instance on error
        assert loadcell_sensor.hx711 is None


class TestViamIntegration:
    """Test Viam-specific functionality"""

    @pytest.mark.asyncio
    async def test_do_command_tare(self, loadcell_sensor, mock_hx711):
        """Test do_command with tare command"""
        mock_hx711.get_raw_data.return_value = [60000, 60000, 60000]

        command = {"tare": []}
        result = await loadcell_sensor.do_command(command)

        # Should return the tare offset in kg
        assert "tare" in result
        expected_tare_kg = 60000 / 8200
        assert abs(result["tare"] - expected_tare_kg) < 0.001

    @pytest.mark.asyncio
    async def test_do_command_unknown_command(self, loadcell_sensor):
        """Test do_command with unknown command"""
        command = {"unknown_command": []}
        result = await loadcell_sensor.do_command(command)

        # Should return False for unknown commands
        assert result["unknown_command"] is False


class TestResourceManagement:
    """Test resource cleanup and management"""

    def test_cleanup_gpio_pins(self, loadcell_sensor, mock_gpio):
        """Test GPIO cleanup"""
        loadcell_sensor.cleanup_gpio_pins()
        mock_gpio.cleanup.assert_called_once_with((5, 6))

    def test_close_cleanup(self, loadcell_sensor, mock_gpio):
        """Test component cleanup on close"""
        loadcell_sensor.hx711 = Mock()
        loadcell_sensor.close()

        # Should clean up HX711 and GPIO
        assert loadcell_sensor.hx711 is None
        mock_gpio.cleanup.assert_called_once_with((5, 6))


class TestHardwareIntegration:
    """Hardware integration tests (require physical hardware)"""

    @pytest.mark.hardware
    @pytest.mark.skipif(
        not pytest.importorskip("RPi.GPIO", reason="Hardware tests require RPi.GPIO"),
        reason="Hardware tests disabled"
    )
    def test_hardware_connection(self):
        """Test actual hardware connection (only runs with --hardware flag)"""
        # This test would only run when hardware tests are enabled
        # and would test actual sensor connectivity
        pytest.skip("Hardware test placeholder")