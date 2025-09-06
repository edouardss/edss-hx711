"""
Comprehensive unit tests for the Loadcell component.
Tests all functionality using MockHX711 simulation.
"""

import pytest
import asyncio
from unittest.mock import patch, MagicMock, call
from typing import Mapping, Any

# Import the component under test
import sys
import os
from pathlib import Path

# Add src directory to Python path
project_root = Path(__file__).parent.parent
src_dir = project_root / "src"
sys.path.insert(0, str(src_dir))

from main import Loadcell
from tests.mock_hx711 import MockHX711, MockHX711Factory, SimulationMode


def create_test_loadcell():
    """Create a Loadcell instance for testing."""
    loadcell = Loadcell(name="test_loadcell")
    loadcell.doutPin = 5
    loadcell.sckPin = 6
    loadcell.gain = 64
    loadcell.numberOfReadings = 3
    loadcell.tare_offset = 0.0
    loadcell.hx711 = None
    loadcell.logger = MagicMock()  # Mock logger to avoid Viam logger dependency
    return loadcell


class TestLoadcellConfiguration:
    """Test configuration validation and reconfiguration."""
    
    def test_validate_config_valid_inputs(self):
        """Test configuration validation with valid inputs."""
        # Create mock config with valid fields
        config = MagicMock()
        config.attributes.fields = {
            "gain": MagicMock(HasField=lambda x: x == "number_value", number_value=64),
            "doutPin": MagicMock(HasField=lambda x: x == "number_value", number_value=5),
            "sckPin": MagicMock(HasField=lambda x: x == "number_value", number_value=6),
            "numberOfReadings": MagicMock(HasField=lambda x: x == "number_value", number_value=3),
            "tare_offset": MagicMock(HasField=lambda x: x == "number_value", number_value=0.0)
        }
        
        errors = Loadcell.validate_config(config)
        assert errors == []
    
    def test_validate_config_missing_gain(self):
        """Test configuration validation with missing gain."""
        config = MagicMock()
        config.attributes.fields = {}
        
        errors = Loadcell.validate_config(config)
        assert errors == []
    
    def test_validate_config_invalid_gain_type(self):
        """Test configuration validation with invalid gain type."""
        config = MagicMock()
        config.attributes.fields = {
            "gain": MagicMock(HasField=lambda x: False)
        }
        
        with pytest.raises(Exception, match="Gain must be a valid number"):
            Loadcell.validate_config(config)
    
    def test_validate_config_invalid_doutPin_type(self):
        """Test configuration validation with invalid doutPin type."""
        config = MagicMock()
        config.attributes.fields = {
            "doutPin": MagicMock(HasField=lambda x: False)
        }
        
        with pytest.raises(Exception, match="Data Out pin must be a valid number"):
            Loadcell.validate_config(config)
    
    def test_validate_config_invalid_sckPin_type(self):
        """Test configuration validation with invalid sckPin type."""
        config = MagicMock()
        config.attributes.fields = {
            "sckPin": MagicMock(HasField=lambda x: False)
        }
        
        with pytest.raises(Exception, match="Gain must be a valid number"):
            Loadcell.validate_config(config)
    
    def test_validate_config_invalid_numberOfReadings_type(self):
        """Test configuration validation with invalid numberOfReadings type."""
        config = MagicMock()
        config.attributes.fields = {
            "numberOfReadings": MagicMock(HasField=lambda x: False)
        }
        
        with pytest.raises(Exception, match="Gain must be a valid number"):
            Loadcell.validate_config(config)
    
    def test_validate_config_invalid_tare_offset_type(self):
        """Test configuration validation with invalid tare_offset type."""
        config = MagicMock()
        config.attributes.fields = {
            "tare_offset": MagicMock(HasField=lambda x: False)
        }
        
        with pytest.raises(Exception, match="Tare offset must be a valid number"):
            Loadcell.validate_config(config)


class TestLoadcellReconfiguration:
    """Test component reconfiguration functionality."""
    
    @patch('main.HX711')
    def test_reconfigure_with_all_parameters(self, mock_hx711_class):
        """Test reconfiguration with all parameters provided."""
        mock_hx711_class.return_value = MockHX711(5, 6, 'A', 64)
        
        loadcell = create_test_loadcell()
        config = MagicMock()
        config.attributes = MagicMock()
        
        # Mock struct_to_dict to return test values
        with patch('main.struct_to_dict') as mock_struct_to_dict:
            mock_struct_to_dict.return_value = {
                "gain": 128,
                "doutPin": 7,
                "sckPin": 8,
                "numberOfReadings": 5,
                "tare_offset": 100.0
            }
            
            loadcell.reconfigure(config, {})
            
            assert loadcell.gain == 128
            assert loadcell.doutPin == 7
            assert loadcell.sckPin == 8
            assert loadcell.numberOfReadings == 5
            assert loadcell.tare_offset == 100.0
    
    @patch('main.HX711')
    def test_reconfigure_with_default_values(self, mock_hx711_class):
        """Test reconfiguration with default values."""
        mock_hx711_class.return_value = MockHX711(5, 6, 'A', 64)
        
        loadcell = create_test_loadcell()
        config = MagicMock()
        config.attributes = MagicMock()
        
        with patch('main.struct_to_dict') as mock_struct_to_dict:
            mock_struct_to_dict.return_value = {}
            
            loadcell.reconfigure(config, {})
            
            assert loadcell.gain == 64
            assert loadcell.doutPin == 5
            assert loadcell.sckPin == 6
            assert loadcell.numberOfReadings == 3
            assert loadcell.tare_offset == 0.0


class TestLoadcellHX711Management:
    """Test HX711 object management."""
    
    @patch('main.HX711')
    def test_get_hx711_creates_new_instance_when_none(self, mock_hx711_class):
        """Test that get_hx711 creates new instance when none exists."""
        mock_hx711_class.return_value = MockHX711(5, 6, 'A', 64)
        
        loadcell = create_test_loadcell()
        loadcell.doutPin = 5
        loadcell.sckPin = 6
        loadcell.gain = 64
        loadcell.hx711 = None
        
        hx711 = loadcell.get_hx711()
        
        assert hx711 is not None
        assert loadcell.hx711 is hx711
        mock_hx711_class.assert_called_once_with(
            dout_pin=5, pd_sck_pin=6, channel='A', gain=64
        )
    
    @patch('main.HX711')
    def test_get_hx711_returns_existing_instance(self, mock_hx711_class):
        """Test that get_hx711 returns existing instance."""
        existing_hx711 = MockHX711(5, 6, 'A', 64)
        mock_hx711_class.return_value = existing_hx711
        
        loadcell = create_test_loadcell()
        loadcell.doutPin = 5
        loadcell.sckPin = 6
        loadcell.gain = 64
        loadcell.hx711 = existing_hx711
        
        hx711 = loadcell.get_hx711()
        
        assert hx711 is existing_hx711
        mock_hx711_class.assert_not_called()
    
    @patch('main.HX711')
    def test_get_hx711_handles_initialization_failure(self, mock_hx711_class):
        """Test that get_hx711 handles initialization failure."""
        mock_hx711_class.side_effect = Exception("Hardware initialization failed")
        
        loadcell = create_test_loadcell()
        loadcell.doutPin = 5
        loadcell.sckPin = 6
        loadcell.gain = 64
        loadcell.hx711 = None
        
        with pytest.raises(Exception, match="Hardware initialization failed"):
            loadcell.get_hx711()
        
        assert loadcell.hx711 is None
    
    @patch('main.HX711')
    def test_get_hx711_cleans_up_on_failure(self, mock_hx711_class):
        """Test that get_hx711 cleans up on failure."""
        # Create a mock that fails after partial initialization
        mock_instance = MagicMock()
        mock_hx711_class.return_value = mock_instance
        mock_hx711_class.side_effect = Exception("Partial initialization")
        
        loadcell = create_test_loadcell()
        loadcell.doutPin = 5
        loadcell.sckPin = 6
        loadcell.gain = 64
        loadcell.hx711 = None
        
        with pytest.raises(Exception):
            loadcell.get_hx711()
        
        assert loadcell.hx711 is None


class TestLoadcellGPIO:
    """Test GPIO cleanup functionality."""
    
    @patch('main.GPIO')
    def test_cleanup_gpio_pins_success(self, mock_gpio):
        """Test successful GPIO cleanup."""
        loadcell = create_test_loadcell()
        loadcell.doutPin = 5
        loadcell.sckPin = 6
        
        loadcell.cleanup_gpio_pins()
        
        mock_gpio.cleanup.assert_called_once_with((5, 6))
    
    @patch('main.GPIO')
    def test_cleanup_gpio_pins_handles_gpio_error(self, mock_gpio):
        """Test GPIO cleanup error handling."""
        mock_gpio.cleanup.side_effect = Exception("GPIO cleanup failed")
        
        loadcell = create_test_loadcell()
        loadcell.doutPin = 5
        loadcell.sckPin = 6
        
        # Should not raise exception
        loadcell.cleanup_gpio_pins()
        
        mock_gpio.cleanup.assert_called_once_with((5, 6))


class TestLoadcellLifecycle:
    """Test component lifecycle management."""
    
    @patch('main.GPIO')
    def test_close_cleans_up_resources(self, mock_gpio):
        """Test that close method cleans up resources."""
        loadcell = create_test_loadcell()
        loadcell.hx711 = MockHX711(5, 6, 'A', 64)
        loadcell.doutPin = 5
        loadcell.sckPin = 6
        
        loadcell.close()
        
        assert loadcell.hx711 is None
        mock_gpio.cleanup.assert_called_once_with((5, 6))
    
    @patch('main.GPIO')
    def test_close_handles_missing_hx711(self, mock_gpio):
        """Test close method handles missing HX711 object."""
        loadcell = create_test_loadcell()
        loadcell.hx711 = None
        loadcell.doutPin = 5
        loadcell.sckPin = 6
        
        # Should not raise exception
        loadcell.close()
        
        mock_gpio.cleanup.assert_called_once_with((5, 6))


class TestLoadcellReadings:
    """Test sensor reading functionality."""
    
    @pytest.mark.asyncio
    @patch('main.HX711')
    async def test_get_readings_success(self, mock_hx711_class):
        """Test successful reading operation."""
        mock_hx711 = MockHX711(5, 6, 'A', 64)
        mock_hx711.set_simulated_weight(1.0)  # 1kg
        mock_hx711_class.return_value = mock_hx711
        
        loadcell = create_test_loadcell()
        loadcell.doutPin = 5
        loadcell.sckPin = 6
        loadcell.gain = 64
        loadcell.numberOfReadings = 3
        loadcell.tare_offset = 0.0
        
        result = await loadcell.get_readings()
        
        assert "weight" in result
        assert "measures" in result
        assert "doutPin" in result
        assert "sckPin" in result
        assert "gain" in result
        assert "numberOfReadings" in result
        assert "tare_offset" in result
        
        assert len(result["measures"]) == 3
        assert abs(result["weight"] - 1.0) < 0.1  # Should be close to 1kg
        assert result["doutPin"] == 5
        assert result["sckPin"] == 6
        assert result["gain"] == 64
        assert result["numberOfReadings"] == 3
    
    @pytest.mark.asyncio
    @patch('main.HX711')
    async def test_get_readings_calculates_measures_correctly(self, mock_hx711_class):
        """Test that measures are calculated correctly."""
        mock_hx711 = MockHX711(5, 6, 'A', 64)
        mock_hx711.set_simulated_weight(2.0)  # 2kg
        mock_hx711_class.return_value = mock_hx711
        
        loadcell = create_test_loadcell()
        loadcell.doutPin = 5
        loadcell.sckPin = 6
        loadcell.gain = 64
        loadcell.numberOfReadings = 3
        loadcell.tare_offset = 0.0
        
        result = await loadcell.get_readings()
        
        # All measures should be close to 2kg
        for measure in result["measures"]:
            assert abs(measure - 2.0) < 0.1
    
    @pytest.mark.asyncio
    @patch('main.HX711')
    async def test_get_readings_applies_tare_offset(self, mock_hx711_class):
        """Test that tare offset is applied correctly."""
        mock_hx711 = MockHX711(5, 6, 'A', 64)
        mock_hx711.set_simulated_weight(1.0)  # 1kg
        mock_hx711_class.return_value = mock_hx711
        
        loadcell = create_test_loadcell()
        loadcell.doutPin = 5
        loadcell.sckPin = 6
        loadcell.gain = 64
        loadcell.numberOfReadings = 3
        loadcell.tare_offset = 8200  # 1kg offset
        
        result = await loadcell.get_readings()
        
        # With 1kg tare offset, readings should be close to 0kg
        assert abs(result["weight"]) < 0.1
    
    @pytest.mark.asyncio
    @patch('main.HX711')
    async def test_get_readings_handles_hx711_error(self, mock_hx711_class):
        """Test error handling in get_readings."""
        mock_hx711 = MockHX711(5, 6, 'A', 64, SimulationMode.ERROR)
        mock_hx711.set_error_probability(1.0)  # Always error
        mock_hx711_class.return_value = mock_hx711
        
        loadcell = create_test_loadcell()
        loadcell.doutPin = 5
        loadcell.sckPin = 6
        loadcell.gain = 64
        loadcell.numberOfReadings = 3
        loadcell.tare_offset = 0.0
        
        with pytest.raises(Exception):
            await loadcell.get_readings()
        
        # HX711 should be reset to None
        assert loadcell.hx711 is None
    
    @pytest.mark.asyncio
    @patch('main.HX711')
    async def test_get_readings_cleans_up_on_error(self, mock_hx711_class):
        """Test that get_readings cleans up on error."""
        mock_hx711 = MockHX711(5, 6, 'A', 64, SimulationMode.ERROR)
        mock_hx711.set_error_probability(1.0)
        mock_hx711_class.return_value = mock_hx711
        
        loadcell = create_test_loadcell()
        loadcell.doutPin = 5
        loadcell.sckPin = 6
        loadcell.gain = 64
        loadcell.numberOfReadings = 3
        loadcell.tare_offset = 0.0
        
        with pytest.raises(Exception):
            await loadcell.get_readings()
        
        # HX711 should be cleaned up
        assert loadcell.hx711 is None


class TestLoadcellTare:
    """Test tare functionality."""
    
    @pytest.mark.asyncio
    @patch('main.HX711')
    async def test_tare_success(self, mock_hx711_class):
        """Test successful tare operation."""
        mock_hx711 = MockHX711(5, 6, 'A', 64)
        mock_hx711.set_simulated_weight(1.5)  # 1.5kg
        mock_hx711_class.return_value = mock_hx711
        
        loadcell = create_test_loadcell()
        loadcell.doutPin = 5
        loadcell.sckPin = 6
        loadcell.gain = 64
        loadcell.numberOfReadings = 3
        loadcell.tare_offset = 0.0
        
        await loadcell.tare()
        
        # Tare offset should be set to approximately 1.5kg in raw units
        expected_offset = 1.5 * 8200
        assert abs(loadcell.tare_offset - expected_offset) < 500  # Allow some tolerance for mock variations
    
    @pytest.mark.asyncio
    @patch('main.HX711')
    async def test_tare_calculates_offset_correctly(self, mock_hx711_class):
        """Test that tare calculates offset correctly."""
        mock_hx711 = MockHX711(5, 6, 'A', 64)
        mock_hx711.set_simulated_weight(2.0)  # 2kg
        mock_hx711_class.return_value = mock_hx711
        
        loadcell = create_test_loadcell()
        loadcell.doutPin = 5
        loadcell.sckPin = 6
        loadcell.gain = 64
        loadcell.numberOfReadings = 5
        loadcell.tare_offset = 0.0
        
        await loadcell.tare()
        
        # Tare offset should be close to 2kg in raw units
        expected_offset = 2.0 * 8200
        assert abs(loadcell.tare_offset - expected_offset) < 200  # Allow some tolerance
    
    @pytest.mark.asyncio
    @patch('main.HX711')
    async def test_tare_handles_hx711_error(self, mock_hx711_class):
        """Test tare error handling."""
        mock_hx711 = MockHX711(5, 6, 'A', 64, SimulationMode.ERROR)
        mock_hx711.set_error_probability(1.0)
        mock_hx711_class.return_value = mock_hx711
        
        loadcell = create_test_loadcell()
        loadcell.doutPin = 5
        loadcell.sckPin = 6
        loadcell.gain = 64
        loadcell.numberOfReadings = 3
        loadcell.tare_offset = 0.0
        
        with pytest.raises(Exception):
            await loadcell.tare()
        
        # HX711 should be reset to None
        assert loadcell.hx711 is None


class TestLoadcellCommands:
    """Test command handling functionality."""
    
    @pytest.mark.asyncio
    @patch('main.HX711')
    async def test_do_command_tare_success(self, mock_hx711_class):
        """Test successful tare command."""
        mock_hx711 = MockHX711(5, 6, 'A', 64)
        mock_hx711.set_simulated_weight(1.0)  # 1kg
        mock_hx711_class.return_value = mock_hx711
        
        loadcell = create_test_loadcell()
        loadcell.doutPin = 5
        loadcell.sckPin = 6
        loadcell.gain = 64
        loadcell.numberOfReadings = 3
        loadcell.tare_offset = 0.0
        
        command = {"tare": []}
        result = await loadcell.do_command(command)
        
        assert "tare" in result
        assert result["tare"] > 0  # Should return the tare offset in kg
    
    @pytest.mark.asyncio
    @patch('main.HX711')
    async def test_do_command_unknown_command_ignored(self, mock_hx711_class):
        """Test that unknown commands are ignored."""
        mock_hx711_class.return_value = MockHX711(5, 6, 'A', 64)
        
        loadcell = create_test_loadcell()
        loadcell.doutPin = 5
        loadcell.sckPin = 6
        loadcell.gain = 64
        loadcell.numberOfReadings = 3
        loadcell.tare_offset = 0.0
        
        command = {"unknown_command": []}
        result = await loadcell.do_command(command)
        
        assert "unknown_command" in result
        assert result["unknown_command"] is False
    
    @pytest.mark.asyncio
    @patch('main.HX711')
    async def test_do_command_multiple_commands(self, mock_hx711_class):
        """Test handling multiple commands."""
        mock_hx711 = MockHX711(5, 6, 'A', 64)
        mock_hx711.set_simulated_weight(1.0)
        mock_hx711_class.return_value = mock_hx711
        
        loadcell = create_test_loadcell()
        loadcell.doutPin = 5
        loadcell.sckPin = 6
        loadcell.gain = 64
        loadcell.numberOfReadings = 3
        loadcell.tare_offset = 0.0
        
        command = {"tare": [], "unknown": []}
        result = await loadcell.do_command(command)
        
        assert "tare" in result
        assert "unknown" in result
        assert result["tare"] > 0
        assert result["unknown"] is False


class TestLoadcellIntegration:
    """Integration tests for the complete workflow."""
    
    @pytest.mark.asyncio
    @patch('main.HX711')
    async def test_full_workflow_readings_and_tare(self, mock_hx711_class):
        """Test complete workflow: tare then readings."""
        mock_hx711 = MockHX711(5, 6, 'A', 64)
        mock_hx711.set_simulated_weight(1.0)  # 1kg
        mock_hx711_class.return_value = mock_hx711
        
        loadcell = create_test_loadcell()
        loadcell.doutPin = 5
        loadcell.sckPin = 6
        loadcell.gain = 64
        loadcell.numberOfReadings = 3
        loadcell.tare_offset = 0.0
        
        # First, perform tare
        await loadcell.tare()
        tare_offset = loadcell.tare_offset
        
        # Then get readings - should be close to zero after tare
        result = await loadcell.get_readings()
        
        assert abs(result["weight"]) < 0.1  # Should be close to zero
        assert tare_offset > 0  # Tare offset should be set
    
    @pytest.mark.asyncio
    @patch('main.HX711')
    async def test_error_recovery_after_failure(self, mock_hx711_class):
        """Test that component recovers after error."""
        # First call fails, second call succeeds
        mock_hx711_fail = MockHX711(5, 6, 'A', 64, SimulationMode.ERROR)
        mock_hx711_fail.set_error_probability(1.0)
        
        mock_hx711_success = MockHX711(5, 6, 'A', 64)
        mock_hx711_success.set_simulated_weight(1.0)
        
        mock_hx711_class.side_effect = [mock_hx711_fail, mock_hx711_success]
        
        loadcell = create_test_loadcell()
        loadcell.doutPin = 5
        loadcell.sckPin = 6
        loadcell.gain = 64
        loadcell.numberOfReadings = 3
        loadcell.tare_offset = 0.0
        
        # First call should fail
        with pytest.raises(Exception):
            await loadcell.get_readings()
        
        # HX711 should be reset
        assert loadcell.hx711 is None
        
        # Second call should succeed (new HX711 will be created)
        result = await loadcell.get_readings()
        assert "weight" in result


class TestLoadcellEdgeCases:
    """Test edge cases and error conditions."""
    
    @pytest.mark.asyncio
    @patch('main.HX711')
    async def test_division_by_zero_protection(self, mock_hx711_class):
        """Test protection against division by zero."""
        mock_hx711 = MockHX711(5, 6, 'A', 64)
        mock_hx711.set_simulated_weight(0.0)  # Zero weight
        mock_hx711_class.return_value = mock_hx711
        
        loadcell = create_test_loadcell()
        loadcell.doutPin = 5
        loadcell.sckPin = 6
        loadcell.gain = 64
        loadcell.numberOfReadings = 3
        loadcell.tare_offset = 0.0
        
        # Should not raise division by zero error
        result = await loadcell.get_readings()
        assert "weight" in result
        assert result["weight"] == 0.0
    
    @pytest.mark.asyncio
    @patch('main.HX711')
    async def test_negative_measurements(self, mock_hx711_class):
        """Test handling of negative measurements."""
        mock_hx711 = MockHX711(5, 6, 'A', 64)
        mock_hx711.set_simulated_weight(-0.5)  # Negative weight
        mock_hx711_class.return_value = mock_hx711
        
        loadcell = create_test_loadcell()
        loadcell.doutPin = 5
        loadcell.sckPin = 6
        loadcell.gain = 64
        loadcell.numberOfReadings = 3
        loadcell.tare_offset = 0.0
        
        result = await loadcell.get_readings()
        assert "weight" in result
        assert result["weight"] < 0  # Should handle negative weights
    
    @pytest.mark.asyncio
    @patch('main.HX711')
    async def test_extremely_large_measurements(self, mock_hx711_class):
        """Test handling of extremely large measurements."""
        mock_hx711 = MockHX711(5, 6, 'A', 64)
        mock_hx711.set_simulated_weight(1000.0)  # Very large weight
        mock_hx711_class.return_value = mock_hx711
        
        loadcell = create_test_loadcell()
        loadcell.doutPin = 5
        loadcell.sckPin = 6
        loadcell.gain = 64
        loadcell.numberOfReadings = 3
        loadcell.tare_offset = 0.0
        
        result = await loadcell.get_readings()
        assert "weight" in result
        assert result["weight"] > 0  # Should handle large weights


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
