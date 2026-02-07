import asyncio
from bleak import BleakClient
from datetime import datetime

LISTENER_MAC = "50:F1:4A:4D:DC:E9"
SENDER_MAC = "5C:F8:21:9E:55:84"
CHAR_UUID = "0000ffe1-0000-1000-8000-00805f9b34fb"


class BluetoothServer:

    def log(self, msg):
        ts = datetime.now().strftime("%H:%M:%S")
        print(ts, msg)

    async def start(self):
        self.listener = BleakClient(LISTENER_MAC)
        self.sender = BleakClient(SENDER_MAC)

        print("Connecting listener...")
        await self.listener.connect()
        await self.listener.get_services()

        print("Connecting sender...")
        await self.sender.connect()
        await self.sender.get_services()

        print("BLE ready")

        def on_rx(_, data):
            msg = data.decode(errors="ignore").strip()
            self.log(f"RX {msg}")

            if "TEST1@" in msg:
                asyncio.create_task(self.send("|ON@"))
            elif "TEST2@" in msg:
                asyncio.create_task(self.send("|OFF@"))

        await self.listener.start_notify(CHAR_UUID, on_rx)

        while True:
            await asyncio.sleep(1)

    async def send(self, message):
        await self.sender.write_gatt_char(
            CHAR_UUID,
            message.encode()
        )
        self.log(f"SEND {message}")


if __name__ == "__main__":
    asyncio.run(BluetoothServer().start())
