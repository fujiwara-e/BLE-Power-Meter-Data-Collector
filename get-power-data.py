import asyncio
import os
from bleak import BleakScanner, BleakClient
import struct
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Cycling Power Service UUID
CYCLING_POWER_SERVICE_UUID = "00001818-0000-1000-8000-00805f9b34fb"
POWER_MEASUREMENT_UUID = "00002a63-0000-1000-8000-00805f9b34fb"

class PowerMeter:
    def __init__(self):
        self.client = None
        
    async def find_device(self):
        """Search for power meter"""
        device_name = os.getenv('DEVICE_NAME', 'PowerPro_39945')
        print(f"Searching for {device_name}...")
        devices = await BleakScanner.discover(timeout=10)
        
        for device in devices:
            if device.name == device_name:
                print(f"Found: {device.name} ({device.address})")
                return device.address
        
        print(f"{device_name} not found")
        return None
    
    def data_handler(self, sender, data):
        """Data reception handler"""
        if len(data) >= 4:
            # Get power value (bytes 2-3)
            power = struct.unpack('<H', data[2:4])[0]
            print(f"Power: {power} W")
    
    async def connect_and_collect(self, duration=30):
        """Connect and collect data"""
        device_address = await self.find_device()
        if not device_address:
            return
        
        async with BleakClient(device_address) as client:
            print("Connecting...")
            
            # Start notifications
            await client.start_notify(POWER_MEASUREMENT_UUID, self.data_handler)
            print(f"Starting {duration} seconds data collection...")
            
            # Collect data
            await asyncio.sleep(duration)
            
            # Stop notifications
            await client.stop_notify(POWER_MEASUREMENT_UUID)
            print("Collection finished")

async def main():
    meter = PowerMeter()
    await meter.connect_and_collect(duration=30)

if __name__ == "__main__":
    asyncio.run(main())
