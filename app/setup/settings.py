import os

# ========== API Key ==========
# Gemini API Key for Freeze Process Function
GENAI_API_KEY = os.getenv('GENAI_API_KEY', '')


# ========== Paths ==========
# Data Directory
SETUP_DIR = os.path.dirname(os.path.abspath(__file__))

ROOT_DIR = os.path.abspath(os.path.join(SETUP_DIR, "../.."))
OUTPUT_DIR = os.path.join(ROOT_DIR, "output/")

# Acquisition output
DEVICE_INFORMATION_DIR = os.path.join(OUTPUT_DIR, "device_information/")
ISOLATE_DEVICE_DIR = os.path.join(OUTPUT_DIR, "isolation_status/")
ANALYZE_PROCESSES_DIR = os.path.join(OUTPUT_DIR, "analyze_processes/")

# User Settings
USER_SETTING = os.path.join(SETUP_DIR, "user_settings.json")