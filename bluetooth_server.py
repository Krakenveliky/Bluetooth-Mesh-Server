import os
import bluetooth
from datetime import datetime
import time

# Path to the log file
LOG_FILE = "log.txt"

# Function to log events to a file
def log_event(event):
    """
    Logs events with timestamps to a log file.
    :param event: The event description to log.
    """
    with open(LOG_FILE, "a") as f:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        f.write(f"{timestamp} - {event}\n")

# Function to make the Raspberry Pi always discoverable
def make_discoverable():
    """
    Ensures the Bluetooth device (hci0) is set to discoverable and pairable mode.
    This allows other devices to find and connect to the Raspberry Pi.
    """
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
def start_bluetooth_server():
    """
    Starts a Bluetooth RFCOMM server on the Raspberry Pi.
    The server listens for incoming connections and allows communication with connected devices.
    """
    # Create a Bluetooth socket
    server_socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)

    try:
        # Ensure the Raspberry Pi is discoverable
        make_discoverable()

        # Bind the socket to any available Bluetooth adapter and port
        server_socket.bind(("", bluetooth.PORT_ANY))
        server_socket.listen(1)

        # Log that the server has started
        log_event("Bluetooth server started. Waiting for connections...")
        print("Bluetooth server started. Waiting for connections...")

        while True:
            try:
                # Make the server discoverable to clients via SDP (Service Discovery Protocol)
                bluetooth.advertise_service(
                    server_socket,
                    "rpi",  # Server name
                    service_classes=[bluetooth.SERIAL_PORT_CLASS],  # Class for serial port communication
                    profiles=[bluetooth.SERIAL_PORT_PROFILE]        # Profile for serial port communication
                )
                break
            except bluetooth.BluetoothError as e:
                log_event(f"Server error: no advertisable device, retrying in 5 seconds...")
                print("Server error: no advertisable device, retrying in 5 seconds...")
                time.sleep(5)

        while True:
            try:
                # Wait for a client to connect
                client_socket, client_info = server_socket.accept()
                log_event(f"Connected to {client_info}")
                print(f"Connected to {client_info}")

                # Handle communication with the connected client
                while True:
                    # Receive data from the client (maximum 1024 bytes)
                    data = client_socket.recv(1024).decode("utf-8")
                    if data:
                        # Log and display the received data
                        log_event(f"Received from {client_info}: {data}")
                        print(f"Received: {data}")
                        # Echo the message back to the client
                        client_socket.send(f"Echo: {data}")
            except Exception as e:
                # Log any connection errors
                log_event(f"Connection error: {e}")
                print(f"Connection error: {e}")
                # Close the client socket before accepting a new connection
                if 'client_socket' in locals():
                    client_socket.close()

    except Exception as e:
        # Log any errors related to the server
        log_event(f"Server error: {e}")
        print(f"Server error: {e}")

    finally:
        # Clean up the server socket when the program ends
        server_socket.close()
        log_event("Bluetooth server shut down.")
        print("Bluetooth server shut down.")

# Entry point of the script
if __name__ == "__main__":
    # Start the Bluetooth server
    start_bluetooth_server()
