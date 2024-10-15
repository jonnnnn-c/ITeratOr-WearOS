import os

# Data Directory
SETUP_DIR = os.path.dirname(os.path.abspath(__file__))

ROOT_DIR = os.path.abspath(os.path.join(SETUP_DIR, "../.."))
OUTPUT_DIR = os.path.join(ROOT_DIR, 'output/')
DEVICE_INFORMATION_DIR = os.path.join(OUTPUT_DIR, 'device_information/')