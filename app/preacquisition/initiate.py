import re
import subprocess
from app.logs.logger_config import initialize_loggers
from app.preacquisition.network_management import *

# Initialize all loggers
loggers = initialize_loggers()

def is_valid_ip(ip):
    """Validate an IPv4 address."""
    ip_pattern = r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$"
    if re.match(ip_pattern, ip):
        # Check if each segment is between 0 and 255
        return all(0 <= int(part) <= 255 for part in ip.split("."))
    return False


def initialise(network_interface):
    """
    Sets up the WearOS smartwatch pairing and network verification.
    
    :param network_interface: Network interface to use (e.g., 'wlan0').
    :return: Tuple (success, watch_ip) where success is a boolean and watch_ip is the paired device's IP.
    """
    try:
        # Start of setup
        print("\n" + "=" * 50)
        print("Network Verification")
        print("=" * 50)

        # Step 1: Retrieve and log the current ESSID
        loggers["network"].info("Retrieving current network ESSID...")
        current_network_essid = get_current_network_essid(network_interface)
        if not current_network_essid:
            loggers["network"].error("Failed to retrieve the current network. Exiting setup.")
            return False, None
        loggers["network"].info(f"Currently connected to ESSID: {current_network_essid}\n")

        # Step 2: Perform a security check on the current network
        loggers["network"].info("Performing security check on the current network...")
        if not iwlist_security_check(network_interface, current_network_essid):
            loggers["network"].error("Security scan failed. Aborting connection setup.")
            return False, None
        loggers["network"].info("Network security check passed.\n")

        # Step 4: Prompt for optional router IP and port in "ip:port" format for firmware version check
        while True:
            router_input = input(
                "Optional: Retrieve and identify the router's firmware version.\n"
                "This step helps ensure compatibility and security of the connection.\n"
                "Leave blank to skip firmware check.\n"
                "Enter Router IP and Port in the format ip:port (e.g., 192.168.1.1:80): "
            ).strip()

            if not router_input:
                loggers["network"].info("Skipping firmware version check.")
                break  # Skip firmware check if no input is provided

            # Parse and validate IP and port
            if ":" in router_input:
                router_ip, router_port = router_input.split(":", 1)
                
                if is_valid_ip(router_ip) and router_port.isdigit() and 1 <= int(router_port) <= 65535:
                    loggers["network"].info(f"Checking firmware version for router at IP: {router_ip}, Port: {router_port}")
                    check_firmware_version(router_ip, router_port)
                    break
                else:
                    loggers["network"].error("Invalid IP or port entered. Please enter a valid IP and port (1-65535).")
            else:
                loggers["network"].error("Invalid format. Please enter in 'ip:port' format.")

        # Step 5: Pair and verify connection to the smartwatch
        loggers["network"].info("Attempting to pair with the WearOS smartwatch...")
        success, watch_ip = pair_device()
        if not success:
            loggers["network"].error("Failed to pair with the smartwatch. Ensure it's in pairing mode.")
            return False, None
        loggers["network"].info(f"Smartwatch paired successfully. Watch IP: {watch_ip}")

        # Step 6: Verify network devices and establish connection
        loggers["network"].info("Verifying network devices and connecting to smartwatch...")

        # Step 7: Get the device's IP address
        loggers["network"].info("Fetching current device IP address...")
        current_device_ip = subprocess.getoutput("hostname -I | awk '{print $1}'").strip()
        loggers["network"].debug(f"Current device IP: {current_device_ip}")

        if verify_network_devices(current_device_ip, watch_ip, network_interface):
            if connect_to_device(watch_ip):
                loggers["network"].info("Successfully connected to the smartwatch.")
                return True, watch_ip
            else:
                loggers["network"].error("Failed to establish a connection with the smartwatch.")
        else:
            loggers["network"].error("Network verification failed.")

        return False, watch_ip

    except KeyboardInterrupt:
        loggers["app"].warning("Keyboard Interrupt: Setup process terminated by user.")
        exit_program()  # Ensure cleanup if needed
        return False, None