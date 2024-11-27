import os

# ========== API Key ==========
# Gemini API Key for Freeze Process Function
GENAI_API_KEY = "AIxxxx"  # Input API Key here, cant get from env if not will show errors


# ========== Paths ==========
# Data Directory
SETUP_DIR = os.path.dirname(os.path.abspath(__file__))

ROOT_DIR = os.path.abspath(os.path.join(SETUP_DIR, "../.."))
OUTPUT_DIR = os.path.join(ROOT_DIR, "output/")

# Acquisition output
NETWORK_DIR = os.path.join(OUTPUT_DIR, "preacquisition/")
DEVICE_INFORMATION_DIR = os.path.join(OUTPUT_DIR, "device_information/")
ISOLATE_DEVICE_DIR = os.path.join(OUTPUT_DIR, "isolation_status/")
ANALYZE_PROCESSES_DIR = os.path.join(OUTPUT_DIR, "analyze_processes/")
LOGICAL_DATA_EXTRACTION_DIR = os.path.join(OUTPUT_DIR, "logical_data_extraction/")

# User Settings
USER_SETTING = os.path.join(SETUP_DIR, "user_settings.json")