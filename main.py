import os
from datetime import datetime

f = open("log.txt", "w")
f.writelines([datetime.today().strftime('%Y-%m-%d_%H-%M-%S'),"LOG"])
f.close()
#Komentar

