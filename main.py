import threading
from bluetooth_server import BluetoothServer
from web_server import WebServer


if __name__ == "__main__":

    ble_server = BluetoothServer()

    ble_thread = threading.Thread(
        target=ble_server.start,
        daemon=True
    )

    ble_thread.start()

    web = WebServer(ble_server)
    web.start_in_thread()