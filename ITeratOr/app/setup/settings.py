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
NETWORK_DIR = os.path.join(OUTPUT_DIR, "1_preacquisition/")
DEVICE_INFORMATION_DIR = os.path.join(OUTPUT_DIR, "2_device_information/")
ISOLATE_DEVICE_DIR = os.path.join(OUTPUT_DIR, "3_isolation_status/")
DATA_EXTRACTION_DIR = os.path.join(OUTPUT_DIR, "4_data_extraction/")
LOGICAL_DATA_EXTRACTION_DIR = os.path.join(DATA_EXTRACTION_DIR, "logical_data_extraction/")
PHYSICAL_DATA_EXTRACTION_DIR = os.path.join(DATA_EXTRACTION_DIR, "physical_data_extraction/")
ANALYZE_PROCESSES_DIR = os.path.join(OUTPUT_DIR, "5_analyze_processes/")

# User Settings
USER_SETTING = os.path.join(SETUP_DIR, "user_settings.json")

# Logical Data Extraction folders
EXCLUDED_FOLDERS = {"dev", "proc", "sys"}
"""
dev: The files in /dev are not actual data files but virtual interfaces created dynamically at runtime by the kernel. They do not persist between reboots and do not store static data.
proc: The contents of /proc are entirely dynamic and exist only while the device is running. Once the device is powered off or rebooted, the data is lost.
sys: Like /proc, the contents of /sys are generated dynamically by the kernel and do not persist across reboots.
"""

IMPORTANT_FOLDERS = {"sdcard", "/system/apex", "/etc/hosts", "/system/etc", "/system/fonts", "/system/framework", "/system/hidden", "/system/lib", "/system/media", "/system/priv-app", "/system/tts", "/system/usr"}
"""
sdcard: This directory often holds evidence of user activity, making it critical for digital investigations.
/system/apex: Tampered or outdated APEX modules can indicate a compromised system or unauthorized firmware modification.
/etc/hosts: Modifications to this file can reveal attempts to redirect network traffic for malicious purposes.
/system/etc: Investigating system configuration files can reveal how the device is set up and identify signs of unauthorized changes.
/system/fonts: Modified or added fonts could indicate customization or tampering with the system (e.g., to inject malicious code in stylized texts).
/system/framework: Any tampering here could compromise the operating system’s behavior or indicate the presence of custom ROMs or malware.
/system/hidden: Hidden files can provide insight into device configurations, debugging attempts, or manufacturer-specific customizations.
/system/lib: Modified libraries could indicate the presence of exploits or tampered software.
/system/media: Changes to this directory can reveal user customization or tampering, such as replacing boot animations with malicious versions.
/system/priv-app: Unauthorized apps in this directory can pose significant risks since they run with elevated privileges.
/system/tts: Changes in TTS files could be a vector for malware or indicate system modifications.
/system/usr: Modifications here can indicate attempts to monitor or intercept user inputs, such as keylogging.
"""