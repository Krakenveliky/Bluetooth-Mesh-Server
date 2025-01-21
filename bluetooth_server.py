import os
from bumble.device import Device, AdvertisingData, Connection
from bumble.core import ProtocolError
from boot_logger import log_message


class BluetoothServer:
    def __init__(self, device_name: str, transport: str):
        self.device_name = device_name
        self.transport = transport
        self.device = None

    async def setup_device(self):
        """
        Initialize the Bluetooth device.
        """
        log_message()
        try:
            self.device = await Device.create(transport=self.transport)
            self.device.name = self.device_name
        except Exception as e:
            log_message(f"Failed to initialize device: {e}")
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
            log_message("Started advertising")
        except Exception as e:
            log_message(f"Advertising failed: {e}")
            raise

    async def handle_connection(self, connection: Connection):
        try:
            log_message(f"Connection established with {connection.peer_address}")
            async for data in connection.read():
                log_message(f"Received: {data}")
                await connection.write(data)  # Echo back data
        except ProtocolError as e:
            log_message(f"Protocol error: {e}")
        except Exception as e:
            log_message(f"Unexpected error: {e}")
        finally:
            log_message(f"Connection with {connection.peer_address} closed")

    async def run(self):
        """
        Run the Bluetooth server.
        """
        await self.setup_device()
        await self.start_advertising()

        try:
            log_message("Waiting for connections...")
            async for connection in self.device.accept_connections():
                await self.handle_connection(connection)
        except Exception as e:
            log_message(f"Server error: {e}")
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
        log_message("Server stopped by user")
    except Exception as e:
        log_message(f"Unhandled exception: {e}")