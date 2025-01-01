import os
from datetime import datetime
from boot_logger import log_message
from bluetooth_server import start_bluetooth_server

log_message()

if __name__ == "__main__":
    start_bluetooth_server()