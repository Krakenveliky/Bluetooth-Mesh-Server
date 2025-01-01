import os
from datetime import datetime

def log_message():
    with open("log.txt", "a") as f:  # Use 'a' mode for appending
        f.write(datetime.today().strftime('%Y-%m-%d_%H-%M-%S') + " LOG\n")
