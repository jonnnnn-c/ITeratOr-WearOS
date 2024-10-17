"""
adb shell settings get global airplane_mode_on
# 0|1 -  dis/en abled

adb shell settings get global mobile_data
# 0|1 - dis/en abled

adb shell settings get global wifi_on
# 0|1 - dis/en abled

adb shell settings get global bluetooth_on
# 2|1 - dis/en abled

adb shell settings get global cell_on
# 2|1 - dis/en abled
"""

import os
from app.setup import paths
from app.logs.logger_config import initialize_loggers, run_adb_command, append_to_output_file

# Initialize all loggers
loggers = initialize_loggers()

# Set output folder and output file path
upload_dir = paths.ISOLATE_DEVICE_DIR
output_file_path = os.path.join(upload_dir, "isolation_status.txt")


def enable_airplane_mode():
    """Enable airplane mode on the device."""
    original_value = run_adb_command(
        ["adb", "shell", "settings", "get", "global", "airplane_mode_on"],
        "Retrieving original airplane mode status"
    ).strip()

    # Interpret the value
    status = "Airplane Mode is OFF" if original_value == "0" else "Airplane Mode is ON"
    append_to_output_file(output_file_path, f"Original Airplane Mode Status: {status}")

    run_adb_command(
        ["adb", "shell", "settings", "put", "global", "airplane_mode_on", "1"],
        "Enabling airplane mode"
    )
    run_adb_command(
        ["adb", "shell", "am", "broadcast", "-a", "android.intent.action.AIRPLANE_MODE"],
        "Broadcasting airplane mode intent"
    )
    append_to_output_file(output_file_path, "Airplane mode enabled.")


def disable_mobile_data():
    """Disable mobile data on the device."""
    original_value = run_adb_command(
        ["adb", "shell", "settings", "get", "global", "mobile_data"],
        "Retrieving original mobile data status"
    ).strip()

    status = "Mobile Data is OFF" if original_value == "0" else "Mobile Data is ON"
    append_to_output_file(output_file_path, f"Original Mobile Data Status: {status}")
    
    run_adb_command(
        ["adb", "shell", "svc", "data", "disable"],
        "Disabling mobile data"
    )
    append_to_output_file(output_file_path, "Mobile data disabled.")


def disable_bluetooth():
    """Disable Bluetooth on the device."""
    original_value = run_adb_command(
        ["adb", "shell", "settings", "get", "global", "bluetooth_on"],
        "Retrieving original Bluetooth status"
    ).strip()

    # Interpret the value (0 = off, 1 = on, 2 = unavailable)
    if original_value == "1":
        status = "Bluetooth is ON"
    elif original_value == "0":
        status = "Bluetooth is OFF"
    elif original_value == "2":
        status = "Bluetooth is unavailable"
    else:
        status = f"Unknown Bluetooth status: {original_value}"

    append_to_output_file(output_file_path, f"Original Bluetooth Status: {status}")

    run_adb_command(
        ["adb", "shell", "svc", "bluetooth", "disable"],
        "Disabling Bluetooth"
    )
    append_to_output_file(output_file_path, "Bluetooth disabled.")


def disable_wifi():
    """Disable WiFi on the device."""
    original_value = run_adb_command(
        ["adb", "shell", "settings", "get", "global", "wifi_on"],
        "Retrieving original WiFi status"
    ).strip()

    status = "WiFi is OFF" if original_value == "0" else "WiFi is ON"
    append_to_output_file(output_file_path, f"Original WiFi Status: {status}")
    
    run_adb_command(
        ["adb", "shell", "svc", "wifi", "disable"],
        "Disabling WiFi"
    )
    append_to_output_file(output_file_path, "WiFi disabled.")


def disable_location_services():
    """Disable location services."""
    original_value = run_adb_command(
        ["adb", "shell", "settings", "get", "secure", "location_mode"],
        "Retrieving original location services status"
    ).strip()

    status = "Location Services are OFF" if original_value == "0" else "Location Services are ON"
    append_to_output_file(output_file_path, f"Original Location Services Status: {status}")

    run_adb_command(
        ["adb", "shell", "settings", "put", "secure", "location_mode", "0"],
        "Disabling location services"
    )
    append_to_output_file(output_file_path, "Location services disabled.")


def available_functions():
    """List of available functions for isolating the device."""
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
        loggers["acquisition"].debug(f"Created directory: {upload_dir}")

    return {
        "enable_airplane_mode": "Enable airplane mode on the device",
        "disable_mobile_data": "Disable mobile data on the device",
        "disable_bluetooth": "Disable Bluetooth on the device",
        "disable_wifi": "Disable WiFi on the device",
        "disable_location_services": "Disable location services"
    }


def isolate_device_state():
    """Document the isolation state of the device."""
    loggers["acquisition"].info("2. Running isolation of device commands\n")
    all_functions = available_functions()

    # Loop through the dictionary and execute each function
    for func_name in all_functions.keys():
        globals()[func_name]()  # Dynamically call the function by name
    
    loggers["acquisition"].info("Device isolation completed.\n")
