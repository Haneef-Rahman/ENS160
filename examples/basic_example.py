#!/usr/bin/env python3
"""
Basic example for using the ENS160 sensor library.

This example demonstrates how to:
1. Initialize the ENS160 sensor
2. Read air quality measurements
3. Display AQI, TVOC, and eCO2 values
"""

import time
from smbus2 import SMBus
from ens160 import ENS160, AQI


def main():
    """Main example function."""
    # Initialize I2C bus (typically bus 1 on Raspberry Pi)
    i2c_bus = SMBus(1)
    
    # Create ENS160 sensor instance
    # Use default address 0x53, or specify alternate address 0x52
    sensor = ENS160(i2c_bus)
    
    # Initialize the sensor
    print("Initializing ENS160 sensor...")
    if not sensor.begin():
        print("Failed to initialize ENS160 sensor!")
        print("Please check:")
        print("  - I2C connections")
        print("  - I2C address (default: 0x53, alternate: 0x52)")
        print("  - Power supply to sensor")
        return
    
    print("ENS160 sensor initialized successfully!")
    
    # Get firmware version
    try:
        major, minor, release = sensor.get_firmware_version()
        print(f"Firmware version: {major}.{minor}.{release}")
    except Exception as e:
        print(f"Could not read firmware version: {e}")
    
    print("\nWaiting for sensor warmup...")
    print("This may take a few seconds...\n")
    
    # Wait for sensor to warm up
    warmup_timeout = 30  # 30 seconds timeout
    start_time = time.time()
    
    while not sensor.is_data_valid():
        if time.time() - start_time > warmup_timeout:
            print("Warning: Sensor warmup timeout. Data may not be accurate.")
            break
        
        validity = sensor.get_validity_flag()
        if validity == sensor.VALIDITY_WARMUP:
            print("Sensor warming up...")
        elif validity == sensor.VALIDITY_INITIAL_STARTUP:
            print("Sensor in initial startup...")
        
        time.sleep(1)
    
    print("Sensor ready!\n")
    
    # Optional: Set temperature and humidity compensation
    # Uncomment and adjust values if you have external temp/humidity readings
    # sensor.set_temp_rh(temperature=25.0, humidity=50.0)
    
    # Main reading loop
    print("Reading sensor data (Ctrl+C to exit)...")
    print("-" * 60)
    
    try:
        while True:
            # Wait for new data
            if sensor.is_new_data_available():
                # Read all measurements
                aqi, tvoc, eco2 = sensor.get_all_data()
                
                # Get AQI rating text
                aqi_rating = AQI.get_rating(aqi)
                
                # Display results
                print(f"AQI: {aqi} ({aqi_rating})  |  "
                      f"TVOC: {tvoc} ppb  |  "
                      f"eCO2: {eco2} ppm")
                
                # Check data validity
                if not sensor.is_data_valid():
                    print("  (Data still in warmup/startup phase)")
            
            # Wait before next reading
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\nExiting...")
    finally:
        # Clean up
        i2c_bus.close()
        print("I2C bus closed.")


if __name__ == "__main__":
    main()
