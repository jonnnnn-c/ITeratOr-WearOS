import os
import subprocess

from app.preacquisition.connect import *

def dump_watch_data():
    """Dump data from the smartwatch into a file."""
    print("Dumping watch data...")
    devices = check_adb_devices()  # Check for connected devices
    if devices:
        try:
            # Get the current script directory
            current_directory = os.path.dirname(os.path.abspath(__file__))
            output_file = os.path.join(current_directory, 'wearos_dumpsys.txt')
            
            # Run the dumpsys command and redirect output to a file
            with open(output_file, 'w') as file:
                subprocess.run(['adb', 'shell', 'dumpsys'], stdout=file, stderr=subprocess.PIPE, check=True)
            
            print(f"Watch data dumped successfully to {output_file}.")
        except subprocess.CalledProcessError as e:
            print(f"Error dumping watch data: {e}")
    else:
        print("No devices found. Please ensure the smartwatch is connected.")