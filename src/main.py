import asyncio
from typing import Any, ClassVar, Dict, Final, Mapping, Optional, Sequence

from typing_extensions import Self
from viam.components.sensor import *
from viam.module.module import Module
from viam.proto.app.robot import ComponentConfig
from viam.proto.common import ResourceName
from viam.resource.base import ResourceBase
from viam.resource.easy_resource import EasyResource
from viam.resource.types import Model, ModelFamily
from viam.utils import SensorReading, struct_to_dict, ValueTypes
import random
from hx711 import HX711
import RPi.GPIO as GPIO

class Loadcell(Sensor, EasyResource):
    MODEL: ClassVar[Model] = Model(ModelFamily("edss", "hx711-loadcell"), "loadcell")

    @classmethod
    def new(
        cls, config: ComponentConfig, dependencies: Mapping[ResourceName, ResourceBase]
    ) -> Self:
        return super().new(config, dependencies)

    @classmethod
    def validate_config(cls, config: ComponentConfig) -> Sequence[str]:
        fields = config.attributes.fields

        if "gain" in fields:
            if not fields["gain"].HasField("number_value"):
                raise Exception("Gain must be a valid number.")
        if "doutPin" in fields:
            if not fields["doutPin"].HasField("number_value"):
                raise Exception("Data Out pin must be a valid number.")
        if "sckPin" in fields:
            if not fields["sckPin"].HasField("number_value"):
                raise Exception("Clock pin must be a valid number.")
        if "numberOfReadings" in fields:
            if not fields["numberOfReadings"].HasField("number_value"):
                raise Exception("Number of readings must be a valid number.")
        if "tare_offset" in fields:
            if not fields["tare_offset"].HasField("number_value"):
                raise Exception("Tare offset must be a valid number.")
        # If all checks pass, return an empty list indicating no errors

        return []

    def reconfigure(
        self, config: ComponentConfig, dependencies: Mapping[ResourceName, ResourceBase]
    ):
        attrs = struct_to_dict(config.attributes)
        self.gain = float(attrs.get("gain", 64))
        self.doutPin = int(attrs.get("doutPin", 5))
        self.sckPin = int(attrs.get("sckPin", 6))
        self.numberOfReadings = int(attrs.get("numberOfReadings", 3))
        self.tare_offset = float(attrs.get("tare_offset", 0.0))
        
        self.logger.debug(f"Reconfigured with gain {self.gain}, doutPin {self.doutPin}, sckPin {self.sckPin}, numberOfReadings {self.numberOfReadings}, tare_offset {self.tare_offset}")
       
        # Initialize HX711 object if not already done
        if not hasattr(self, 'hx711') or self.hx711 is None:
            self.hx711 = None
            self.get_hx711()
            
        return super().reconfigure(config, dependencies)

    def get_hx711(self):
        """Get the HX711 instance, creating it if necessary."""
        if self.hx711 is None:
            try:
                self.logger.debug(f"Initializing HX711 with doutPin {self.doutPin}, sckPin {self.sckPin}, gain {self.gain}")
                self.hx711 = HX711(
                    dout_pin=self.doutPin,
                    pd_sck_pin=self.sckPin,
                    channel='A',
                    gain=self.gain
                )
                # Reset the HX711 only when first created
                self.hx711.reset()
                self.logger.debug("HX711 initialized and reset successfully")
            except Exception as e:
                self.logger.error(f"Failed to initialize HX711: {e}")
                # Clean up the failed object
                if hasattr(self, 'hx711') and self.hx711 is not None:
                    try:
                        del self.hx711
                    except Exception as cleanup_error:
                        self.logger.warning(f"Error cleaning up failed HX711 object: {cleanup_error}")
                self.hx711 = None
                raise
        return self.hx711

    def cleanup_gpio_pins(self):
        """Clean up only the specific GPIO pins used by this sensor."""
        try:
            self.logger.debug(f"Cleaning up GPIO pins {self.doutPin}, {self.sckPin}")
            GPIO.cleanup((self.doutPin, self.sckPin))
        except Exception as e:
            self.logger.warning(f"Error cleaning up GPIO pins {self.doutPin}, {self.sckPin}: {e}")

    def close(self):
        """Clean up resources when the component is closed."""
        try:
            if hasattr(self, 'hx711') and self.hx711 is not None:
                del self.hx711
                self.hx711 = None
            self.cleanup_gpio_pins()
            self.logger.debug("Load cell component closed and resources cleaned up")
        except Exception as e:
            self.logger.warning(f"Error during component cleanup: {e}")

    async def get_readings(
        self,
        *,
        extra: Optional[Mapping[str, Any]] = None,
        timeout: Optional[float] = None,
        **kwargs
    ) -> Mapping[str, SensorReading]:
        
        try:
            self.logger.debug("Getting readings from load cell")
            hx711 = self.get_hx711()
            measures = hx711.get_raw_data(times=self.numberOfReadings)
            # Convert each measure to kgs by subtracting tare offset and dividing by 8200
            measures_kg = [(measure - self.tare_offset) / 8200 for measure in measures]
            avg_kgs = sum(measures_kg) / len(measures_kg)  # Assuming 8200 ~ 1kg, then this converts to kg
            
            # Return a dictionary of the readings
            return {
                "doutPin": self.doutPin,
                "sckPin": self.sckPin,
                "gain": self.gain,
                "numberOfReadings": self.numberOfReadings,
                "tare_offset": self.tare_offset / 8200, # reporting tare value in kgs for consistency with readings
                "measures": measures_kg,  # Now returning measures in kg
                "weight": avg_kgs
            }
        except Exception as e:
            self.logger.error(f"Error getting readings from load cell: {e}")
            # If there's an error, clean up and reset the HX711 object for next time
            if hasattr(self, 'hx711') and self.hx711 is not None:
                try:
                    del self.hx711
                except Exception as cleanup_error:
                    self.logger.warning(f"Error cleaning up HX711 object after reading error: {cleanup_error}")
            self.hx711 = None
            raise

    async def tare(self):
        """Tare the load cell by setting the current reading as the zero offset."""
        
        try:
            self.logger.debug("Taring load cell")
            hx711 = self.get_hx711()
            measures = hx711.get_raw_data(times=self.numberOfReadings)
            self.tare_offset = sum(measures) / len(measures)  # Set tare offset
            self.logger.debug(f"Tare completed. New offset: {self.tare_offset}")
        except Exception as e:
            self.logger.error(f"Error during tare operation: {e}")
            # If there's an error, clean up and reset the HX711 object for next time
            if hasattr(self, 'hx711') and self.hx711 is not None:
                try:
                    del self.hx711
                except Exception as cleanup_error:
                    self.logger.warning(f"Error cleaning up HX711 object after tare error: {cleanup_error}")
            self.hx711 = None
            raise

    async def do_command(
            self,
            command: Mapping[str, ValueTypes],
            *,
            timeout: Optional[float] = None,
            **kwargs
        ) -> Mapping[str, ValueTypes]:
            result = {key: False for key in command.keys()}
            for (name, args) in command.items():
                if name == "tare":
                    await self.tare(*args)
                    result[name] = self.tare_offset / 8200
            return result

if __name__ == "__main__":
    asyncio.run(Module.run_from_registry())
