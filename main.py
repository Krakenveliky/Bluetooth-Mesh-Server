import os
from datetime import datetime
from logger import log_message, log_rpi_start
from bluetooth_server import start_bluetooth_server

log_rpi_start()
start_bluetooth_server()