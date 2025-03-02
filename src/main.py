import asyncio
from typing import Any, ClassVar, Final, List, Mapping, Optional, Sequence

from typing_extensions import Self
from viam.components.sensor import Sensor
from viam.module.module import Module
from viam.proto.app.robot import ComponentConfig
from viam.proto.common import ResourceName
from viam.resource.base import ResourceBase
from viam.resource.easy_resource import EasyResource
from viam.resource.types import Model, ModelFamily
from viam.utils import SensorReading, struct_to_dict

import RPi.GPIO as GPIO
from hx711 import HX711

class Loadcell(Sensor, EasyResource):
    MODEL: ClassVar[Model] = Model(ModelFamily("kodama", "hx711-loadcell"), "loadcell")

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

        if "gain" in fields:
            if not fields["gain"].HasField("number_value"):
                raise Exception("Gain must be a valid number.")
        if "doutPin" in fields:
            if not fields["doutPin"].HasField("number_value"):
                raise Exception("Data Out pin must be a valid number.")
        if "sckPin" in fields:
            if not fields["sckPin"].HasField("number_value"):
                raise Exception("Gain must be a valid number.")
        if "numberOfReadings" in fields:
            if not fields["numberOfReadings"].HasField("number_value"):
                raise Exception("Gain must be a valid number.")

        return []

    def reconfigure(
        self, config: ComponentConfig, dependencies: Mapping[ResourceName, ResourceBase]
    ):
        """This method allows you to dynamically update your service when it receives a new `config` object.

        Args:
            config (ComponentConfig): The new configuration
            dependencies (Mapping[ResourceName, ResourceBase]): Any dependencies (both implicit and explicit)
        """
        attrs = struct_to_dict(config.attributes)
        self.gain = float(attrs.get("gain", 64))
        self.doutPin = int(attrs.get("doutPin", 5))
        self.sckPin = int(attrs.get("sckPin", 6))
        self.numberOfReadings = int(attrs.get("numberOfReadings", 3))
        return super().reconfigure(config, dependencies)

    async def get_readings(
        self,
        *,
        extra: Optional[Mapping[str, Any]] = None,
        timeout: Optional[float] = None,
        **kwargs
    ) -> Mapping[str, SensorReading]:
        
        try:
            hx711 = HX711(
                dout_pin=self.doutPin,
                pd_sck_pin=self.sckPin,
                channel='A',
                gain=self.gain
            )

            hx711.reset()   # Before we start, reset the HX711 (not obligate)
            measures = hx711.get_raw_data(times=self.numberOfReadings)
            avg = sum(measures) / len(measures)
        finally:
            GPIO.cleanup()  # always do a GPIO cleanup in your scripts!


        # Return a dictionary of the readings
        return {
            "weight": avg
        }

if __name__ == "__main__":
    asyncio.run(Module.run_from_registry())

