import os
import subprocess
from app.setup import settings
from app.logs.logger_config import initialize_loggers, run_adb_command, append_to_output_file

# Initialize all loggers
loggers = initialize_loggers()

# Set output folder and output file path
upload_dir = settings.DEVICE_INFORMATION_DIR
output_file_path = os.path.join(upload_dir, "device_information.txt")


def get_device_info():
    """Function to capture device model and OS information"""
    device_name = run_adb_command(
        ["adb", "shell", "getprop", "ro.product.name"],
        "Retrieving: device name"
    )
    device_model = run_adb_command(
        ["adb", "shell", "getprop", "ro.product.model"],
        "Retrieving: device model"
    )
    device_manufacturer = run_adb_command(
        ["adb", "shell", "getprop", "ro.product.manufacturer"],
        "Retrieving: device manufacturer"
    )
    serial_number = run_adb_command(
        ["adb", "shell", "getprop", "ro.serialno"],
        "Retrieving: serial number"
    )
    device_code = run_adb_command(
        ["adb", "shell", "getprop", "ro.product.code"],
        "Retrieving: device code"
    )
    device_chip = run_adb_command(
        ["adb", "shell", "getprop", "ro.chipname"],
        "Retrieving: device chipset"
    )
    append_to_output_file(output_file_path, f"Device Name: {device_name}")
    append_to_output_file(output_file_path, f"Device Model: {device_model}")
    append_to_output_file(output_file_path, f"Device Manufacturer: {device_manufacturer}")
    append_to_output_file(output_file_path, f"Serial Number: {serial_number}")
    append_to_output_file(output_file_path, f"Device Code: {device_code}")
    append_to_output_file(output_file_path, f"Device Chip: {device_chip}")


def get_envs_info():
    """Function to capture device environment information"""
    build_id = run_adb_command(
        ["adb", "shell", "getprop", "ro.build.id"],
        "Retrieving: system build ID"
    )
    build_date = run_adb_command(
        ["adb", "shell", "getprop", "ro.build.date"],
        "Retrieving: system build date"
    )
    build_fingerprint = run_adb_command(
        ["adb", "shell", "getprop", "ro.build.fingerprint"],
        "Retrieving: system build fingerprint"
    )
    build_version = run_adb_command(
        ["adb", "shell", "getprop", "ro.build.version.release"],
        "Retrieving: android version"
    )
    build_security_path = run_adb_command(
        ["adb", "shell", "getprop", "ro.build.version.security_patch"],
        "Retrieving: latest android security patch"
    )
    build_bootloader = run_adb_command(
        ["adb", "shell", "getprop", "ro.boot.bootloader"],
        "Retrieving: build bootloader"
    )
    sys_timezone = run_adb_command(
        ["adb", "shell", "getprop", "persist.sys.timezone"],
        "Retrieving: device timezone"
    )
    sys_uptime = run_adb_command(
        ["adb", "shell", "uptime"],
        "Retrieving: device uptime"
    )
    kernel_info = run_adb_command(
        ["adb", "shell", "cat", "/proc/version"],
        "Retrieving: kernel information"
    )
    usr_priv = run_adb_command(
        ["adb", "shell", "id"],
        "Retrieving: user privileges"
    )
    su_priv = run_adb_command(
        ["adb", "shell", "su", "-c", "id"],
        "Retrieving: superuser privileges"
    )
    append_to_output_file(output_file_path, f"Device Build ID: {build_id}")
    append_to_output_file(output_file_path, f"Device Build Date: {build_date}")
    append_to_output_file(
        output_file_path, f"Device Build Fingerprint: {build_fingerprint}")
    append_to_output_file(output_file_path, f"Android Version: {build_version}")
    append_to_output_file(
        output_file_path, f"Latest Security Patch: {build_security_path}")
    append_to_output_file(
        output_file_path, f"Device Bootloader: {build_bootloader}")
    append_to_output_file(output_file_path, f"Device Timezone: {sys_timezone}")
    append_to_output_file(output_file_path, f"Device Uptime: {sys_uptime}")
    append_to_output_file(output_file_path, f"Kernel Information: {kernel_info}")
    append_to_output_file(output_file_path, f"User Privileges: {usr_priv}")
    append_to_output_file(output_file_path, f"Superuser Privileges: {su_priv}")


def get_disk_partition():
    """Function to capture all disk partitions and configurations"""
    disk_partition = run_adb_command(
        ["adb", "shell", "cat", "/proc/diskstats"],
        "Retrieving: disk partitions"
    )
    append_to_output_file(
        output_file_path, f"Disk Partitions: {disk_partition}")


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


def get_biometric_info():
    """Function to capture biometric information"""
    biometric_info = run_adb_command(
        ["adb", "shell", "dumpsys", "biometric"],
        "Retrieving: biometric information"
    )
    append_to_output_file(
        output_file_path, f"Biometric Information:\n{biometric_info}")
    

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
    device_usrs = run_adb_command(
        ["adb", "shell", "pm", "list", "users"],
        "Retrieving: device users"
    )
    permission_grp = run_adb_command(
        ["adb", "shell", "pm", "list", "permission-groups"],
        "Retrieving: device permission groups"
    )
    packages_permissions = run_adb_command(
        ["adb", "shell", "pm", "list", "permissions", "-f"],
        "Retrieving: packages permisisons"
    )
    installed_packages = run_adb_command(
        ["adb", "shell", "pm", "list", "packages"],
        "Retrieving: installed packages"
    )
    append_to_output_file(
        output_file_path, f"Device Users:\n{device_usrs}")
    append_to_output_file(
        output_file_path, f"Device Permission Groups:\n{installed_packages}")
    append_to_output_file(
        output_file_path, f"Installed Packages:\n{packages_permissions}")
    append_to_output_file(
        output_file_path, f"Installed Packages:\n{installed_packages}")


def get_running_processes():
    """Function to get active processes"""
    running_processes = run_adb_command(
        ["adb", "shell", "ps", "-A"],
        "Retrieving: running processes"
    )
    memory_info = run_adb_command(
        ["adb", "shell", "dumpsys", "meminfo"],
        "Retrieving: running processes"
    )
    append_to_output_file(
        output_file_path, f"Running Processes:\n{running_processes}")
    append_to_output_file(
        output_file_path, f"Memory Information:\n{memory_info}")


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
        ["adb", "shell", "netstat", "-an"],
        "Retrieving: network connections"
    )
    network_rules = run_adb_command(
        ["adb", "shell", "dumpsys", "network_management"],
        "Retrieving: WiFi info"
    )
    network_logs = run_adb_command(
        ["adb", "shell", "dumpsys", "connectivity"],
        "Retrieving: WiFi info"
    )
    persistent_jobs = run_adb_command(
        ["adb", "shell", "dumpsys", "jobscheduler"],
        "Retrieving: WiFi info"
    )
    append_to_output_file(
        output_file_path, f"Network Connections:\n{network_connections}")
    append_to_output_file(
        output_file_path, f"Network Rules:\n{network_rules}")
    append_to_output_file(
        output_file_path, f"Network Logs:\n{network_logs}")
    append_to_output_file(
        output_file_path, f"Persistent Jobs:\n{persistent_jobs}")


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
        screenshot_file_path = os.path.join(upload_dir, "screenshot.png")
        append_to_output_file(
            screenshot_file_path,
            screenshot.stdout,
            action="wb",
            add_newline=False
        )
        loggers["acquisition"].info(
            "Screenshot captured and saved as screenshot.png")
    except subprocess.CalledProcessError as e:
        loggers["acquisition"].error("Failed to capture screenshot.")
        loggers["acquisition"].error(e.stderr)


def get_packages_information():
    """Function to capture system logs (logcat)"""
    dumpsys_package = run_adb_command(
        ["adb", "shell", "dumpsys", "package"],
        "Retrieving: package dump information (dumpsys)"
    )
    dumpsys_package_path = os.path.join(upload_dir, "dumpsys_package.txt")
    append_to_output_file(
        dumpsys_package_path, f"Dumpsys Package Output: {dumpsys_package}", action="w")


def available_functions():
    """List of available functions to document device state."""
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
        loggers["acquisition"].debug(f"Created directory: {upload_dir}")

    return {
        "get_device_info": "Capture device model and and serial number",
        "get_envs_info": "Capture all device environment information",
        "get_disk_partition": "Capture all disk partitions and configurations",
        "get_network_info": "Capture network interfaces, and WiFi info",
        "get_biometric_info": "Capture biometric information",
        "get_battery_status": "Capture battery status",
        "get_storage_info": "Capture storage information",
        "get_installed_packages": "List installed applications",
        "get_running_processes": "Get active processes",
        "get_running_services": "Get running services",
        "get_network_connections": "Get current network connections",
        "get_encryption_status": "Capture encryption status",
        "get_system_log": "Capture system logs (logcat)",
        "capture_screenshot": "Capture a screenshot of the device",
        "get_packages_information": "Get information of all packages"
    }


def document_device_state():
    """Function to document the initial state of the device."""
    all_functions = available_functions()
    
    # Loop through the dictionary and execute each function
    for func_name in all_functions.keys():
        globals()[func_name]()  # Dynamically call the function by name
    loggers["acquisition"].info("Device state documentation completed.\n")
