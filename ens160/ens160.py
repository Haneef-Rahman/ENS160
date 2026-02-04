"""
ENS160 Digital Metal-Oxide Multi-Gas Sensor Driver

This module provides a Python interface for the ScioSense ENS160 sensor,
which measures air quality index (AQI), total volatile organic compounds (TVOC),
and equivalent CO2 (eCO2).
"""

import time
from typing import Tuple, Optional


class ENS160:
    """
    Driver class for the ENS160 Digital Metal-Oxide Multi-Gas Sensor.
    
    The ENS160 is an I2C digital metal-oxide multi-gas sensor that provides
    measurements for:
    - Air Quality Index (AQI): 1-5 scale
    - Total Volatile Organic Compounds (TVOC): ppb
    - Equivalent CO2 (eCO2): ppm
    """
    
    # Default I2C address
    I2C_ADDRESS_DEFAULT = 0x53
    I2C_ADDRESS_ALT = 0x52
    
    # Register addresses
    REG_PART_ID = 0x00
    REG_OPMODE = 0x10
    REG_CONFIG = 0x11
    REG_COMMAND = 0x12
    REG_TEMP_IN = 0x13
    REG_RH_IN = 0x15
    REG_DATA_STATUS = 0x20
    REG_DATA_AQI = 0x21
    REG_DATA_TVOC = 0x22
    REG_DATA_ECO2 = 0x24
    REG_DATA_ETOH = 0x22  # Raw ethanol data
    REG_DATA_T = 0x30
    REG_DATA_RH = 0x32
    REG_DATA_MISR = 0x38
    REG_GPR_WRITE_0 = 0x40
    REG_GPR_READ_4 = 0x48
    
    # Part ID
    PART_ID = 0x0160
    
    # Operating modes
    MODE_DEEP_SLEEP = 0x00
    MODE_IDLE = 0x01
    MODE_STANDARD = 0x02
    MODE_RESET = 0xF0
    
    # Command register values
    CMD_NOP = 0x00
    CMD_GET_APPVER = 0x0E
    CMD_CLRGPR = 0xCC
    
    # Status bits
    STATUS_NEWGPR = 0x01
    STATUS_NEWDAT = 0x02
    STATUS_VALIDITY_FLAG = 0x0C
    STATUS_STATAS = 0x80
    STATUS_STATER = 0x40
    
    # Validity flags
    VALIDITY_NORMAL = 0x00
    VALIDITY_WARMUP = 0x01
    VALIDITY_INITIAL_STARTUP = 0x02
    VALIDITY_INVALID = 0x03
    
    # AQI ratings
    AQI_EXCELLENT = 1
    AQI_GOOD = 2
    AQI_MODERATE = 3
    AQI_POOR = 4
    AQI_UNHEALTHY = 5
    
    def __init__(self, i2c_bus, address: int = I2C_ADDRESS_DEFAULT):
        """
        Initialize the ENS160 sensor.
        
        Args:
            i2c_bus: I2C bus object (e.g., from smbus2 or busio)
            address: I2C address of the sensor (default: 0x53)
        """
        self.i2c = i2c_bus
        self.address = address
        self._initialized = False
        
    def begin(self) -> bool:
        """
        Initialize the sensor and verify communication.
        
        Returns:
            bool: True if initialization successful, False otherwise
        """
        try:
            # Check part ID
            part_id = self._read_word(self.REG_PART_ID)
            if part_id != self.PART_ID:
                return False
            
            # Reset the sensor
            self.reset()
            time.sleep(0.1)
            
            # Set to idle mode first
            self._write_byte(self.REG_OPMODE, self.MODE_IDLE)
            time.sleep(0.01)
            
            # Set to standard mode
            self._write_byte(self.REG_OPMODE, self.MODE_STANDARD)
            time.sleep(0.01)
            
            self._initialized = True
            return True
            
        except Exception as e:
            print(f"Initialization error: {e}")
            return False
    
    def reset(self):
        """Reset the sensor."""
        self._write_byte(self.REG_OPMODE, self.MODE_RESET)
        time.sleep(0.1)
    
    def set_mode(self, mode: int):
        """
        Set the operating mode of the sensor.
        
        Args:
            mode: Operating mode (MODE_DEEP_SLEEP, MODE_IDLE, MODE_STANDARD)
        """
        self._write_byte(self.REG_OPMODE, mode)
        time.sleep(0.02)
    
    def get_status(self) -> int:
        """
        Get the sensor status.
        
        Returns:
            int: Status byte
        """
        return self._read_byte(self.REG_DATA_STATUS)
    
    def is_new_data_available(self) -> bool:
        """
        Check if new data is available.
        
        Returns:
            bool: True if new data available
        """
        status = self.get_status()
        return bool(status & self.STATUS_NEWDAT)
    
    def get_validity_flag(self) -> int:
        """
        Get the data validity flag.
        
        Returns:
            int: Validity flag (VALIDITY_NORMAL, VALIDITY_WARMUP, 
                 VALIDITY_INITIAL_STARTUP, VALIDITY_INVALID)
        """
        status = self.get_status()
        return (status & self.STATUS_VALIDITY_FLAG) >> 2
    
    def is_data_valid(self) -> bool:
        """
        Check if sensor data is valid (not in warmup or startup).
        
        Returns:
            bool: True if data is valid
        """
        return self.get_validity_flag() == self.VALIDITY_NORMAL
    
    def get_aqi(self) -> int:
        """
        Get the Air Quality Index (AQI).
        
        Returns:
            int: AQI value (1-5)
                1 = Excellent
                2 = Good
                3 = Moderate
                4 = Poor
                5 = Unhealthy
        """
        return self._read_byte(self.REG_DATA_AQI)
    
    def get_tvoc(self) -> int:
        """
        Get the Total Volatile Organic Compounds (TVOC) measurement.
        
        Returns:
            int: TVOC in ppb (parts per billion)
        """
        return self._read_word(self.REG_DATA_TVOC)
    
    def get_eco2(self) -> int:
        """
        Get the equivalent CO2 (eCO2) measurement.
        
        Returns:
            int: eCO2 in ppm (parts per million)
        """
        return self._read_word(self.REG_DATA_ECO2)
    
    def get_all_data(self) -> Tuple[int, int, int]:
        """
        Get all sensor measurements at once.
        
        Returns:
            Tuple[int, int, int]: (AQI, TVOC in ppb, eCO2 in ppm)
        """
        aqi = self.get_aqi()
        tvoc = self.get_tvoc()
        eco2 = self.get_eco2()
        return (aqi, tvoc, eco2)
    
    def set_temp_rh(self, temperature: float, humidity: float):
        """
        Set temperature and humidity compensation values.
        
        Args:
            temperature: Temperature in Celsius
            humidity: Relative humidity in %
        """
        # Convert temperature to format expected by sensor
        # (temperature + 273.15) * 64
        temp_kelvin = int((temperature + 273.15) * 64)
        self._write_word(self.REG_TEMP_IN, temp_kelvin)
        
        # Convert humidity to format expected by sensor
        # humidity * 512
        rh_value = int(humidity * 512)
        self._write_word(self.REG_RH_IN, rh_value)
    
    def get_firmware_version(self) -> Tuple[int, int, int]:
        """
        Get the firmware version.
        
        Returns:
            Tuple[int, int, int]: (major, minor, release)
        """
        self._write_byte(self.REG_COMMAND, self.CMD_GET_APPVER)
        time.sleep(0.01)
        
        # Read from GPR registers
        gpr_data = []
        for i in range(3):
            gpr_data.append(self._read_byte(self.REG_GPR_READ_4 + i))
        
        return (gpr_data[0], gpr_data[1], gpr_data[2])
    
    def _read_byte(self, register: int) -> int:
        """
        Read a single byte from a register.
        
        Args:
            register: Register address
            
        Returns:
            int: Byte value
        """
        try:
            # Try smbus2 style first
            return self.i2c.read_byte_data(self.address, register)
        except AttributeError:
            # Try busio/CircuitPython style
            result = bytearray(1)
            self.i2c.writeto_then_readfrom(self.address, bytes([register]), result)
            return result[0]
    
    def _read_word(self, register: int) -> int:
        """
        Read a 16-bit word from a register (little-endian).
        
        Args:
            register: Register address
            
        Returns:
            int: Word value
        """
        try:
            # Try smbus2 style first
            return self.i2c.read_word_data(self.address, register)
        except AttributeError:
            # Try busio/CircuitPython style
            result = bytearray(2)
            self.i2c.writeto_then_readfrom(self.address, bytes([register]), result)
            return result[0] | (result[1] << 8)
    
    def _write_byte(self, register: int, value: int):
        """
        Write a single byte to a register.
        
        Args:
            register: Register address
            value: Byte value to write
        """
        try:
            # Try smbus2 style first
            self.i2c.write_byte_data(self.address, register, value)
        except AttributeError:
            # Try busio/CircuitPython style
            self.i2c.writeto(self.address, bytes([register, value]))
    
    def _write_word(self, register: int, value: int):
        """
        Write a 16-bit word to a register (little-endian).
        
        Args:
            register: Register address
            value: Word value to write
        """
        try:
            # Try smbus2 style first
            self.i2c.write_word_data(self.address, register, value)
        except AttributeError:
            # Try busio/CircuitPython style
            low_byte = value & 0xFF
            high_byte = (value >> 8) & 0xFF
            self.i2c.writeto(self.address, bytes([register, low_byte, high_byte]))


class AQI:
    """Helper class for AQI rating descriptions."""
    
    RATINGS = {
        1: "Excellent",
        2: "Good", 
        3: "Moderate",
        4: "Poor",
        5: "Unhealthy"
    }
    
    @staticmethod
    def get_rating(aqi: int) -> str:
        """
        Get the text description for an AQI value.
        
        Args:
            aqi: AQI value (1-5)
            
        Returns:
            str: Rating description
        """
        return AQI.RATINGS.get(aqi, "Unknown")
