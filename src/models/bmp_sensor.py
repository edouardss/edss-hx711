from typing import (Any, ClassVar, Mapping, Optional,Sequence)

from typing_extensions import Self
from viam.components.sensor import *
from viam.proto.app.robot import ComponentConfig
from viam.proto.common import ResourceName
from viam.resource.base import ResourceBase
from viam.resource.types import Model, ModelFamily
from viam.utils import SensorReading, ValueTypes
import Adafruit_BMP.BMP085 as BMP085
import board
import busio

class BmpSensor(Sensor):
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
        # Validate sea_level_pressure parameter if provided
        if "sea_level_pressure" in config.attributes:
            try:
                sea_level_pressure = float(config.attributes["sea_level_pressure"])
                if sea_level_pressure <= 0:
                    raise ValueError("sea_level_pressure must be a positive number")
            except (ValueError, TypeError) as e:
                raise ValueError(f"Invalid sea_level_pressure value: {e}")
        
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
            
            # Set sea level pressure from config if provided, otherwise use default
            if "sea_level_pressure" in config.attributes:
                self.sea_level_pressure = float(config.attributes["sea_level_pressure"])
            else:
                self.sea_level_pressure = 1013.25  # Default sea level pressure in hPa
                
        except Exception as e:
            self.logger.error(f"Failed to initialize BMP sensor: {e}")
            self.sensor = None
        
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
                pressure = self.sensor.read_pressure()
                
                # Calculate altitude using the configured sea level pressure
                altitude = self.sensor.read_altitude(self.sea_level_pressure)
                
                readings = {
                    "temperature": float(temperature),
                    "pressure": float(pressure),
                    "altitude": float(altitude),
                    "sea_level_pressure": float(self.sea_level_pressure),
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
        self.logger.error("`do_command` is not implemented")
        raise NotImplementedError()


