import os
from datetime import datetime

def log_rpi_start():
    with open("log.txt", "a") as f:  
        f.write(datetime.today().strftime('%Y-%m-%d_%H-%M-%S') + " RPI WAS STARTED\n")

def log_device_connected():
    with open("log.txt", "a") as f:  
        f.write(datetime.today().strftime('%Y-%m-%d_%H-%M-%S') + " DEVICE CONNECTED TO RPI\n")