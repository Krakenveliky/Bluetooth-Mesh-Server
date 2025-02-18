import asyncio
from bleak import BleakScanner, BleakClient
from datetime import datetime
import os

async def main():
    devices = await BleakScanner.discover()
    for d in devices:
        
        log_event(d)

    message = "Connected to Raspberry Pi!"
    await connect_and_send_message(HM10_MAC_ADDRESS, message)
    
  
    

def start():
    asyncio.run(main())


# Path to the log file
LOG_FILE = "log.txt"

# Function to log events to a file
def log_event(event):
    """
    Logs events with timestamps to a log file.
    :param event: The event description to log.
    """
    try:
        with open(LOG_FILE, "a") as f:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            f.write(f"{timestamp} - {event}\n")
    except FileNotFoundError:
        os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
        with open(LOG_FILE, "a") as f:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            f.write(f"{timestamp} - {event}\n")

HM10_MAC_ADDRESS = "50:F1:4A:4D:DC:E9"  


CHARACTERISTIC_UUID = "0000ffe1-0000-1000-8000-00805f9b34fb"

async def connect_and_send_message(mac_address, message):

    async with BleakClient(mac_address) as client:
        log_event(f"Connected: {client.is_connected}")

        if client.is_connected:
           
            await client.write_gatt_char(CHARACTERISTIC_UUID, message.encode())
            log_event(f"Message sent: {message}")

       
        log_event("Disconnecting...")

        