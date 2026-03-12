import asyncio
from bleak import BleakClient
from datetime import datetime


class BluetoothServer:

    def __init__(self):

        self.SENDER_MAC = "5C:F8:21:9E:55:84"
        self.CHAR_UUID = "0000ffe1-0000-1000-8000-00805f9b34fb"

        self.sender_client = None
        self.loop = None
        self.ble_lock = asyncio.Lock()

        self.LOG_FILE = "log.txt"

    def log_event(self, msg):
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.LOG_FILE, "a") as f:
            f.write(f"{ts} - {msg}\n")

    async def connect_sender(self):

        while True:
            try:

                self.sender_client = BleakClient(self.SENDER_MAC)
                await self.sender_client.connect()

                self.log_event("BLE connected")

                return

            except Exception as e:

                self.log_event(f"BLE connect error {e}")
                await asyncio.sleep(2)

    async def safe_write(self, message):

        async with self.ble_lock:

            if not self.sender_client or not self.sender_client.is_connected:
                await self.connect_sender()

            await self.sender_client.write_gatt_char(
                self.CHAR_UUID,
                message.encode(),
                response=False
            )

            self.log_event(f"SEND {message}")

    def send(self, message):

        asyncio.run_coroutine_threadsafe(
            self.safe_write(message),
            self.loop
        )

    def start(self):

        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

        self.loop.create_task(self.connect_sender())

        self.loop.run_forever()