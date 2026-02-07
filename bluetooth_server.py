import asyncio
from bleak import BleakClient
from datetime import datetime


class BluetoothServer:
    """Bluetooth gateway for HM-10 modules (listener + sender, sequential)"""

    def __init__(self):
        self.LISTENER_MAC = "50:F1:4A:4D:DC:E9"
        self.CHARACTERISTIC_UUID = "0000ffe1-0000-1000-8000-00805f9b34fb"
        self.LOG_FILE = "log.txt"
        self.loop = None
        self.listening = True
        self.listener_client = None

    # -------------------------------------------------
    # LOG
    # -------------------------------------------------
    def log_event(self, event):
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.LOG_FILE, "a") as f:
            f.write(f"{ts} - {event}\n")

    # -------------------------------------------------
    # LISTENER (Arduino A → RPi)
    # -------------------------------------------------
    async def listen(self):
        while True:
            if not self.listening:
                await asyncio.sleep(0.2)
                continue

            try:
                self.listener_client = BleakClient(self.LISTENER_MAC)
                await self.listener_client.connect()
                self.log_event("LISTENER connected")

                def handle_notify(_, data):
                    msg = data.decode(errors="ignore").strip()
                    print("RX:", msg)
                    self.log_event(f"RX {msg}")

                    if "TEST1@" in msg:
                        # rozsvítit
                        self.connect_and_send_message(
                            "5C:F8:21:9E:55:84",
                            "|ON@"
                        )

                    elif "TEST2@" in msg:
                        # zhasnout
                        self.connect_and_send_message(
                            "5C:F8:21:9E:55:84",
                            "|OFF@"
                        )


                await self.listener_client.start_notify(
                    self.CHARACTERISTIC_UUID,
                    handle_notify
                )

                while self.listening:
                    await asyncio.sleep(0.2)

            except Exception as e:
                self.log_event(f"LISTENER error: {e}")
                await asyncio.sleep(1)

    async def _disconnect_listener(self):
        if self.listener_client:
            try:
                await self.listener_client.stop_notify(self.CHARACTERISTIC_UUID)
                await self.listener_client.disconnect()
                self.log_event("LISTENER disconnected")
            except Exception as e:
                self.log_event(f"LISTENER disconnect error: {e}")
            self.listener_client = None

    # -------------------------------------------------
    # SEND (RPi → Arduino B)
    # -------------------------------------------------
    def connect_and_send_message(self, mac_address, message):
        self.log_event(f"SEND request {mac_address} {message}")
        asyncio.run_coroutine_threadsafe(
            self._send(mac_address, message),
            self.loop
        )

    async def _send(self, mac_address, message):
        # zastav listener
        self.listening = False
        await self._disconnect_listener()
        await asyncio.sleep(0.5)

        try:
            async with BleakClient(mac_address) as client:
                self.log_event(f"SEND connected {mac_address}")

                # POSÍLÁME PO ZNAKU (HM-10 UART styl)
                await client.write_gatt_char(
                    self.CHARACTERISTIC_UUID,
                    message.encode(),
                )
                await asyncio.sleep(0.03)

                self.log_event("SEND done")
                await client.disconnect()

        except Exception as e:
            self.log_event(f"SEND error: {e}")

        await asyncio.sleep(0.5)
        self.listening = True

    # -------------------------------------------------
    # START
    # -------------------------------------------------
    def start(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

        self.loop.create_task(self.listen())
        self.loop.run_forever()
