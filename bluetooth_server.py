import asyncio
from bleak import BleakClient
from datetime import datetime
import os

class BluetoothServer:
    """Bluetooth LE server with SEQUENTIAL BLE switching (HM-10 safe)"""

    def __init__(self):
        # Arduino A – POSÍLÁ (kabely → log)
        self.HM10_MAC_ADDRESS = "50:F1:4A:4D:DC:E9"

        # UART charakteristika HM-10 (STEJNÁ PRO VŠECHNA)
        self.CHARACTERISTIC_UUID = "0000ffe1-0000-1000-8000-00805f9b34fb"

        self.LOG_FILE = "log.txt"

        # stav listeneru
        self.listening = True
        self.listener_client = None
        self.loop = None

    # --------------------------------------------------
    # LOG
    # --------------------------------------------------
    def log_event(self, event):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open(self.LOG_FILE, "a") as f:
            f.write(f"{timestamp} - {event}\n")

    # --------------------------------------------------
    # LISTEN – Arduino A → LOG
    # --------------------------------------------------
    async def listen(self):
        self.listening = True
        self.listener_client = BleakClient(self.HM10_MAC_ADDRESS)

        await self.listener_client.connect()
        self.log_event("BLE listener connected (Arduino A)")
        print("Listening Arduino A")

        def handle_notify(_, data: bytearray):
            msg = data.decode(errors="ignore").strip()
            print("RX:", msg)
            self.log_event(f"RX {msg}")

        await self.listener_client.start_notify(
            self.CHARACTERISTIC_UUID,
            handle_notify
        )

        while self.listening:
            await asyncio.sleep(0.2)

        await self.listener_client.disconnect()
        self.log_event("BLE listener disconnected")

    # --------------------------------------------------
    # SEND – Arduino B ← MOBIL
    # --------------------------------------------------
    async def connect_and_send_message(self, mac_address, message):

        # 1️⃣ zastav listener
        if self.listening:
            self.listening = False
            await asyncio.sleep(0.5)

        # 2️⃣ pošli příkaz Arduino B
        async with BleakClient(mac_address) as client:
            await client.connect()
            self.log_event(f"Connected to {mac_address}")

            await client.write_gatt_char(
                self.CHARACTERISTIC_UUID,
                message.encode(),
                response=False
            )

            self.log_event(f"Message sent: {message}")
            await client.disconnect()

        # 3️⃣ vrať se zpět k poslouchání Arduino A
        await asyncio.sleep(0.5)
        self.loop.create_task(self.listen())

    # --------------------------------------------------
    # START
    # --------------------------------------------------
    def start(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.create_task(self.listen())
        self.loop.run_forever()
