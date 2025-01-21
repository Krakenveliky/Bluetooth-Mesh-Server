import os
from datetime import datetime
from bumble.device import Device, AdvertisingData, Connection
from bumble.core import ProtocolError
from bumble.transport import open_transport_or_link

LOG_FILE = "log.txt"

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


class BluetoothServer:
    def __init__(self, device_name: str, transport: str):
        self.device_name = device_name
        self.transport = transport
        self.device = None

    async def setup_device(self):
        """
        Initialize the Bluetooth device.
        """
        try:
            # Open transport
            host, controller_source, controller_sink = open_transport_or_link(self.transport)

            # Create Device without the non-existent 'transport' parameter
            self.device = Device(
                host=host,
                controller_source=controller_source,
                controller_sink=controller_sink
            )
            self.device.name = self.device_name
        except Exception as e:
            log_event(f"Failed to initialize device: {e}")
            raise

    async def start_advertising(self):
        """
        Start advertising the Bluetooth service.
        """
        try:
            advertisement = AdvertisingData(
                local_name=self.device_name,
                flags=AdvertisingData.Flag.BR_EDR_NOT_SUPPORTED
            )
            await self.device.advertise(advertisement)
            log_event("Started advertising")
        except Exception as e:
            log_event(f"Advertising failed: {e}")
            raise

    async def handle_connection(self, connection: Connection):
        try:
            log_event(f"Connection established with {connection.peer_address}")
            async for data in connection.read():
                log_event(f"Received: {data}")
                await connection.write(data)  # Echo back data
        except ProtocolError as e:
            log_event(f"Protocol error: {e}")
        except Exception as e:
            log_event(f"Unexpected error: {e}")
        finally:
            log_event(f"Connection with {connection.peer_address} closed")

    async def run(self):
        """
        Run the Bluetooth server.
        """
        await self.setup_device()
        await self.start_advertising()

        try:
            log_event("Waiting for connections...")
            async for connection in self.device.accept_connections():
                await self.handle_connection(connection)
        except Exception as e:
            log_event(f"Server error: {e}")
        finally:
            if self.device:
                await self.device.stop()


def start():
    """
    Entry point for the Bluetooth server.
    """
    from asyncio import run

    DEVICE_NAME = "Bluetooth Server"
    TRANSPORT = "bluez" 

    server = BluetoothServer(DEVICE_NAME, TRANSPORT)
    try:
        run(server.run())
    except KeyboardInterrupt:
        log_event("Server stopped by user")
    except Exception as e:
        log_event(f"Unhandled exception: {e}")