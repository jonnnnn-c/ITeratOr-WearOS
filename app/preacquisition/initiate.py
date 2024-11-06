from app.logs.logger_config import initialize_loggers
from app.preacquisition.connect import *

# Initialize all loggers
loggers = initialize_loggers()


import re

def is_valid_ip(ip):
    """Validate an IPv4 address."""
    ip_pattern = r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$"
    if re.match(ip_pattern, ip):
        # Check if each segment is between 0 and 255
        return all(0 <= int(part) <= 255 for part in ip.split("."))
    return False

def initialise(network_interface):
    try:
        loggers["network"].info("Pairing to WearOS Smartwatch")

        # Retrieve and log the current ESSID
        current_network_essid = get_current_network_essid(network_interface)
        if not current_network_essid:
            loggers["network"].error("Could not retrieve the current network. Exiting...")
            return False
        loggers["network"].info(f"Currently connected to: {current_network_essid}")

        # Perform a security check on the current network
        if not iwlist_security_check(network_interface, current_network_essid):
            loggers["network"].error("Security scan failed. Aborting connection.")
            return False
        
        # Get the device's IP and optionally check router firmware version
        current_device_ip = subprocess.getoutput("hostname -I | awk '{print $1}'").strip()

        # Prompt for router IP with validation
        while True:
            router_ip = input(
                "\nOptional: retrieves and identifies the firmware version of a router by accessing its webpage for a version pattern (e.g., X.Y.Z)\n"
                "This step helps ensure compatibility and security of the connection.\n"
                "Leave blank if you do not want to check the firmware version.\n"
                "Router IP (e.g., 192.168.1.1): "
            ).strip()

            if not router_ip:
                break  # Skip firmware check if no IP is provided

            if is_valid_ip(router_ip):
                check_firmware_version(router_ip)
                break
            else:
                loggers["network"].error("Invalid IP address. Please enter a valid IPv4 address.")

        # Pair and verify connection to the smartwatch
        success, watch_ip = pair_device()
        if not success:
            loggers["network"].error("Failed to pair with the device.")
            return False, watch_ip

        if verify_network_devices(current_device_ip, watch_ip, network_interface) and connect_to_device(watch_ip):
            loggers["network"].info("Successfully connected to the smartwatch.")
            return True, watch_ip

        loggers["network"].error("Failed to connect to the device.")
        return False, watch_ip
        
    except KeyboardInterrupt:
        loggers["app"].warning("Keyboard Interrupt: Script ended abruptly")
        should_exit = True  # Set exit state
        exit_program()