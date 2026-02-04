# ENS160

Python library to interface with ScioSense ENS160 Digital Metal-Oxide Multi-Gas Sensor

## Overview

The ENS160 is a digital metal-oxide multi-gas sensor with four sensor elements that can be used to detect a wide range of Volatile Organic Compounds (VOCs). This Python library provides an easy-to-use interface for reading air quality measurements including:

- **Air Quality Index (AQI)**: 1-5 scale rating (1=Excellent, 5=Unhealthy)
- **Total Volatile Organic Compounds (TVOC)**: Measured in parts per billion (ppb)
- **Equivalent CO2 (eCO2)**: Measured in parts per million (ppm)

## Features

- Simple and intuitive API
- Support for both I2C addresses (0x53 default, 0x52 alternate)
- Compatible with smbus2 and CircuitPython/Blinka I2C interfaces
- Temperature and humidity compensation
- Data validity checking
- Firmware version reading
- Multiple operating modes (Standard, Idle, Deep Sleep)

## Installation

### From PyPI (when published)

```bash
pip install ens160
```

### From source

```bash
git clone https://github.com/Haneef-Rahman/ENS160.git
cd ENS160
pip install .
```

### For development

```bash
pip install -e .
```

## Hardware Requirements

- ENS160 sensor breakout board
- I2C interface (e.g., Raspberry Pi, Arduino with Python)
- Proper I2C pull-up resistors (usually included on breakout boards)

### Typical Connections (Raspberry Pi)

| ENS160 Pin | Raspberry Pi Pin |
|------------|------------------|
| VCC        | 3.3V             |
| GND        | GND              |
| SDA        | GPIO 2 (SDA)     |
| SCL        | GPIO 3 (SCL)     |

## Quick Start

```python
from smbus2 import SMBus
from ens160 import ENS160, AQI

# Initialize I2C bus
i2c_bus = SMBus(1)  # Bus 1 on Raspberry Pi

# Create sensor instance
sensor = ENS160(i2c_bus)

# Initialize sensor
if sensor.begin():
    print("Sensor initialized!")
    
    # Wait for valid data
    while not sensor.is_data_valid():
        time.sleep(1)
    
    # Read measurements
    aqi, tvoc, eco2 = sensor.get_all_data()
    
    print(f"AQI: {aqi} ({AQI.get_rating(aqi)})")
    print(f"TVOC: {tvoc} ppb")
    print(f"eCO2: {eco2} ppm")
else:
    print("Failed to initialize sensor!")
```

## Usage Examples

### Basic Reading

```python
import time
from smbus2 import SMBus
from ens160 import ENS160

i2c_bus = SMBus(1)
sensor = ENS160(i2c_bus)

if sensor.begin():
    while True:
        if sensor.is_new_data_available() and sensor.is_data_valid():
            aqi = sensor.get_aqi()
            tvoc = sensor.get_tvoc()
            eco2 = sensor.get_eco2()
            
            print(f"AQI: {aqi}, TVOC: {tvoc} ppb, eCO2: {eco2} ppm")
        
        time.sleep(1)
```

### With Temperature and Humidity Compensation

```python
from smbus2 import SMBus
from ens160 import ENS160

i2c_bus = SMBus(1)
sensor = ENS160(i2c_bus)

if sensor.begin():
    # Set compensation values (if you have external temp/humidity sensor)
    sensor.set_temp_rh(temperature=25.0, humidity=50.0)
    
    # Continue with readings...
    aqi, tvoc, eco2 = sensor.get_all_data()
```

### Using Alternate I2C Address

```python
from smbus2 import SMBus
from ens160 import ENS160

i2c_bus = SMBus(1)

# Use alternate address 0x52
sensor = ENS160(i2c_bus, address=ENS160.I2C_ADDRESS_ALT)

if sensor.begin():
    print("Connected to sensor at address 0x52")
```

### Power Management

```python
from smbus2 import SMBus
from ens160 import ENS160

i2c_bus = SMBus(1)
sensor = ENS160(i2c_bus)

if sensor.begin():
    # Take a reading
    aqi, tvoc, eco2 = sensor.get_all_data()
    
    # Put sensor in deep sleep to save power
    sensor.set_mode(ENS160.MODE_DEEP_SLEEP)
    
    # Later, wake it up
    sensor.set_mode(ENS160.MODE_STANDARD)
```

## API Reference

### ENS160 Class

#### Methods

- `__init__(i2c_bus, address=0x53)`: Initialize the sensor object
- `begin()`: Initialize and configure the sensor (returns True on success)
- `reset()`: Reset the sensor
- `set_mode(mode)`: Set operating mode (MODE_STANDARD, MODE_IDLE, MODE_DEEP_SLEEP)
- `get_aqi()`: Get Air Quality Index (1-5)
- `get_tvoc()`: Get TVOC in ppb
- `get_eco2()`: Get eCO2 in ppm
- `get_all_data()`: Get tuple of (AQI, TVOC, eCO2)
- `is_new_data_available()`: Check if new data is ready
- `is_data_valid()`: Check if data is valid (not in warmup/startup)
- `get_validity_flag()`: Get data validity status
- `set_temp_rh(temperature, humidity)`: Set temperature and humidity compensation
- `get_firmware_version()`: Get firmware version tuple (major, minor, release)

#### Constants

**I2C Addresses:**
- `I2C_ADDRESS_DEFAULT = 0x53`
- `I2C_ADDRESS_ALT = 0x52`

**Operating Modes:**
- `MODE_DEEP_SLEEP`: Deep sleep mode (lowest power)
- `MODE_IDLE`: Idle mode
- `MODE_STANDARD`: Standard measurement mode

**Validity Flags:**
- `VALIDITY_NORMAL`: Data is valid
- `VALIDITY_WARMUP`: Sensor warming up
- `VALIDITY_INITIAL_STARTUP`: Initial startup phase
- `VALIDITY_INVALID`: Invalid data

**AQI Values:**
- `AQI_EXCELLENT = 1`
- `AQI_GOOD = 2`
- `AQI_MODERATE = 3`
- `AQI_POOR = 4`
- `AQI_UNHEALTHY = 5`

### AQI Helper Class

#### Methods

- `AQI.get_rating(aqi)`: Convert AQI number to text rating

## Understanding the Measurements

### Air Quality Index (AQI)

The ENS160 provides a simplified 5-point AQI scale:

| Value | Rating    | Description                           |
|-------|-----------|---------------------------------------|
| 1     | Excellent | Air quality is excellent              |
| 2     | Good      | Air quality is good                   |
| 3     | Moderate  | Air quality is acceptable             |
| 4     | Poor      | Air quality is poor                   |
| 5     | Unhealthy | Air quality is unhealthy              |

### TVOC (Total Volatile Organic Compounds)

Measured in parts per billion (ppb). Common sources of VOCs include:
- Cleaning products
- Paints and solvents
- Building materials
- Furnishings
- Human breath and body odor

### eCO2 (Equivalent CO2)

Measured in parts per million (ppm). This is a calculated value based on VOC levels:
- 400-1000 ppm: Normal outdoor/indoor air
- 1000-2000 ppm: Drowsiness may occur
- 2000+ ppm: Headaches, poor concentration

## Sensor Warmup

The ENS160 requires a warmup period after power-on or reset. During this time:
- Initial warmup: ~3 seconds
- Initial baseline: ~1 hour for best accuracy

Use `is_data_valid()` to check if the sensor has completed warmup.

## Troubleshooting

### Sensor not detected

1. Check I2C connections (SDA, SCL, VCC, GND)
2. Verify I2C address (default: 0x53, alternate: 0x52)
3. Ensure I2C is enabled on your system
4. Check for proper pull-up resistors on I2C lines
5. Try scanning I2C bus: `i2cdetect -y 1`

### Invalid readings

1. Wait for sensor warmup (check `is_data_valid()`)
2. Ensure stable power supply (3.3V)
3. Check for I2C communication errors

### Erratic readings

1. Apply temperature and humidity compensation if available
2. Ensure good air circulation around sensor
3. Allow 1-hour stabilization for best accuracy

## Examples

See the `examples/` directory for complete working examples:
- `basic_example.py`: Basic usage with continuous reading

## Dependencies

- `smbus2` (for standard Linux I2C)

Optional:
- CircuitPython libraries (for use with CircuitPython/Blinka)

## License

MIT License - see LICENSE file for details

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## References

- [ENS160 Datasheet](https://www.sciosense.com/products/environmental-sensors/ens160-digital-metal-oxide-multi-gas-sensor/)
- ScioSense ENS160 Product Page

## Author

Haneef Rahman

## Acknowledgments

Based on the ScioSense ENS160 specifications and datasheet.
