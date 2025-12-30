import asyncio
from bleak import BleakScanner, BleakClient
from datetime import datetime
import os


class BluetoothServer:
    """A class to handle Bluetooth LE server operations"""
    
    def __init__(self):
        self.HM10_MAC_ADDRESS = ["50:F1:4A:4D:DC:E9", "5C:F8:21:9E:55:84"]
        self.CHARACTERISTIC_UUID = "0000ffe1-0000-1000-8000-00805f9b34fb"
        self.LOG_FILE = "log.txt"
        self.loop = None
        self.listening = True




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

    

    async def listen(self, MAC):
        while True:
            if not self.listening:
                await asyncio.sleep(0.2)
                continue

            


    def connect_and_send_message(self, mac_address, message):
        asyncio.run_coroutine_threadsafe(
            self._connect_and_send(mac_address, message),
            self.loop
        )

    async def _connect_and_send(self, mac_address, message):
        self.listening = False
        await asyncio.sleep(0.5)

        async with BleakClient(mac_address) as client:
            await client.connect()
            await client.write_gatt_char(
                self.CHARACTERISTIC_UUID,
                message.encode(),
                response=False
            )
            await client.disconnect()

        await asyncio.sleep(0.5)
        self.listening = True


            
    def start(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.create_task(self.listen("50:F1:4A:4D:DC:E9"))
        self.loop.run_forever()


# Example usage