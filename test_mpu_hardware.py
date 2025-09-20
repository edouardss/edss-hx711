#!/usr/bin/env python3
"""
Test script to verify MPU6050 hardware connection and functionality
"""

import sys
import time

def test_mpu_hardware():
    print("Testing MPU6050 hardware connection...")
    
    try:
        # Test imports
        print("1. Testing imports...")
        import board
        import busio
        import adafruit_mpu6050
        print("   ✅ All imports successful")
        
        # Test I2C bus initialization
        print("2. Testing I2C bus initialization...")
        i2c = busio.I2C(board.SCL, board.SDA)
        print("   ✅ I2C bus created")
        
        # Test sensor initialization
        print("3. Testing MPU6050 sensor initialization...")
        sensor = adafruit_mpu6050.MPU6050(i2c)
        print("   ✅ MPU6050 sensor initialized")
        
        # Test sensor configuration
        print("4. Testing sensor configuration...")
        sensor.accelerometer_range = adafruit_mpu6050.Range.RANGE_4_G
        sensor.gyro_range = adafruit_mpu6050.GyroRange.RANGE_500_DPS
        print("   ✅ Sensor configured")
        
        # Test reading sensor data
        print("5. Testing sensor data reading...")
        for i in range(3):
            try:
                acceleration = sensor.acceleration
                gyro = sensor.gyro
                temperature = sensor.temperature
                
                print(f"   Reading {i+1}:")
                print(f"     Acceleration: X={acceleration[0]:.2f}, Y={acceleration[1]:.2f}, Z={acceleration[2]:.2f} m/s²")
                print(f"     Gyroscope: X={gyro[0]:.2f}, Y={gyro[1]:.2f}, Z={gyro[2]:.2f} rad/s")
                print(f"     Temperature: {temperature:.2f}°C")
                
                time.sleep(0.5)
            except Exception as e:
                print(f"   ❌ Error reading sensor data: {e}")
                return False
        
        print("   ✅ Sensor data reading successful")
        
        # Test I2C scan to see what devices are available
        print("6. Scanning I2C bus for devices...")
        try:
            while not i2c.try_lock():
                pass
            devices = i2c.scan()
            i2c.unlock()
            print(f"   Found I2C devices at addresses: {[hex(addr) for addr in devices]}")
            if 0x68 in devices or 0x69 in devices:
                print("   ✅ MPU6050 detected on I2C bus")
            else:
                print("   ⚠️  MPU6050 not detected on I2C bus (addresses 0x68 or 0x69)")
        except Exception as e:
            print(f"   ❌ Error scanning I2C bus: {e}")
        
        print("\n🎉 MPU6050 hardware test completed successfully!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   Make sure you have installed: pip install adafruit-circuitpython-mpu6050")
        return False
    except Exception as e:
        print(f"❌ Hardware error: {e}")
        print("   Check I2C connections and permissions")
        return False

if __name__ == "__main__":
    success = test_mpu_hardware()
    sys.exit(0 if success else 1)
