import asyncio
from bleak import BleakClient
from datetime import datetime

class BluetoothServer:
    def __init__(self):
        # Arduino A – POSÍLÁ (kabely)
        self.SENDER_MAC = "50:F1:4A:4D:DC:E9"

        # HM-10 UART UUID (stejný pro všechna zařízení)
        self.CHAR_UUID = "0000ffe1-0000-1000-8000-00805f9b34fb"

        self.LOG_FILE = "log.txt"

        self.listening = True
        self.loop = None

    # --------------------------------------------------
    # LOG
    # --------------------------------------------------
    def log_event(self, msg):
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.LOG_FILE, "a") as f:
            f.write(f"{ts} - {msg}\n")

    # --------------------------------------------------
    # LISTENER – Arduino A -> LOG
    # --------------------------------------------------
    async def listen(self):
        while True:
            try:
                if not self.listening:
                    await asyncio.sleep(0.2)
                    continue

                client = BleakClient(self.SENDER_MAC)
                await client.connect()
                self.log_event("LISTENER CONNECTED (Arduino A)")
                print("Listening Arduino A")

                def handle(_, data: bytearray):
                    msg = data.decode(errors="ignore").strip()
                    print("RX:", msg)
                    self.log_event(f"RX {msg}")

                await client.start_notify(self.CHAR_UUID, handle)

                while self.listening:
                    await asyncio.sleep(0.2)

                await client.stop_notify(self.CHAR_UUID)
                await client.disconnect()
                self.log_event("LISTENER DISCONNECTED")

            except Exception as e:
                self.log_event(f"LISTENER ERROR: {e}")
                print("Listener error, retrying...")
                await asyncio.sleep(1)

    # --------------------------------------------------
    # SEND – Arduino B <- MOBIL
    # --------------------------------------------------
    async def connect_and_send_message(self, mac_address, message):
        try:
            # stop listener
            self.listening = False
            await asyncio.sleep(0.5)

            async with BleakClient(mac_address) as client:
                await client.connect()
                self.log_event(f"SEND CONNECTED {mac_address}")

                await client.write_gatt_char(
                    self.CHAR_UUID,
                    message.encode(),
                    response=False
                )

                self.log_event(f"SENT {message} TO {mac_address}")
                await client.disconnect()

        except Exception as e:
            self.log_event(f"SEND ERROR: {e}")

        finally:
            # resume listener
            await asyncio.sleep(0.5)
            self.listening = True

    # --------------------------------------------------
    # START
    # --------------------------------------------------
    def start(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.create_task(self.listen())
        self.loop.run_forever()
