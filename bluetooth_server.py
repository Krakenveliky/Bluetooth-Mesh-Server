import asyncio
from bleak import BleakClient
from datetime import datetime


class BluetoothServer:

    def __init__(self):
        self.LISTENER_MAC = "50:F1:4A:4D:DC:E9"
        self.SENDER_MAC   = "5C:F8:21:9E:55:84"

        self.CHAR_UUID = "0000ffe1-0000-1000-8000-00805f9b34fb"
        self.LOG_FILE = "log.txt"

        self.loop = None
        self.listener_client = None
        self.sender_client = None

        self.ble_lock = asyncio.Lock()

    # ---------------- LOG ----------------

    def log_event(self, msg):
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.LOG_FILE, "a") as f:
            f.write(f"{ts} - {msg}\n")

    # ---------------- LISTENER ----------------

    async def listen(self):
        while True:
            try:
                self.listener_client = BleakClient(self.LISTENER_MAC)
                await self.listener_client.connect()
                self.log_event("LISTENER connected")

                def on_notify(_, data):
                    msg = data.decode(errors="ignore").strip()
                    self.log_event(f"RX {msg}")

                    if msg in ("O@", "F@"):
                        self.handle_power(msg)

                    elif msg in ("R@","G@","B@","Y@","P@","C@"):
                        self.handle_color(msg)

                await self.listener_client.start_notify(
                    self.CHAR_UUID,
                    on_notify
                )

                while True:
                    await asyncio.sleep(1)

            except Exception as e:
                self.log_event(f"LISTENER error {e}")
                await asyncio.sleep(1)

    # ---------------- HANDLERS ----------------

    def handle_power(self, msg):
        self.send(f"|{msg}")

    def handle_color(self, msg):
        self.send(f"|{msg}")

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

        async def safe_write():
            try:
                async with self.ble_lock:
                    if not self.sender_client or not self.sender_client.is_connected:
                        await self.connect_sender()

                    await self.sender_client.write_gatt_char(
                        self.CHAR_UUID,
                        message.encode(),
                        response=False
                    )

                    self.log_event(f"SEND {message}")

            except Exception as e:
                self.log_event(f"SEND error {e}")

        asyncio.run_coroutine_threadsafe(safe_write(), self.loop)

    # ---------------- START ----------------

    def start(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

        self.loop.create_task(self.listen())
        self.loop.create_task(self.connect_sender())

        self.loop.run_forever()