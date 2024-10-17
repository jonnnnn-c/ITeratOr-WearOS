import os
import subprocess
from app.logs.logger_config import initialize_loggers
from app.setup import paths
from app.logs.run_save_acq_cmd import run_adb_command, append_to_output_file

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
    )
    append_to_output_file(output_file_path, f"Original Airplane Mode Status: {original_value}")

    run_adb_command(
        ["adb", "shell", "settings", "put", "global", "airplane_mode_on", "1"],
        "Enabling airplane mode"
    )
    run_adb_command(
        ["adb", "shell", "am", "broadcast", "-a",
            "android.intent.action.AIRPLANE_MODE"],
        "Broadcasting airplane mode intent"
    )
    append_to_output_file(output_file_path, "Airplane mode enabled.")


def disable_mobile_data():
    """
    Disable mobile data on the device.

    Forensic Soundness: Disabling mobile data is generally acceptable as it 
    prevents the device from accessing external networks and reduces the 
    risk of remote wiping or data alteration.
    
    Recommendation: Safe to implement.

    """
    original_value = run_adb_command(
        ["adb", "shell", "svc", "data", "status"],
        "Retrieving original mobile data status"
    )
    append_to_output_file(output_file_path, f"Original Mobile Data Status: {original_value}")
    
    run_adb_command(
        ["adb", "shell", "svc", "data", "disable"],
        "Disabling mobile data"
    )
    append_to_output_file(output_file_path, "Mobile data disabled.")
    loggers["acquisition"].info("Mobile data has been disabled.")


def disable_bluetooth():
    """
    Disable Bluetooth on the device.
    
    Forensic Soundness: Disabling Bluetooth prevents unauthorized connections. 
    This is typically a sound practice for isolation.
    
    Recommendation: Safe to implement.

    """
    original_value = run_adb_command(
        ["adb", "shell", "settings", "get", "global", "bluetooth_on"],
        "Retrieving original Bluetooth status"
    )
    # Interpret the value (0 = off, 1 = on)
    if original_value == "0":
        status = "Bluetooth is OFF"
    elif original_value == "1":
        status = "Bluetooth is ON"
    else:
        status = f"Unknown Bluetooth status: {original_value}"

    run_adb_command(
        ["adb", "shell", "svc", "bluetooth", "disable"],
        "Disabling Bluetooth"
    )
    append_to_output_file(output_file_path, "Bluetooth disabled.")
    loggers["acquisition"].info("Bluetooth has been disabled.")


def stop_background_sync():
    """
    Stop background synchronization.
    
    Forensic Soundness: Stopping background sync can prevent apps from sending 
    data or receiving updates. However, this may alter the state of certain 
    applications, which could affect data integrity.
    
    Recommendation: Consider the impact on app states; if possible, 
    document which apps are affected.

    """
    original_value = run_adb_command(
        ["adb", "shell", "settings", "get", "global", "background_data"],
        "Retrieving original background data sync status"
    )
    append_to_output_file(output_file_path, f"Original Background Data Sync Status: {original_value}")
    
    run_adb_command(
        ["adb", "shell", "settings", "put", "global", "background_data", "0"],
        "Stopping background data sync"
    )
    append_to_output_file(output_file_path, "Background data sync stopped.")
    loggers["acquisition"].info("Background data sync has been stopped.")


def lock_screen():
    """
    Lock the device screen.
    
    Forensic Soundness: Locking the screen does not affect data integrity 
    and can help secure the device.
    
    Recommendation: Safe to implement

    """
    run_adb_command(
        ["adb", "shell", "input", "keyevent", "26"],  # Keyevent for power button
        "Locking the screen"
    )
    append_to_output_file(output_file_path, "Screen locked.")
    loggers["acquisition"].info("Device screen has been locked.")


def disable_location_services():
    """
    Disable location services.
    
    Forensic Soundness: Disabling location services may alter the state of applications 
    that rely on location data, potentially affecting the evidence collected.
    
    Recommendation: Use with caution; document that location services were disabled.
    
    """
    original_value = run_adb_command(
        ["adb", "shell", "settings", "get", "secure", "location_mode"],
        "Retrieving original location services status"
    )
    append_to_output_file(output_file_path, f"Original Location Services Status: {original_value}")
    
    run_adb_command(
        ["adb", "shell", "settings", "put", "secure", "location_mode", "0"],
        "Disabling location services"
    )
    append_to_output_file(output_file_path, "Location services disabled.")
    loggers["acquisition"].info("Location services have been disabled.")


def available_functions():
    """List of available functions for isolating the device."""

    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
        loggers["acquisition"].info(f"Created directory: {upload_dir}")

    return {
        "enable_airplane_mode": "Enable airplane mode on the device",
        "disable_mobile_data": "Disable mobile data on the device",
        "disable_bluetooth": "Disable Bluetooth on the device",
        "stop_background_sync": "Stop background synchronization",
        "lock_screen": "Lock the device screen",
        "disable_location_services": "Disable location services",
    }


def isolate_device_state():
    """Document the isolation state of the device."""
    print()
    loggers["acquisition"].info("2. Running isolation of device commands\n")
    all_functions = available_functions()
    
    # Loop through the dictionary and execute each function
    for func_name, description in all_functions.items():
        globals()[func_name]()  # Dynamically call the function by name
    loggers["acquisition"].info("Device isolation completed.")
