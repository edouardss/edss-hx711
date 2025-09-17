"""Main entry point for the HX711 load cell module."""

import asyncio

from viam.module.module import Module

try:
    from models.loadcell import Loadcell
    print("LoadCell imported normally")
except Exception as e:
    print("LoadCell error occured: ", e)
    try:
        from .models.loadcell import Loadcell
        print("LoadCell imported locally")
    except Exception as e:
        print("LoadCell error occured: ", e)
        print("Count not find the module LoadCell, locally")
        exit(1)

try:
    from models.bmp_sensor import BmpSensor
    print("BmpSensor imported normally")
except Exception as e:
    print("LoadCell error occured: ", e)
    try:
        from .models import BmpSensor
        print("BmpSensor imported locally")
    except Exception as e:
        print("BmpSensor error occured: ", e)
        print("Count not find the module BmpSensor, locally")
        exit(1)


if __name__ == "__main__":
    asyncio.run(Module.run_from_registry())
