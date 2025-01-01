import bluetooth
import subprocess
from logger import log_device_connected

def make_discoverable():
    subprocess.run(["sudo", "hciconfig", "hci0", "piscan"])

def start_bluetooth_server():
    make_discoverable()
    
    server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    port = bluetooth.PORT_ANY
    server_sock.bind(("", port))
    server_sock.listen(1)

    port = server_sock.getsockname()[1]

    bluetooth.advertise_service(server_sock, "BluetoothServer",
                                service_classes=[bluetooth.SERIAL_PORT_CLASS],
                                profiles=[bluetooth.SERIAL_PORT_PROFILE])

    print(f"Waiting for connection on RFCOMM channel {port}")

    client_sock, client_info = server_sock.accept()
    print(f"Accepted connection from {client_info}")
    log_device_connected()

    try:
        while True:
            data = client_sock.recv(1024)
            if not data:
                break
            print(f"Received: {data}")
            client_sock.send(data)  # Echo back the received data
    except OSError:
        pass

    print("Disconnected")

    client_sock.close()
    server_sock.close()
    print("Server shut down")

if __name__ == "__main__":
    start_bluetooth_server()
