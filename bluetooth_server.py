import sys
import logging
import asyncio
import threading
import os
from datetime import datetime

from typing import Any, Union

from bless import (  # type: ignore
    BlessServer,
    BlessGATTCharacteristic,
    GATTCharacteristicProperties,
    GATTAttributePermissions,
)

# Path to the log file
LOG_FILE = "log.txt"

# Function to log events to a file
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

# Function to make the Raspberry Pi always discoverable
def make_discoverable():
    try:
        # Enable discoverable and pairable mode using hciconfig
        os.system("sudo hciconfig hci0 piscan")
        log_event("Bluetooth set to discoverable mode.")
        print("Bluetooth is discoverable.")
        
        # Verify if the device is discoverable
        result = os.popen("sudo hciconfig hci0").read()
        log_event(f"hciconfig output: {result}")
        print(f"hciconfig output: {result}")
        if "UP RUNNING PSCAN" in result:
            log_event("Bluetooth device is discoverable.")
            print("Bluetooth device is discoverable.")
        else:
            raise Exception("Bluetooth device is not discoverable.")
    except Exception as e:
        # Log any errors if the command fails
        log_event(f"Failed to set Bluetooth to discoverable: {e}")
        print(f"Error setting discoverable: {e}")

# Function to start the Bluetooth server
trigger: Union[asyncio.Event, threading.Event]
if sys.platform in ["darwin", "win32"]:
    trigger = threading.Event()
else:
    trigger = asyncio.Event()


restart_trigger: Union[asyncio.Event, threading.Event]
if sys.platform in ["darwin", "win32"]:
    restart_trigger = threading.Event()
else:
    restart_trigger = asyncio.Event()

def read_request(characteristic: BlessGATTCharacteristic, **kwargs) -> bytearray:
    log_event(f"Reading {characteristic.value}")
    # If the value is "shutdown", set restart trigger
    if characteristic.value == b'shutdown\r\n':
        log_event("Shutdown command received")
        restart_trigger.set()
    return characteristic.value


def write_request(characteristic: BlessGATTCharacteristic, value: Any, **kwargs):
    characteristic.value = value
    log_event(f"Char value is set to {characteristic.value}")
    if characteristic.value == b"\x0f":
        log_event("NICE")
        trigger.set()


async def run(loop):
    try:    
        trigger.clear()
        # Instantiate the server
        my_service_name = "Test Service"
        server = BlessServer(name=my_service_name, loop=loop)
        server.read_request_func = read_request
        server.write_request_func = write_request

        # Add Service
        my_service_uuid = "A07498CA-AD5B-474E-940D-16F1FBE7E8CD"
        await server.add_new_service(my_service_uuid)

        # Add a Characteristic to the service
        my_char_uuid = "51FF12BB-3ED8-46E5-B4F9-D64E2FEC021B"
        char_flags = (
            GATTCharacteristicProperties.read
            | GATTCharacteristicProperties.write
            | GATTCharacteristicProperties.indicate
        )
        permissions = GATTAttributePermissions.readable | GATTAttributePermissions.writeable
        await server.add_new_characteristic(
            my_service_uuid, my_char_uuid, char_flags, None, permissions
        )

        log_event(server.get_characteristic(my_char_uuid))
        await server.start()
        log_event("Advertising")
        
        # Keep server running until explicitly stopped
        while True:
            try:
                if restart_trigger.is_set():
                    log_event("Disconnecting server...")
                    await server.stop()
                    log_event("Restarting server...")
                    await server.start()
                    log_event("Advertising")
                    restart_trigger.clear()

                if trigger.is_set():
                    log_event("Trigger received, updating characteristic")
                    server.get_characteristic(my_char_uuid)
                    server.update_value(my_service_uuid, my_char_uuid)
                    trigger.clear()
                await asyncio.sleep(1)  # Small sleep to prevent CPU overload
            except asyncio.CancelledError:
                break
            
        await server.stop()
    except Exception as e:
        log_event(f"Error: {e}")
        print(f"Error: {e}")

def start():
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(run(loop))
    except KeyboardInterrupt:
        log_event("Server stopped by user")

