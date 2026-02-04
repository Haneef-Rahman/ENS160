"""
ENS160 - Python library for ScioSense ENS160 Digital Metal-Oxide Multi-Gas Sensor

This library provides an interface to the ENS160 sensor for measuring:
- Air Quality Index (AQI)
- Total Volatile Organic Compounds (TVOC)
- Equivalent CO2 (eCO2)
"""

from .ens160 import ENS160, AQI

__version__ = "0.1.0"
__author__ = "Haneef Rahman"
__all__ = ["ENS160", "AQI"]
