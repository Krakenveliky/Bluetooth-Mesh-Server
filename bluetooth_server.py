import asyncio
from bleak import BleakScanner, BleakClient
from datetime import datetime
import os

class BluetoothServer:
    """A class to handle Bluetooth LE server operations"""
    
    def __init__(self):
        self.HM10_MAC_ADDRESS = "50:F1:4A:4D:DC:E9"
        self.CHARACTERISTIC_UUID = "0000ffe1-0000-1000-8000-00805f9b34fb"
        self.LOG_FILE = "log.txt"

    async def main(self):
        """Main entry point for Bluetooth operations"""
        # Uncomment to scan for devices
        devices = await BleakScanner.discover()
        for d in devices:
            self.log_event(d)

        message = "Connected@"
        await self.connect_and_send_message(self.HM10_MAC_ADDRESS, message)

    def start(self):
        """Start the Bluetooth server"""
        asyncio.run(self.main())

    def log_event(self, event):
        """
        Logs events with timestamps to a log file.
        :param event: The event description to log.
        """
        try:
            with open(self.LOG_FILE, "a") as f:
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                f.write(f"{timestamp} - {event}\n")
        except FileNotFoundError:
            os.makedirs(os.path.dirname(self.LOG_FILE), exist_ok=True)
            with open(self.LOG_FILE, "a") as f:
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                f.write(f"{timestamp} - {event}\n")

    

    async def listen(self):
        async with BleakClient(self.HM10_MAC_ADDRESS) as client:
            self.log_event("BLE listener connected")

            def handle_notify(_, data: bytearray):
                message = data.decode(errors="ignore").strip()
                print("RX:", message)
                self.log_event(f"RX {message}")

            await client.start_notify(self.CHARACTERISTIC_UUID, handle_notify)

            while True:
                await asyncio.sleep(1)

    async def connect_and_send_message(self, mac_address, message):
        """
        Connect to a Bluetooth device and send a message
        :param mac_address: The MAC address of the target device
        :param message: The message to send
        """
        async with BleakClient(mac_address) as client:
            self.log_event(f"Connected: {client.is_connected}")

            if client.is_connected:
                await client.write_gatt_char(self.CHARACTERISTIC_UUID, message.encode(), response=False)
                self.log_event(f"Message sent: {message}")

            self.log_event("Disconnecting...")
            
    def start(self):
        asyncio.run(self.main())

# Example usage
