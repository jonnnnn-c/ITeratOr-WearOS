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
        loggers["app"].info("Starting network verification and device pairing process...\n")

        # Step 1: Retrieve and log the current ESSID
        loggers["network"].info("Retrieving current network ESSID...")
        current_network_essid = get_current_network_essid(network_interface)
        if not current_network_essid:
            loggers["network"].error("Failed to retrieve the current network. Exiting setup.")
            return False, None, None
        
        loggers["network"].info(f"Currently connected to ESSID: {current_network_essid}")

        # Step 2: Perform a security check on the current network
        loggers["network"].info("Performing security check on the current network...")
        if not iwlist_security_check(network_interface, current_network_essid):
            loggers["network"].error("Security scan failed. Aborting connection setup.")
            return False, None, None
        
        loggers["network"].info("Network security check passed successfully.")

        # Step 3: Prompt user for an optional case number (integer)
        case_number = None
        while True:
            user_input = input("\nEnter an optional Case Number (integer) or press Enter to skip: ").strip()
            if not user_input:  # If user presses Enter, skip
                loggers["app"].info("No case number provided. Proceeding without it.")
                break
            elif user_input.isdigit():  # Validate if the input is a positive integer
                case_number = int(user_input)
                loggers["app"].info(f"User entered case number: {case_number}")
                break
            else:
                loggers["app"].warning("Invalid case number entered. It must be an integer.")
                print("Invalid input. Case number must be an integer. Please try again.")

        # Step 4: Prompt for optional router IP for vulnerability scan
        while True:
            print("\n" + "=" * 50)
            print("Optional: Check Router for Vulnerabilities")
            print("=" * 50)
            
            router_input = input(
                "This step helps ensure the security of the connection.\n"
                "Leave blank to skip vulnerability check.\n\n"
                "Enter Router IP, press Ctrl+C to exit the script prematurely:\n> "
            ).strip()
            
            print()

            if router_input:
                loggers["network"].info(f"User entered Router IP: {router_input}")
            else:
                loggers["network"].info("User chose to skip the vulnerability check.")
            
            # Validate IP format
            if not router_input:
                loggers["network"].info("Skipping router vulnerability check as no IP was provided.")
                break  # Skip vulnerability check if no input is provided

            if is_valid_ip(router_input):
                loggers["network"].info(f"Valid IP address entered: {router_input}. Initiating router vulnerability scan...\n")
                check_router_vulnerabilities(router_input)
                loggers["network"].info(f"Vulnerability scan completed for router IP: {router_input}")
                break
            else:
                loggers["network"].warning("Invalid IP address entered by user. Prompting again...")
                print("Invalid IP entered. Please enter a valid IP address.")

        # Step 5: Pair and verify connection to the smartwatch
        loggers["network"].info("Attempting to pair with the WearOS smartwatch...")
        success, watch_ip = pair_device()
        if not success:
            loggers["network"].error("Failed to pair with the smartwatch. Ensure it's in pairing mode and try again.")
            return False, None, None

        loggers["network"].info(f"Smartwatch paired successfully with IP: {watch_ip}")

        # Step 6: Verify network devices and establish connection
        loggers["network"].info("Verifying network devices and connectivity to the smartwatch...")

        # Step 7: Get the device's IP address
        loggers["network"].info("Fetching current device IP address...")
        current_device_ip = subprocess.getoutput("hostname -I | awk '{print $1}'").strip()

        if current_device_ip:
            loggers["network"].debug(f"Current device IP: {current_device_ip}")
        else:
            loggers["network"].error("Failed to retrieve the current device IP. Check network configuration.")
            return False, None, None

        # Step 8: Verify network communication with smartwatch
        if verify_network_devices(current_device_ip, watch_ip, network_interface):
            # Step 9: Attempt to connect to the smartwatch
            if connect_to_device(watch_ip):
                loggers["network"].info("Successfully established a connection to the smartwatch.")
                return True, watch_ip, case_number
            else:
                loggers["network"].error("Failed to establish a connection with the smartwatch after verification.")
        else:
            loggers["network"].error("Network verification failed. Please check your connections and try again.")

        return False, watch_ip, None

    except KeyboardInterrupt:
        loggers["app"].warning("Keyboard Interrupt: Setup process terminated by user.")
        exit_program()  # Ensure cleanup if needed
        return False, None, None
    except Exception as e:
        loggers["app"].error(f"An unexpected error occurred: {e}")
        return False, None, None
