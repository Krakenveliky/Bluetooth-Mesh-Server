import os
from datetime import datetime

with open("log.txt", "a") as f:  
    f.write(datetime.today().strftime('%Y-%m-%d_%H-%M-%S') + " LOG\n")








