# BLE Power Meter Data Collector

Python script for collecting power data from Bluetooth Low Energy (BLE) cycling power meters using standard Cycling Power Service.

## Requirements

- Python 3.7+
- BLE-compatible cycling power meter

## Tested Devices

- Python 3.12.8
- macOS 15.5
- GIANT Power Pro (PowerPro_<id>)

## Installation

1. Create a virtual environment:
   ```bash
   python3 -m venv myenv
   source myenv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install bleak python-dotenv
   ```
3. Configure device name:
   ```bash
   # Copy .env.example to .env and edit device name
   cp .env.example .env
   # Edit DEVICE_NAME in .env file
   ```

## Usage

1. Power on your BLE power meter device
2. Run the script:
   ```bash
   python get-power-data.py
   ```

The script will automatically discover the device, connect, and display real-time power values for 30 seconds.