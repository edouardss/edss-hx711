from typing import (Any, ClassVar, Mapping, Optional,Sequence)

from typing_extensions import Self
from viam.components.sensor import *
from viam.proto.app.robot import ComponentConfig
from viam.proto.common import ResourceName
from viam.resource.base import ResourceBase
from viam.resource.easy_resource import EasyResource
from viam.resource.types import Model, ModelFamily
from viam.utils import SensorReading, ValueTypes, struct_to_dict
import Adafruit_BMP.BMP085 as BMP085
import board
import busio

class BmpSensor(Sensor, EasyResource):
    # To enable debug-level logging, either run viam-server with the --debug option,
    # or configure your resource/machine to display debug logs.
    MODEL: ClassVar[Model] = Model(ModelFamily("edss", "i2c-sensors"), "bmp-sensor")
    # print('MODEL: ', Self.MODEL)

    @classmethod
    def new(
        cls, config: ComponentConfig, dependencies: Mapping[ResourceName, ResourceBase]
    ) -> Self:
        """This method creates a new instance of this Sensor component.
        The default implementation sets the name from the `config` parameter and then calls `reconfigure`.

        Args:
            config (ComponentConfig): The configuration for this resource
            dependencies (Mapping[ResourceName, ResourceBase]): The dependencies (both implicit and explicit)

        Returns:
            Self: The resource
        """
        return super().new(config, dependencies)

    @classmethod
    def validate_config(cls, config: ComponentConfig) -> Sequence[str]:
        """This method allows you to validate the configuration object received from the machine,
        as well as to return any implicit dependencies based on that `config`.

        Args:
            config (ComponentConfig): The configuration for this resource

        Returns:
            Sequence[str]: A list of implicit dependencies
        """
        fields = config.attributes.fields

        # Validate sea_level_pressure parameter if provided
        if "sea_level_pressure" in fields:
            if not(fields["sea_level_pressure"].HasField("number_value")):
                raise ValueError("sea_level_pressure must be a valid number")
            else:
                sea_level_pressure = int(fields["sea_level_pressure"].number_value)
                if sea_level_pressure <= 0:
                    raise ValueError("sea_level_pressure must be a positive number")
        
        return []

    def reconfigure(
        self, config: ComponentConfig, dependencies: Mapping[ResourceName, ResourceBase]
    ):
        """This method allows you to dynamically update your service when it receives a new `config` object.

        Args:
            config (ComponentConfig): The new configuration
            dependencies (Mapping[ResourceName, ResourceBase]): Any dependencies (both implicit and explicit)
        """
        try:
            # Initialize I2C and BMP sensor
            i2c = busio.I2C(board.SCL, board.SDA)
            self.sensor = BMP085.BMP085(busnum=1)
            
            attrs = struct_to_dict(config.attributes)
            self.sea_level_pressure = int(attrs.get("sea_level_pressure", 101325))  # Default sea level pressure in hPa*100
            
            # Initialize tare offsets (default to 0 - no offset)
            self.pressure_offset = 0.0
            self.altitude_offset = 0.0

        except Exception as e:
            self.logger.error(f"Failed to initialize BMP sensor: {e}")
            self.sensor = None
            raise
 
        return super().reconfigure(config, dependencies)

    async def get_readings(
        self,
        *,
        extra: Optional[Mapping[str, Any]] = None,
        timeout: Optional[float] = None,
        **kwargs
    ) -> Mapping[str, SensorReading]:
        if self.sensor:
            try:
                # Read sensor data
                temperature = self.sensor.read_temperature()
                raw_pressure = self.sensor.read_pressure()
                raw_altitude = self.sensor.read_altitude(self.sea_level_pressure)
                
                # Apply tare offsets (always applied, defaults to 0)
                pressure = raw_pressure - self.pressure_offset
                altitude = raw_altitude - self.altitude_offset
                
                readings = {
                    "temperature - C": float(temperature),
                    "pressure - Pa": float(pressure),
                    "altitude - m": float(altitude),
                    "sea_level_pressure - Pa": float(self.sea_level_pressure),
                    "raw_pressure - Pa": float(raw_pressure),
                    "raw_altitude - m": float(raw_altitude),
                    "pressure_offset - Pa": float(self.pressure_offset),
                    "altitude_offset - m": float(self.altitude_offset),
                }
                
                return readings
            except Exception as e:
                self.logger.error(f"Error reading sensor data: {e}")
                return {}
        else:
            self.logger.error("Sensor not initialized")
            return {}

    async def do_command(
        self,
        command: Mapping[str, ValueTypes],
        *,
        timeout: Optional[float] = None,
        **kwargs
    ) -> Mapping[str, ValueTypes]:
        """Handle custom commands for the BMP sensor.
        
        Supported commands:
        - "tare": Set current pressure and altitude as baseline (offset = 0)
        - "reset_tare": Clear tare offsets and reset to original readings
        """
        if not self.sensor:
            self.logger.error("Sensor not initialized")
            return {"error": "Sensor not initialized"}
        
        command_name = command.get("command", "").lower()
        
        try:
            if command_name == "tare":
                # Read current values and set as baseline (offset = 0)
                self.pressure_offset = self.sensor.read_pressure()
                self.altitude_offset = self.sensor.read_altitude(self.sea_level_pressure)
                
                self.logger.info(f"Tare set - Pressure baseline: {self.pressure_offset:.2f} Pa, Altitude baseline: {self.altitude_offset:.2f} m")
                
                return {
                    "status": "tare_completed",
                    "pressure_offset": float(self.pressure_offset),
                    "altitude_offset": float(self.altitude_offset),
                    "message": "Tare completed successfully"
                }
                
            elif command_name == "reset_tare":
                # Clear tare offsets
                self.pressure_offset = 0.0
                self.altitude_offset = 0.0
                
                self.logger.info("Tare reset - returning to raw readings")
                
                return {
                    "status": "tare_reset",
                    "message": "Tare reset successfully"
                }
                
            else:
                return {
                    "error": f"Unknown command: {command_name}",
                    "available_commands": ["tare", "reset_tare"]
                }
                
        except Exception as e:
            self.logger.error(f"Error executing command '{command_name}': {e}")
            return {"error": f"Command failed: {str(e)}"}


