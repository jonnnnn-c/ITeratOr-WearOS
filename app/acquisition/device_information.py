import os
import subprocess
from app.logs.logger_config import initialize_loggers
from app.setup import paths
from app.logs.run_save_acq_cmd import run_adb_command, append_to_output_file

# Initialize all loggers
loggers = initialize_loggers()

# Set output folder and output file path
upload_dir = paths.DEVICE_INFORMATION_DIR
output_file_path = os.path.join(upload_dir, "device_information.txt")


def get_device_info():
    """Function to capture device model and OS information"""
    device_model = run_adb_command(
        ["adb", "shell", "getprop", "ro.product.model"],
        "Retrieving: device model"
    )
    android_version = run_adb_command(
        ["adb", "shell", "getprop", "ro.build.version.release"],
        "Retrieving: android version"
    )
    serial_number = run_adb_command(
        ["adb", "shell", "getprop", "ro.serialno"],
        "Retrieving: serial number"
    )
    append_to_output_file(output_file_path, f"Device Model: {device_model}")
    append_to_output_file(
        output_file_path, f"Android Version: {android_version}")
    append_to_output_file(output_file_path, f"Serial Number: {serial_number}")


def get_network_info():
    """Function to capture network configuration"""
    network_interfaces = run_adb_command(
        ["adb", "shell", "ifconfig"],
        "Retrieving: network interfaces"
    )
    wifi_info = run_adb_command(
        ["adb", "shell", "dumpsys", "wifi"],
        "Retrieving: WiFi info"
    )
    append_to_output_file(
        output_file_path, f"Network Interfaces:\n{network_interfaces}")
    append_to_output_file(output_file_path, f"WiFi Info:\n{wifi_info}")


def get_battery_status():
    """Function to capture battery status"""
    battery_status = run_adb_command(
        ["adb", "shell", "dumpsys", "battery"],
        "Retrieving: battery status"
    )
    append_to_output_file(
        output_file_path, f"Battery Status:\n{battery_status}")


def get_storage_info():
    """Function to capture storage information"""
    storage_info = run_adb_command(
        ["adb", "shell", "df", "-h"],
        "Retrieving: storage information"
    )
    append_to_output_file(output_file_path, f"Storage Info:\n{storage_info}")


def get_installed_packages():
    """Function to list installed applications"""
    installed_packages = run_adb_command(
        ["adb", "shell", "pm", "list", "packages"],
        "Retrieving: installed packages"
    )
    append_to_output_file(
        output_file_path, f"Installed Packages:\n{installed_packages}")


def get_running_processes():
    """Function to get active processes"""
    running_processes = run_adb_command(
        ["adb", "shell", "ps", "-A"],
        "Retrieving: running processes"
    )
    append_to_output_file(
        output_file_path, f"Running Processes:\n{running_processes}")


def get_running_services():
    """Function to get running services"""
    running_services = run_adb_command(
        ["adb", "shell", "dumpsys", "activity", "services"],
        "Retrieving: running services"
    )
    append_to_output_file(
        output_file_path, f"Running Services:\n{running_services}")


def get_network_connections():
    """Function to get current network connections"""
    network_connections = run_adb_command(
        ["adb", "shell", "netstat"],
        "Retrieving: network connections"
    )
    append_to_output_file(
        output_file_path, f"Network Connections:\n{network_connections}")


def get_encryption_status():
    """Function to capture encryption status"""
    encryption_status = run_adb_command(
        ["adb", "shell", "getprop", "ro.crypto.state"],
        "Retrieving: encryption status"
    )
    append_to_output_file(
        output_file_path, f"Encryption Status: {encryption_status}")


def get_system_log():
    """Function to capture system logs (logcat)"""
    logcat_output = run_adb_command(
        ["adb", "logcat", "-d"],
        "Retrieving: system log (logcat)"
    )
    logcat_file_path = os.path.join(upload_dir, "logcat.txt")
    append_to_output_file(
        logcat_file_path, f"Logcat Output: {logcat_output}", action="w")


def capture_screenshot():
    """Function to capture a screenshot"""
    loggers["acquisition"].info(
        "Retrieving: Capturing screenshot of current screen")
    try:
        screenshot = subprocess.run(
            ["adb", "exec-out", "screencap", "-p"],
            check=True,
            stdout=subprocess.PIPE
        )
        loggers["acquisition"].info(
            "Screenshot captured and saved as screenshot.png")
        screenshot_file_path = os.path.join(upload_dir, "screenshot.png")
        append_to_output_file(
            screenshot_file_path,
            screenshot.stdout,
            action="wb",
            add_newline=False
        )

    except subprocess.CalledProcessError as e:
        loggers["acquisition"].error("Failed to capture screenshot.")
        loggers["acquisition"].error(e.stderr)


def available_functions():
    """List of available functions to document device state."""
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
        loggers["acquisition"].info(f"Created directory: {upload_dir}")

    return {
        "get_device_info": "Capture device model, android version, and serial number",
        "get_network_info": "Capture network interfaces, and WiFi info",
        "get_battery_status": "Capture battery status",
        "get_storage_info": "Capture storage information",
        "get_installed_packages": "List installed applications",
        "get_running_processes": "Get active processes",
        "get_running_services": "Get running services",
        "get_network_connections": "Get current network connections",
        "get_encryption_status": "Capture encryption status",
        "get_system_log": "Capture system logs (logcat)",
        "capture_screenshot": "Capture a screenshot of the device"
    }


def document_device_state():
    """Function to document the initial state of the device."""
    loggers["acquisition"].info("1. Running device information commands\n")
    all_functions = available_functions()
    
    # Loop through the dictionary and execute each function
    for func_name, description in all_functions.items():
        globals()[func_name]()  # Dynamically call the function by name
    loggers["acquisition"].info("Device state documentation completed.")
