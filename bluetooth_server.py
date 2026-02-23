import asyncio
from bleak import BleakClient
from datetime import datetime


class BluetoothServer:
    """Realtime BLE gateway – no reconnect lag"""

    def __init__(self):
        self.LISTENER_MAC = "50:F1:4A:4D:DC:E9"
        self.SENDER_MAC   = "5C:F8:21:9E:55:84"

        self.CHARACTERISTIC_UUID = "0000ffe1-0000-1000-8000-00805f9b34fb"
        self.LOG_FILE = "log.txt"

        self.loop = None
        self.listener_client = None
        self.sender_client = None

    # ---------------- LOG ----------------

    def log_event(self, event):
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.LOG_FILE, "a") as f:
            f.write(f"{ts} - {event}\n")

    # ---------------- LISTENER ----------------

    async def listen(self):
        while True:
            try:
                self.listener_client = BleakClient(self.LISTENER_MAC)
                await self.listener_client.connect()
                self.log_event("LISTENER connected")

                def handle_notify(_, data):
                    msg = data.decode(errors="ignore").strip()
                    self.log_event(f"RX {msg}")

                    if "ON@" in msg:
                        self.send("|ON@")

                    elif "OFF@" in msg:
                        self.send("|OFF@")

                await self.listener_client.start_notify(
                    self.CHARACTERISTIC_UUID,
                    handle_notify
                )

                while True:
                    await asyncio.sleep(1)

            except Exception as e:
                self.log_event(f"LISTENER error {e}")
                await asyncio.sleep(1)

    # ---------------- SENDER ----------------

    async def connect_sender(self):
        while True:
            try:
                self.sender_client = BleakClient(self.SENDER_MAC)
                await self.sender_client.connect()
                self.log_event("SENDER connected")
                return
            except Exception as e:
                self.log_event(f"SENDER connect error {e}")
                await asyncio.sleep(1)

    def send(self, message):
        if not self.sender_client:
            return

        asyncio.run_coroutine_threadsafe(
            self.sender_client.write_gatt_char(
                self.CHARACTERISTIC_UUID,
                message.encode(),
                response=False
            ),
            self.loop
        )

    # ---------------- START ----------------

    def start(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

        self.loop.create_task(self.listen())
        self.loop.create_task(self.connect_sender())

        self.loop.run_forever()