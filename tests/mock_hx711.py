"""
Mock HX711 simulation class for testing load cell components.
Simulates realistic HX711 load cell behavior without hardware.
"""

import random
import time
from typing import List, Optional
from enum import Enum


class SimulationMode(Enum):
    """Different simulation modes for testing various scenarios."""
    NORMAL = "normal"
    ERROR = "error"
    TIMEOUT = "timeout"
    INVALID_DATA = "invalid_data"
    NOISY = "noisy"
    DRIFT = "drift"


class MockHX711:
    """
    Mock HX711 load cell sensor for testing.
    
    Simulates realistic load cell behavior including:
    - Raw data readings
    - Reset functionality
    - Error conditions
    - Noise and drift
    - Different weight scenarios
    """
    
    def __init__(
        self, 
        dout_pin: int, 
        pd_sck_pin: int, 
        channel: str = 'A', 
        gain: int = 64,
        simulation_mode: SimulationMode = SimulationMode.NORMAL
    ):
        self.dout_pin = dout_pin
        self.pd_sck_pin = pd_sck_pin
        self.channel = channel
        self.gain = gain
        self.simulation_mode = simulation_mode
        
        # State tracking
        self.is_reset = False
        self.call_count = 0
        self.weight_kg = 0.0
        self.tare_offset = 0.0
        self.noise_level = 0.02  # 2% noise
        self.drift_rate = 0.001  # 0.1% per reading
        self.temperature_drift = 0.0
        
        # Error simulation
        self.error_probability = 0.0
        self.timeout_probability = 0.0
        
        # Performance simulation
        self.reading_delay = 0.001  # 1ms delay per reading
        
    def reset(self):
        """Simulate HX711 reset operation."""
        if self.simulation_mode == SimulationMode.ERROR and random.random() < self.error_probability:
            raise Exception("Simulated reset error")
            
        self.is_reset = True
        self.call_count += 1
        
    def get_raw_data(self, times: int = 1) -> List[int]:
        """
        Simulate getting raw data from load cell.
        
        Args:
            times: Number of readings to take
            
        Returns:
            List of raw integer readings
            
        Raises:
            Exception: If simulation mode is ERROR or other error conditions
            TimeoutError: If simulation mode is TIMEOUT
        """
        if not self.is_reset:
            raise Exception("HX711 not reset before reading")
            
        if self.simulation_mode == SimulationMode.ERROR:
            if random.random() < self.error_probability:
                raise Exception("Simulated hardware error during reading")
                
        if self.simulation_mode == SimulationMode.TIMEOUT:
            if random.random() < self.timeout_probability:
                raise TimeoutError("Simulated timeout during reading")
                
        if self.simulation_mode == SimulationMode.INVALID_DATA:
            return [None, "invalid", 0, -999999]
            
        # Simulate reading delay
        time.sleep(self.reading_delay)
        
        readings = []
        for i in range(times):
            reading = self._generate_realistic_reading(i)
            readings.append(reading)
            
        return readings
    
    def _generate_realistic_reading(self, reading_index: int) -> int:
        """Generate a realistic load cell reading."""
        # Convert kg to raw units (8200 units per kg is typical)
        base_reading = int((self.weight_kg - self.tare_offset) * 8200)
        
        if self.simulation_mode == SimulationMode.NOISY:
            # Add significant noise
            noise = random.gauss(0, self.noise_level * 10 * abs(base_reading))
            base_reading += int(noise)
            
        elif self.simulation_mode == SimulationMode.DRIFT:
            # Add time-based drift
            drift = reading_index * self.drift_rate * abs(base_reading)
            base_reading += int(drift)
            
        else:
            # Normal mode with small noise
            noise = random.gauss(0, self.noise_level * abs(base_reading))
            base_reading += int(noise)
            
        # Add temperature drift
        base_reading += int(self.temperature_drift * 8200)
        
        # Ensure reading is within valid 24-bit signed integer range
        base_reading = max(-8388608, min(8388607, base_reading))
        
        return base_reading
    
    def set_simulated_weight(self, weight_kg: float):
        """Set the simulated weight for testing."""
        self.weight_kg = weight_kg
        
    def set_tare_offset(self, offset: float):
        """Set the tare offset for testing."""
        self.tare_offset = offset
        
    def set_noise_level(self, level: float):
        """Set the noise level (0.0 to 1.0)."""
        self.noise_level = max(0.0, min(1.0, level))
        
    def set_temperature_drift(self, drift_kg: float):
        """Set temperature drift in kg."""
        self.temperature_drift = drift_kg
        
    def set_error_probability(self, probability: float):
        """Set probability of errors (0.0 to 1.0)."""
        self.error_probability = max(0.0, min(1.0, probability))
        
    def set_timeout_probability(self, probability: float):
        """Set probability of timeouts (0.0 to 1.0)."""
        self.timeout_probability = max(0.0, min(1.0, probability))
        
    def set_reading_delay(self, delay_seconds: float):
        """Set delay between readings for performance testing."""
        self.reading_delay = max(0.0, delay_seconds)
        
    def get_state(self) -> dict:
        """Get current simulation state for debugging."""
        return {
            "is_reset": self.is_reset,
            "call_count": self.call_count,
            "weight_kg": self.weight_kg,
            "tare_offset": self.tare_offset,
            "simulation_mode": self.simulation_mode.value,
            "noise_level": self.noise_level,
            "temperature_drift": self.temperature_drift,
            "error_probability": self.error_probability,
            "timeout_probability": self.timeout_probability
        }


class MockHX711Factory:
    """Factory for creating MockHX711 instances with different configurations."""
    
    @staticmethod
    def create_normal(dout_pin: int = 5, pd_sck_pin: int = 6, gain: int = 64) -> MockHX711:
        """Create a normal operating MockHX711."""
        return MockHX711(dout_pin, pd_sck_pin, 'A', gain, SimulationMode.NORMAL)
        
    @staticmethod
    def create_noisy(dout_pin: int = 5, pd_sck_pin: int = 6, gain: int = 64) -> MockHX711:
        """Create a noisy MockHX711 for testing noise handling."""
        mock = MockHX711(dout_pin, pd_sck_pin, 'A', gain, SimulationMode.NOISY)
        mock.set_noise_level(0.05)  # 5% noise
        return mock
        
    @staticmethod
    def create_error_prone(dout_pin: int = 5, pd_sck_pin: int = 6, gain: int = 64) -> MockHX711:
        """Create an error-prone MockHX711 for testing error handling."""
        mock = MockHX711(dout_pin, pd_sck_pin, 'A', gain, SimulationMode.ERROR)
        mock.set_error_probability(0.1)  # 10% error rate
        return mock
        
    @staticmethod
    def create_timeout_prone(dout_pin: int = 5, pd_sck_pin: int = 6, gain: int = 64) -> MockHX711:
        """Create a timeout-prone MockHX711 for testing timeout handling."""
        mock = MockHX711(dout_pin, pd_sck_pin, 'A', gain, SimulationMode.TIMEOUT)
        mock.set_timeout_probability(0.1)  # 10% timeout rate
        return mock
        
    @staticmethod
    def create_drifting(dout_pin: int = 5, pd_sck_pin: int = 6, gain: int = 64) -> MockHX711:
        """Create a drifting MockHX711 for testing drift handling."""
        mock = MockHX711(dout_pin, pd_sck_pin, 'A', gain, SimulationMode.DRIFT)
        mock.set_temperature_drift(0.01)  # 10g drift
        return mock
