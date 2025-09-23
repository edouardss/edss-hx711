"""Main entry point for the HX711 load cell module."""

import asyncio
import sys

from viam.module.module import Module

try:
    from models.loadcell import LoadCell
    print("LoadCell imported normally")
except Exception as e:
    print("LoadCell error occured: ", e)
    try:
        from .models.loadcell import LoadCell
        print("LoadCell imported locally")
    except Exception as e:
        print("LoadCell error occured: ", e)
        print("Could not find the module LoadCell, locally")
        sys.exit(1)

try:
    from models.bmp_sensor import BmpSensor
    print("BmpSensor imported normally")
except Exception as e:
    print("BmpSensor error occured: ", e)
    try:
        from .models.bmp_sensor import BmpSensor
        print("BmpSensor imported locally")
    except Exception as e:
        print("BmpSensor error occured: ", e)
        print("Could not find the module BmpSensor, locally")
        sys.exit(1)

try:
    from models.imu_sensor import ImuSensor
    print("ImuSensor imported normally")
except Exception as e:
    print("ImuSensor error occured: ", e)
    try:
        from .models.imu_sensor import ImuSensor
        print("ImuSensor imported locally")
    except Exception as e:
        print("ImuSensor error occured: ", e)
        print("Could not find the module ImuSensor, locally")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(Module.run_from_registry())
