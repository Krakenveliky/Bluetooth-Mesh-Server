import os
from datetime import datetime
from boot_logger import log_message
from bluetooth_server import start

log_message()

if __name__ == "__main__":
    start()