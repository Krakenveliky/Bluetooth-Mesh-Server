import os
from datetime import datetime

def log_message(message="LOG SUCCESSFULLY ADDED"):
    with open("log.txt", "a") as f:
        f.write(datetime.today().strftime('%Y-%m-%d_%H-%M-%S') + " " + message + "\n")