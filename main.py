import os
from datetime import datetime
from boot_logger import log_message
from bluetooth_server import BluetoothServer
from web_server import WebServer

log_message()

if __name__ == "__main__":
    server = BluetoothServer()
    server.start()
    webserver = WebServer(server)
    webserver.start_in_thread(host="127.0.0.1", port=8000)

