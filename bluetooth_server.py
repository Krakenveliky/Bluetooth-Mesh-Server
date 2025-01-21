import os
from datetime import datetime
from bumble.device import Device, AdvertisingData, Connection
from bumble.core import ProtocolError
from bumble.transport import open_transport_or_link
from bumble.sdp import (
    DataElement,
    ServiceAttribute,
    SDP_PUBLIC_BROWSE_ROOT,
    SDP_BROWSE_GROUP_LIST_ATTRIBUTE_ID,
    SDP_SERVICE_RECORD_HANDLE_ATTRIBUTE_ID,
    SDP_SERVICE_CLASS_ID_LIST_ATTRIBUTE_ID,
    SDP_PROTOCOL_DESCRIPTOR_LIST_ATTRIBUTE_ID,
    SDP_BLUETOOTH_PROFILE_DESCRIPTOR_LIST_ATTRIBUTE_ID,
)
from bumble.core import (
    BT_AUDIO_SINK_SERVICE,
    BT_L2CAP_PROTOCOL_ID,
    BT_AVDTP_PROTOCOL_ID,
    BT_ADVANCED_AUDIO_DISTRIBUTION_SERVICE,
)

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

SDP_SERVICE_RECORDS = {
    0x10001: [
        ServiceAttribute(
            0x00000001,  # Service Record Handle
            DataElement.unsigned_integer_32(0x10001),
        ),
        ServiceAttribute(
            0x00000004,  # Protocol Descriptor List
            DataElement.sequence(
                [
                    DataElement.sequence(
                        [
                            DataElement.uuid(BT_L2CAP_PROTOCOL_ID),
                            DataElement.unsigned_integer_16(25),
                        ]
                    )
                ]
            ),
        ),
    ]
}

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
            
           
            async with await open_transport_or_link("serial:/dev/ttyAMA10")as hci_transport:
                log_event('<<< Transport opened')

                # Create a device from the config file
                log_event('<<< Creating Bluetooth device')
                device = Device.from_config_file_with_hci(
                    "config.json", hci_transport.source, hci_transport.sink
                )
                device.classic_enabled = True
                device.sdp_service_records = SDP_SERVICE_RECORDS
                #log_event('<<< Powering on device')
                #await device.power_on()

                #Set the device to be discoverable and connectable
                log_event('<<< Setting device to discoverable and connectable')
                #await device.set_discoverable(True)
                #await device.set_connectable(True)

                # Set up advertising data and start advertising
                log_event('<<< Starting advertising')
                await device.start_advertising()
                
               

                log_event('<<< Device is now advertising')
                @device.on('connection')
                async def on_connection(connection):
                            log_event(f'<<< Connected to {connection.peer_address}')

                            # Handle incoming data
                            @connection.on('data')
                            async def on_data(data):
                                log_event(f'<<< Received data: {data}')

                            # Wait until the connection is terminated
                            await connection.disconnected()
                            log_event(f'<<< Disconnected from {connection.peer_address}')
                await hci_transport.source.wait_for_termination()
        except Exception as e:
            log_event(f"Failed to initialize device: {e}")
            raise

   

    

    async def run(self):
        """
        Run the Bluetooth server.
        """
        await self.setup_device()     

       
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