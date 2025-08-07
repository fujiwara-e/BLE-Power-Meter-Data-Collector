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
        device_name = os.getenv('DEVICE_NAME')
        print(f"Searching for {device_name}...")
        devices = await BleakScanner.discover(timeout=10)
        
        for device in devices:
            if device.name == device_name:
                print(f"Found: {device.name} ({device.address})")
                return device.address
        
        print(f"{device_name} not found")
        return None
    
    def _parse_power_data(self, data):
        """Parse power data"""
        if len(data) < 4:
            return None, None
        
        flags = struct.unpack('<H', data[0:2])[0]
        power = struct.unpack('<H', data[2:4])[0]
        return flags, power
    
    def _parse_cadence_data(self, data, flags):
        """Parse cadence data"""
        # Return None if cadence data is not present
        if not (flags & 0x02) or len(data) < 10:
            return None
        
        crank_revolutions = struct.unpack('<H', data[4:6])[0]
        last_crank_event_time = struct.unpack('<H', data[6:8])[0]
        
        return self._calculate_cadence(crank_revolutions, last_crank_event_time)
    
    def _calculate_cadence(self, crank_revolutions, last_crank_event_time):
        """Calculate cadence"""
        # Return None if no previous data
        if not hasattr(self, 'prev_crank_revolutions') or not hasattr(self, 'prev_crank_time'):
            self.prev_crank_revolutions = crank_revolutions
            self.prev_crank_time = last_crank_event_time
            return None
        
        rev_diff = crank_revolutions - self.prev_crank_revolutions
        time_diff = last_crank_event_time - self.prev_crank_time
        
        # Handle time rollover (16-bit counter)
        if time_diff < 0:
            time_diff += 65536
        
        self.prev_crank_revolutions = crank_revolutions
        self.prev_crank_time = last_crank_event_time
        
        if time_diff <= 0:
            return None
        
        # Time is in 1/1024 seconds, convert to RPM
        return (rev_diff * 60 * 1024) / time_diff
    
    def data_handler(self, sender, data):
        """Data reception handler"""
        flags, power = self._parse_power_data(data)
        if power is None:
            return
        
        cadence = self._parse_cadence_data(data, flags)
        
        # Display data
        if cadence is not None:
            print(f"Power: {power} W, Cadence: {cadence:.1f} RPM")
        else:
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
