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
    async def test_tare_complete_workflow(self, mock_hx711_class):
        """
        Test complete tare workflow:
        1. Simulation sends non-zero reading
        2. Tare function is called and sets tare value to the reading
        3. New reading is called and value should be (raw_value - tare_offset)
        """
        # Create mock HX711 with a specific weight simulation
        mock_hx711 = MockHX711(5, 6, 'A', 64)
        test_weight = 2.5  # 2.5kg
        mock_hx711.set_simulated_weight(test_weight)
        mock_hx711_class.return_value = mock_hx711
        
        loadcell = create_test_loadcell()
        loadcell.doutPin = 5
        loadcell.sckPin = 6
        loadcell.gain = 64
        loadcell.numberOfReadings = 3
        loadcell.tare_offset = 0.0  # Start with no tare offset
        
        # Step 1: Get initial reading (should show the test weight)
        initial_reading = await loadcell.get_readings()
        initial_weight = initial_reading["weight"]
        
        # Verify initial reading is approximately the test weight
        assert abs(initial_weight - test_weight) < 0.2, f"Initial reading {initial_weight}kg should be close to {test_weight}kg (with mock noise tolerance)"
        
        # Step 2: Call tare function - this should set tare_offset to the current reading
        await loadcell.tare()
        
        # Verify tare_offset is set to approximately the test weight in raw units
        expected_tare_offset = test_weight * 8200  # Convert kg to raw units
        assert abs(loadcell.tare_offset - expected_tare_offset) < 1000, f"Tare offset {loadcell.tare_offset} should be close to {expected_tare_offset} (with mock noise tolerance)"
        
        # Step 3: Get new reading after tare - should now be close to zero
        post_tare_reading = await loadcell.get_readings()
        post_tare_weight = post_tare_reading["weight"]
        
        # The new reading should be close to zero since we tared at the current weight
        assert abs(post_tare_weight) < 0.2, f"Post-tare reading {post_tare_weight}kg should be close to 0kg (with mock noise tolerance)"
        
        # Verify the calculation: (raw_value - tare_offset) / 8200
        # Since we're using the same weight, this should result in ~0kg
        raw_readings = post_tare_reading["measures"]
        tare_offset_kg = loadcell.tare_offset / 8200  # Convert back to kg for verification
        
        # Each measure should be approximately: (raw_reading - tare_offset) / 8200
        for measure in raw_readings:
            # The measure should be close to zero since raw_reading ≈ tare_offset
            # Allow more tolerance for mock noise simulation
            assert abs(measure) < 0.2, f"Individual measure {measure}kg should be close to 0kg after tare (with mock noise tolerance)"
    
    @pytest.mark.asyncio
    @patch('main.HX711')
    async def test_tare_mathematical_verification(self, mock_hx711_class):
        """
        Test tare functionality with explicit mathematical verification:
        Verify that: new_reading = (raw_value - tare_offset) / 8200
        """
        # Create mock with specific weight
        mock_hx711 = MockHX711(5, 6, 'A', 64)
        initial_weight = 3.0  # 3kg
        mock_hx711.set_simulated_weight(initial_weight)
        mock_hx711_class.return_value = mock_hx711
        
        loadcell = create_test_loadcell()
        loadcell.doutPin = 5
        loadcell.sckPin = 6
        loadcell.gain = 64
        loadcell.numberOfReadings = 1  # Single reading for easier calculation
        loadcell.tare_offset = 0.0
        
        # Step 1: Get raw reading before tare
        pre_tare_reading = await loadcell.get_readings()
        pre_tare_weight = pre_tare_reading["weight"]
        
        # Verify we get the expected weight
        assert abs(pre_tare_weight - initial_weight) < 0.2, f"Pre-tare weight should be {initial_weight}kg (with mock noise tolerance)"
        
        # Step 2: Perform tare
        await loadcell.tare()
        
        # Verify tare_offset is set correctly
        expected_tare_offset = initial_weight * 8200
        assert abs(loadcell.tare_offset - expected_tare_offset) < 1000, f"Tare offset should be {expected_tare_offset} (with mock noise tolerance)"
        
        # Step 3: Change the simulated weight to a different value
        new_weight = 5.0  # 5kg (2kg more than tare)
        mock_hx711.set_simulated_weight(new_weight)
        
        # Step 4: Get reading after weight change
        post_tare_reading = await loadcell.get_readings()
        post_tare_weight = post_tare_reading["weight"]
        
        # The reading should now be: (new_weight - tare_weight) = (5kg - 3kg) = 2kg
        expected_difference = new_weight - initial_weight  # 2kg
        assert abs(post_tare_weight - expected_difference) < 0.2, f"Post-tare reading should be {expected_difference}kg, got {post_tare_weight}kg (with mock noise tolerance)"
        
        # Step 5: Verify the mathematical calculation manually
        # Get the raw measures and verify the calculation
        measures = post_tare_reading["measures"]
        tare_offset_kg = loadcell.tare_offset / 8200  # Convert tare_offset back to kg
        
        for measure in measures:
            # The measure should be: (raw_reading - tare_offset) / 8200
            # Where raw_reading ≈ new_weight * 8200 and tare_offset ≈ initial_weight * 8200
            # So: measure ≈ ((new_weight * 8200) - (initial_weight * 8200)) / 8200
            # Simplified: measure ≈ new_weight - initial_weight = 5kg - 3kg = 2kg
            assert abs(measure - expected_difference) < 0.2, f"Measure {measure}kg should equal {expected_difference}kg (with mock noise tolerance)"
        
        print(f"✅ Mathematical verification passed:")
        print(f"   Initial weight: {initial_weight}kg")
        print(f"   Tare offset: {tare_offset_kg:.2f}kg")
        print(f"   New weight: {new_weight}kg") 
        print(f"   Expected reading: {expected_difference}kg")
        print(f"   Actual reading: {post_tare_weight:.2f}kg")
        print(f"   Formula: (raw_value - tare_offset) / 8200 = ({new_weight} - {initial_weight}) = {expected_difference}kg")
    
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
