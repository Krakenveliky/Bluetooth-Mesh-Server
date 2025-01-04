import os
from datetime import datetime
import platform
import subprocess

def log_message():
    # Setup logs directory
    log_dir = "/home/filip/mesh/Bluetooth-Mesh-Server/bootLogs"
    os.makedirs(log_dir, exist_ok=True)
    
    # Create log file with timestamp
    filename = os.path.join(log_dir, datetime.today().strftime('%Y-%m-%d_%H-%M-%S_boot_info.txt'))
    
    try:
        with open(filename, "w") as f:
            f.write("=== Raspberry Pi Boot Log ===\n\n")
            f.write(f"Boot Time: {datetime.today().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"System: {platform.platform()}\n")
            f.write(f"Hostname: {platform.node()}\n")
            
            # CPU Temperature
            try:
                cpu_temp = subprocess.check_output(["vcgencmd", "measure_temp"]).decode().strip()
                f.write(f"CPU Temperature: {cpu_temp}\n")
            except:
                f.write("CPU Temperature: N/A\n")
            
            # Memory Info
            try:
                mem_info = subprocess.check_output(["free", "-h"]).decode()
                f.write(f"\nMemory Information:\n{mem_info}\n")
            except:
                f.write("Memory Information: Error retrieving\n")
            
            # Disk Usage
            try:
                disk_info = subprocess.check_output(["df", "-h"]).decode()
                f.write(f"\nDisk Usage:\n{disk_info}\n")
            except:
                f.write("Disk Usage: Error retrieving\n")
                
    except Exception as e:
        print(f"Error creating boot log: {str(e)}")