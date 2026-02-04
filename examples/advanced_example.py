#!/usr/bin/env python3
"""
Advanced example for using the ENS160 sensor library.

This example demonstrates:
1. Temperature and humidity compensation
2. Power management modes
3. Error handling
4. Data logging
"""

import time
import sys
from smbus2 import SMBus
from ens160 import ENS160, AQI


def print_separator():
    """Print a separator line."""
    print("-" * 70)


def main():
    """Main example function."""
    print("ENS160 Advanced Example")
    print_separator()
    
    # Initialize I2C bus
    try:
        i2c_bus = SMBus(1)
    except Exception as e:
        print(f"Error: Could not open I2C bus: {e}")
        print("Make sure I2C is enabled on your system.")
        sys.exit(1)
    
    # Try both I2C addresses
    sensor = None
    for address in [ENS160.I2C_ADDRESS_DEFAULT, ENS160.I2C_ADDRESS_ALT]:
        print(f"Trying I2C address 0x{address:02X}...")
        test_sensor = ENS160(i2c_bus, address)
        if test_sensor.begin():
            sensor = test_sensor
            print(f"✓ Found ENS160 at address 0x{address:02X}")
            break
        else:
            print(f"✗ No sensor at address 0x{address:02X}")
    
    if sensor is None:
        print("\nError: ENS160 sensor not found!")
        print("Please check connections and I2C configuration.")
        i2c_bus.close()
        sys.exit(1)
    
    print_separator()
    
    # Get and display firmware version
    try:
        major, minor, release = sensor.get_firmware_version()
        print(f"Firmware Version: {major}.{minor}.{release}")
    except Exception as e:
        print(f"Warning: Could not read firmware version: {e}")
    
    print_separator()
    
    # Set temperature and humidity compensation
    # Replace these with actual values from an external sensor if available
    ambient_temp = 25.0  # °C
    ambient_humidity = 50.0  # %
    
    print(f"Setting compensation: Temp={ambient_temp}°C, RH={ambient_humidity}%")
    try:
        sensor.set_temp_rh(ambient_temp, ambient_humidity)
        print("✓ Compensation values set")
    except Exception as e:
        print(f"✗ Could not set compensation: {e}")
    
    print_separator()
    
    # Wait for sensor warmup
    print("Waiting for sensor warmup and stabilization...")
    warmup_start = time.time()
    
    while not sensor.is_data_valid():
        validity = sensor.get_validity_flag()
        
        if validity == sensor.VALIDITY_WARMUP:
            status = "Warming up..."
        elif validity == sensor.VALIDITY_INITIAL_STARTUP:
            status = "Initial startup..."
        else:
            status = "Unknown state"
        
        elapsed = int(time.time() - warmup_start)
        print(f"  [{elapsed}s] {status}", end='\r')
        
        time.sleep(0.5)
        
        # Timeout after 60 seconds
        if elapsed > 60:
            print("\nWarning: Warmup timeout. Continuing anyway...")
            break
    
    print("\n✓ Sensor ready!                    ")
    print_separator()
    
    # Main measurement loop
    print("Starting continuous measurements...")
    print("(Press Ctrl+C to exit)\n")
    
    print(f"{'Time':>8} | {'AQI':>3} | {'Rating':>10} | {'TVOC':>6} | {'eCO2':>6} | {'Valid':>5}")
    print_separator()
    
    measurement_count = 0
    start_time = time.time()
    
    try:
        while True:
            # Check for new data
            if sensor.is_new_data_available():
                # Read all measurements
                aqi, tvoc, eco2 = sensor.get_all_data()
                
                # Get validity status
                is_valid = sensor.is_data_valid()
                valid_str = "Yes" if is_valid else "No"
                
                # Get AQI rating
                rating = AQI.get_rating(aqi)
                
                # Calculate elapsed time
                elapsed = int(time.time() - start_time)
                minutes = elapsed // 60
                seconds = elapsed % 60
                time_str = f"{minutes:02d}:{seconds:02d}"
                
                # Display measurement
                print(f"{time_str:>8} | {aqi:>3} | {rating:>10} | {tvoc:>4} ppb | {eco2:>4} ppm | {valid_str:>5}")
                
                measurement_count += 1
                
                # Example: Put sensor to sleep after 10 measurements (for demo)
                # Uncomment to test power management
                # if measurement_count == 10:
                #     print("\nEntering deep sleep mode for 5 seconds...")
                #     sensor.set_mode(ENS160.MODE_DEEP_SLEEP)
                #     time.sleep(5)
                #     print("Waking up...")
                #     sensor.set_mode(ENS160.MODE_STANDARD)
                #     time.sleep(2)
            
            # Delay between checks
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n")
        print_separator()
        print("Measurement stopped by user")
    except Exception as e:
        print(f"\nError during measurement: {e}")
    finally:
        # Summary
        print_separator()
        print(f"Total measurements: {measurement_count}")
        
        # Put sensor in idle mode to save power
        try:
            sensor.set_mode(ENS160.MODE_IDLE)
            print("Sensor set to idle mode")
        except:
            pass
        
        # Close I2C bus
        i2c_bus.close()
        print("I2C bus closed")
        print("Goodbye!")


if __name__ == "__main__":
    main()
