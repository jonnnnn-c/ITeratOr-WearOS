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
    try:
        original_value = run_adb_command(
            ["adb", "shell", "settings", "get", "global", "airplane_mode_on"],
            "Retrieving original airplane mode status"
        ).strip()  # .strip() to clean up the result

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
    
    except AttributeError as e:
        loggers["acquisition"].error(f"Failed to retrieve airplane mode status: {e}")
    except Exception as e:
        loggers["acquisition"].error(f"An error occurred while enabling airplane mode: {e}")


def disable_mobile_data():
    """Disable mobile data on the device."""
    try:
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

    except AttributeError as e:
        loggers["acquisition"].error(f"Failed to retrieve mobile data status: {e}")
    except Exception as e:
        loggers["acquisition"].error(f"An error occurred while disabling mobile data: {e}")


def disable_bluetooth():
    """Disable Bluetooth on the device."""
    try:
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
    
    except AttributeError as e:
        loggers["acquisition"].error(f"Failed to retrieve Bluetooth status: {e}")
    except Exception as e:
        loggers["acquisition"].error(f"An error occurred while disabling Bluetooth: {e}")


def disable_wifi():
    """Disable WiFi on the device."""
    try:
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
    
    except AttributeError as e:
        loggers["acquisition"].error(f"Failed to retrieve WiFi status: {e}")
    except Exception as e:
        loggers["acquisition"].error(f"An error occurred while disabling WiFi: {e}")


def disable_location_services():
    """Disable location services."""
    try:
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
    
    except AttributeError as e:
        loggers["acquisition"].error(f"Failed to retrieve location services status: {e}")
    except Exception as e:
        loggers["acquisition"].error(f"An error occurred while disabling location services: {e}")


def set_max_screen_timeout():
    """Set screen timeout to the maximum allowable value."""
    try:
        # Retrieve current screen timeout setting
        original_value = run_adb_command(
            ["adb", "shell", "settings", "get", "system", "screen_off_timeout"],
            "Retrieving original screen timeout"
        ).strip()

        append_to_output_file(output_file_path, f"Original Screen Timeout: {original_value} ms")

        # Set screen timeout to max value (24 hours = 86400000 ms)
        run_adb_command(
            ["adb", "shell", "settings", "put", "system", "screen_off_timeout", "86400000"],
            "Setting screen timeout to maximum (24 hours)"
        )
        append_to_output_file(output_file_path, "Screen timeout set to 24 hours.")
    
    except AttributeError as e:
        loggers["acquisition"].error(f"Failed to retrieve screen timeout setting: {e}")
    except Exception as e:
        loggers["acquisition"].error(f"An error occurred while setting screen timeout: {e}")


def set_max_watchface_timeout():
    """Set 'Go to watch face' timeout to the maximum allowable value."""
    try:
        # Retrieve current "Go to watch face" timeout setting
        original_value = run_adb_command(
            ["adb", "shell", "settings", "get", "secure", "wear_display_timeout"],
            "Retrieving original 'Go to watch face' timeout"
        ).strip()

        append_to_output_file(output_file_path, f"Original 'Go to watch face' Timeout: {original_value} ms")

        # Set "Go to watch face" timeout to max value (often 1 hour = 3600000 ms)
        run_adb_command(
            ["adb", "shell", "settings", "put", "secure", "wear_display_timeout", "3600000"],
            "Setting 'Go to watch face' timeout to maximum (1 hour)"
        )
        append_to_output_file(output_file_path, "'Go to watch face' timeout set to 1 hour.")
    
    except AttributeError as e:
        loggers["acquisition"].error(f"Failed to retrieve 'Go to watch face' timeout setting: {e}")
    except Exception as e:
        loggers["acquisition"].error(f"An error occurred while setting 'Go to watch face' timeout: {e}")


def enable_stay_awake():
    """Enable the 'Stay awake while charging' setting."""
    try:
        # Enable 'Stay Awake' mode, which is setting 'stay_on_while_plugged_in' to 7 (USB, AC, and wireless charging)
        run_adb_command(
            ["adb", "shell", "settings", "put", "global", "stay_on_while_plugged_in", "7"],
            "Enabling 'Stay awake while charging'"
        )
        append_to_output_file(output_file_path, "'Stay awake while charging' enabled.")
    
    except Exception as e:
        loggers["acquisition"].error(f"An error occurred while enabling 'Stay awake while charging': {e}")


def available_functions():
    """List of available functions for isolating the device."""
    try:
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)
            loggers["acquisition"].debug(f"Created directory: {upload_dir}")

        return {
            "enable_airplane_mode": "Enable airplane mode on the device",
            "disable_mobile_data": "Disable mobile data on the device",
            "disable_bluetooth": "Disable Bluetooth on the device",
            "disable_wifi": "Disable WiFi on the device",
            "disable_location_services": "Disable location services",
            "set_max_screen_timeout": "Set screen timeout to maximum value (24 hours)",
            "set_max_watchface_timeout": "Set 'Go to watch face' timeout to maximum (1 hour)",
            "enable_stay_awake": "Enable 'Stay awake while charging'"
        }
    
    except Exception as e:
        loggers["acquisition"].error(f"An error occurred while listing available functions: {e}")
        return {}  # Return an empty dictionary if something goes wrong


def isolate_device_state():
    """Document the isolation state of the device."""
    try:
        loggers["acquisition"].info("2. Running isolation of device commands\n")
        all_functions = available_functions()

        # Loop through the dictionary and execute each function
        for func_name in all_functions.keys():
            globals()[func_name]()  # Dynamically call the function by name
        
        loggers["acquisition"].info("Device isolation completed.\n")
    
    except Exception as e:
        loggers["acquisition"].error(f"An error occurred while isolating the device: {e}")
