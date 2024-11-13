import re
import subprocess
import time
import os
import ipaddress
import json
from netdiscover import *  # type: ignore
from app.logs.logger_config import initialize_loggers
from app.setup.choices import exit_program, check_for_given_file
from app.setup.settings import *
from app.preacquisition.run_netdiscover import *
from app.setup.setup_environment import *
from app.logs.logger_config import run_adb_command

# Initialize all loggers
loggers = initialize_loggers()


def check_firmware_version(router_ip):
    """Check for router firmware version using wget."""
    try:
        # Use wget to fetch the router's webpage
        result = subprocess.run(
            ['wget', '-qO-', f'http://{router_ip}'],
            capture_output=True,
            text=True,
            check=True
        )

        # Check for common indicators of firmware version in the output
        output = result.stdout
        # Adjust regex as needed
        firmware_version_pattern = r'(?i)firmware.*?(\d+\.\d+\.\d+|\d+)'
        match = re.search(firmware_version_pattern, output)

        if match:
            loggers["network"].info(
                f"Router firmware version found: {match.group(0)}")
            return match.group(0)  # Return the firmware version
        else:
            loggers["network"].error(
                "Firmware version not found in the router's webpage.")
            return None

    except subprocess.CalledProcessError as e:
        loggers["network"].error(f"Error fetching router page: {e}")
        return None

def get_current_network_essid(interface):
    """Retrieve the ESSID of the currently connected wireless network."""
    essid = run_command(['iwgetid', '-r', interface]).strip()
    if essid is None:
        loggers["network"](f"Error retrieving current ESSID for interface {interface}")
    return essid


def iwlist_security_check(interface, current_network):
    """Use iwlist to check Wi-Fi protocol and encryption key status."""
    try:
        loggers["network"].info(f"Starting Wi-Fi security check on interface '{interface}' for network '{current_network}'.")

        # Run the iwlist scan and capture the output
        result = run_command(['iwlist', interface, 'scan'])
        
        secure_network_found = False
        current_essid = None

        for line in result.splitlines():
            # Check for ESSID line
            if "ESSID" in line:
                essid_value = line.split("ESSID:", 1)[1].strip().strip('"')
                
                # Skip and log empty or invalid ESSIDs
                if not essid_value:
                    loggers["network"].warning("Detected network with empty ESSID. Skipping.")
                    current_essid = None  # Set to None to ensure clarity
                    continue
                else:
                    current_essid = essid_value
                    loggers["network"].info(f"Detected network: '{current_essid}'")

            # Check for encryption key line only if ESSID is valid
            if current_essid and "Encryption key" in line:
                encryption_status = line.split("Encryption key:", 1)[1].strip()
                if encryption_status == "off":
                    loggers["network"].error(
                        f"Network '{current_essid}' detected, but encryption is off. Connection is insecure."
                    )
                    return False
                else:
                    loggers["network"].info(
                        f"Network '{current_essid}' has encryption enabled."
                    )

            # Check for encryption type in WPA/WPA2/WPA3 only if ESSID is valid
            if current_essid == current_network and "IE:" in line:
                if "WPA3" in line:
                    encryption_type = "WPA3"
                elif "WPA2" in line:
                    encryption_type = "WPA2"
                elif "WPA" in line:
                    encryption_type = "WPA"
                else:
                    encryption_type = "Unknown"

                # Log and mark as secure if encryption type is identified
                if encryption_type != "Unknown":
                    loggers["network"].info(
                        f"Network '{current_essid}' uses {encryption_type} encryption."
                    )
                    secure_network_found = True
                    break  # Stop once the desired network is verified

        # Final check if network is secure
        if secure_network_found and current_essid == current_network:
            loggers["network"].info(
                f"Current network '{current_network}' is secure with {encryption_type} encryption."
            )
            return True

        # If no secure network is found in scan results
        loggers["network"].error(
            f"Current network '{current_network}' not found in scan results or is not secure."
        )
        return False

    except subprocess.CalledProcessError as e:
        loggers["network"].error(f"Error during Wi-Fi scan on interface '{interface}': {e}")
        return False



def is_valid_ip(ip):
    """Validate an IPv4 address."""
    ip_pattern = r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$"
    if re.match(ip_pattern, ip):
        # Check if each segment is between 0 and 255
        return all(0 <= int(part) <= 255 for part in ip.split("."))
    return False


def pair_device():
    """Prompt for IP address and port to pair the device using ADB."""

    # Start of setup
    print("\n" + "="*50)
    print("WearOS smartwatch Pairing Setup")
    print("="*50)
    loggers["network"].info(
        "Starting the pairing process with WearOS smartwatch.")

    # Provide guidance on obtaining the IP address
    print("\n" + "="*80)
    print("How to find the necessary information to pair with WearOS smartwatch")
    print("="*80)
    print("1. On your WearOS smartwatch, go to Settings > Developer Options > Wireless Debugging.")
    print("2. Connect to a Wi-Fi network if not already connected.")
    print("3. Click 'Pair new device'.")
    print("4. Enter the IP address and port number when prompted.\n")

    loggers["network"].info(
        "Providing instructions to user on obtaining IP address.")

    # Prompt for IP address with validation
    while True:
        ip_address = input(
            "\nEnter the IP address of the smartwatch:\n"
            "(Example: 192.168.1.10)\n> "
        ).strip()

        if is_valid_ip(ip_address):
            loggers["network"].info(f"Valid IP address entered: {ip_address}")
            break
        else:
            loggers["network"].error(
                "Invalid IP address entered. Please enter a valid IPv4 address.")
            print("Invalid IP address entered. Please enter a valid IPv4 address.")

    # Prompt for port number with validation
    while True:
        port_input = input(
            "\nEnter the port number to pair with the smartwatch:\n"
            "(Example: [1-65535])\n> "
        ).strip()

        if port_input.isdigit():
            port = int(port_input)
            if is_valid_port(port):
                loggers["network"].info(f"Valid port number entered: {port}")
                break
            else:
                loggers["network"].error(
                    "Invalid port number entered. Please enter a number between 1 and 65535.")
                print(
                    "Invalid port number entered. Please enter a number between 1 and 65535.")
        else:
            loggers["network"].error(
                "Invalid input for port. Please enter a valid integer.")
            print("Invalid input for port. Please enter a valid integer.")

    # Attempting pairing using adb
    pair_command = f"{ip_address}:{port}"
    loggers["network"].info(
        f"Attempting to pair with device at {pair_command} using ADB.")
    print()

    try:
        subprocess.run(['adb', 'pair', pair_command], check=True)
        loggers["network"].info(
            f"Successfully paired with device at {ip_address}.")
        return True, ip_address
    except subprocess.CalledProcessError as e:
        loggers["network"].error(
            f"Error pairing with device at {ip_address}: {e}")
        return False, None


def connect_to_device(ip_address):
    """Connect to the device using ADB after pairing."""

    # Start of setup
    print("\n" + "="*50)
    print("WearOS smartwatch Connection Setup")
    print("="*50)
    loggers["network"].info(
        "Initiating connection process with WearOS smartwatch.")

    # Provide guidance on obtaining the IP address
    print("\n" + "="*80)
    print("How to find the necessary information to connect with WearOS smartwatch")
    print("="*80)
    print("1. On your WearOS smartwatch, go to Settings > Developer Options > Wireless Debugging.")
    print("2. Enter the IP address and port number when prompted.")

    # Prompt for port number with default option
    while True:
        port_input = input(
            "Enter the port number to connect with the smartwatch:\n"
            "(Example: [1-65535])\n> "
        ).strip()

        # Use default port 5555 if input is empty
        if port_input == "":
            port = 5555
            loggers["network"].info(
                "No port entered. Using default port 5555.")
            break
        # Validate and set the port if a valid integer is entered
        elif port_input.isdigit():
            port = int(port_input)
            if is_valid_port(port):
                loggers["network"].info(f"Valid port number entered: {port}")
                break
            else:
                loggers["network"].error(
                    "Invalid port number. Please enter a value between 1 and 65535.")
                print("Invalid port number. Please enter a value between 1 and 65535.")
        else:
            loggers["network"].error(
                "Invalid input for port. Please enter a valid integer.")
            print("Invalid input for port. Please enter a valid integer.")

    try:
        connect_command = f"{ip_address}:{port}"
        loggers["network"].info(
            f"Attempting to connect to device at {connect_command} using ADB.\n")

        # subprocess.run(['adb', 'connect', connect_command], check=True)
        result = run_command(['adb', 'connect', connect_command])
        if result:
            loggers["network"].info(
            f"Successfully connected to device at {ip_address}.\n")
            return True  # Return success
        else:
            loggers["network"].error(
            f"Error connecting to device at {ip_address}")
            return False  # Return failure
    except subprocess.CalledProcessError as e:
        loggers["network"].error(
            f"Error connecting to device at {ip_address}: {e}")
        return False  # Return failure


def get_default_gateway():
    """Retrieve the default gateway for the device."""
    try:
        # result = subprocess.run(
        #     ['ip', 'route'], capture_output=True, text=True, check=True
        # )
        result = run_command(['ip', 'route'])
        for line in result.splitlines():
            if 'default' in line:
                # The third field is the default gateway IP
                default_gateway = line.split()[2]
                return default_gateway
            else:
                loggers["network"].error(f"Error retrieving default gateway")
                return None
    except subprocess.CalledProcessError as e:
        loggers["network"].error(f"Error retrieving default gateway: {e}")
    return None


def verify_network_devices(current_device_ip, watch_ip, network_interface):
    """Ensure the smartwatch and the default gateway are present on the network."""
    print("\n" + "="*40)
    print("Verifying Network Devices")
    print("="*40)
    loggers["network"].info("Starting network verification process.")

    # Step 1: Loading indication
    print("\nLoading network scan process...")
    print("Please wait while we perform the network scan.\n")
    # time.sleep(10)  # Simulate waiting for scan

    # Step 2: Scan for the smartwatch on the network
    scan_network(network_interface, watch_ip)

    # Step 3: Get the default gateway for arp scan and log it
    default_gateway = get_default_gateway()
    if default_gateway:
        loggers["network"].info(
            f"Default gateway set on interface '{network_interface}': {default_gateway}")

    if not default_gateway:
        return False  # Return False if default gateway isn't found

    # Step 4: Final message
    print("")
    loggers["network"].info("Network devices verification completed successfully.")
    return True


def get_physical_device_name():
    """Get the device name of the physical device."""
    try:
        # Run the adb command to get the device name
        # output = subprocess.check_output(
        #     ["adb", "shell", "getprop", "ro.product.model"], text=True
        # )
        output = run_command(["adb", "shell", "getprop", "ro.product.model"])
        if output.strip():
            loggers["acquisition"].info(f"Successfully retrieved device name: {output.strip()}")
        return output.strip()
    except subprocess.CalledProcessError as e:
        loggers["acquisition"].error(f"Failed to get device name: {e}")
        return "Unknown Device"


def disconnect_all_devices():
    """Disconnect all ADB devices."""
    try:
        subprocess.run(['adb', 'disconnect'], check=True)
        loggers["network"].info("All ADB devices have been disconnected.\n")
    except subprocess.CalledProcessError as e:
        loggers["network"].error(f"Error disconnecting ADB devices: {e}\n")


def is_valid_port(port):
    """Validate that the port number is an integer within the valid range."""
    return isinstance(port, int) and 1 <= port <= 65535


def check_adb_devices():
    """Check for connected ADB devices and return a list of device identifiers."""
    try:
        result = subprocess.run(
            ['adb', 'devices'], capture_output=True, text=True, check=True)
        devices = []

        # Parse output to get device identifiers
        for line in result.stdout.splitlines():
            if '\tdevice' in line:
                device_id = line.split()[0]
                devices.append(device_id)

        return devices

    except subprocess.CalledProcessError as e:
        loggers["network"].error(f"Error checking ADB devices: {e}")
        return []


def load_network_enforcement_setting():
    """Load network enforcement setting from user_settings.json."""
    settings_file = USER_SETTING
    try:
        with open(settings_file, "r") as file:
            settings = json.load(file)
            # Default to "disable" if not specified
            return settings.get("network_enforcement", "disable")
    except (FileNotFoundError, json.JSONDecodeError) as e:
        loggers["network"].error(f"Error loading user settings: {e}")
        default_settings = {"network_enforcement": "disable"}
        with open(settings_file, 'w') as file:
            json.dump(default_settings, file, indent=4)
            print(f"{settings_file} created with default settings.")
        return "disable"


def get_network_ip_cidr(interface):
    """Retrieve the network IP in CIDR notation for a given wireless interface."""
    try:
        # Run the 'ip' command to get interface details
        # result = subprocess.run(
        #     ['ip', 'addr', 'show', interface],
        #     capture_output=True,
        #     text=True,
        #     check=True
        # )
        result = run_command(['ip', 'addr', 'show', interface])
        # Extract IP address and subnet mask in CIDR format (e.g., '192.168.1.5/24')
        match = re.search(r'inet (\d+\.\d+\.\d+\.\d+/\d+)', result)

        if match:
            # Get the IP address in CIDR format
            ip_cidr = match.group(1)

            # Convert to network address (network IP)
            network = ipaddress.ip_network(ip_cidr, strict=False)
            network_ip_cidr = str(network)

            return network_ip_cidr
        else:
            loggers["network"].error("No IP address found for interface.")
            return "192.168.0.0/24"  # Default fallback subnet

    except subprocess.CalledProcessError as e:
        loggers["network"].error(
            f"Error retrieving network IP and subnet for {interface}: {e}")
        return "192.168.0.0/24"  # Default fallback subnet


def detect_devices(ip_range, smartwatch_ip):
    """Detect devices on the network using python-netdiscover."""
    # Initialize a dictionary to store devices by IP address
    previous_device_ips = {}  # Dictionary to store IPs and their connection status
    # Initialize previous enforcement setting
    previous_enforcement_setting = load_network_enforcement_setting()

    while True:
        try:
            # Load the most up-to-date enforcement setting
            current_enforcement_setting = load_network_enforcement_setting()

            # Check if enforcement setting has changed
            if current_enforcement_setting != previous_enforcement_setting:
                loggers["network"].info(
                    f"Network enforcement setting changed to: {current_enforcement_setting}")
                previous_enforcement_setting = current_enforcement_setting  # Update to new setting

            # Initialize the network scanner
            disc = Discover()

            # Perform the network scan
            devices = disc.scan(ip_range=ip_range)

            # Extract IP addresses of detected devices
            ip_addresses = [device['ip'] for device in devices]
            current_device_count = len(ip_addresses)

            # Allowed IPs: smartwatch and default gateway
            def_gateway = get_default_gateway()
            allowed_ips = {smartwatch_ip, def_gateway}

            # Check for any other devices on the network
            for ip in ip_addresses:
                if ip not in allowed_ips:
                    if ip not in previous_device_ips:
                        # If enforcement is disabled, log new devices and add them to dictionary
                        if current_enforcement_setting == "disable":
                            loggers["network"].info(
                                f"New device connected with IP: {ip}. Network enforcement is disabled.")
                            # Mark device as detected
                            previous_device_ips[ip] = True
                    elif current_enforcement_setting == "enable":
                        # If enforcement is enabled and the device is not allowed, abort the script
                        loggers["network"].error(
                            f"Unauthorized device detected: {ip}. Aborting script...")
                        exit_program()
                        os._exit(0)  # Kill the script

            # Log changes in device count if the device list has changed
            if set(ip_addresses) != set(previous_device_ips.keys()):
                loggers["network"].info(
                    f"Devices detected: {current_device_count}")
                # Update to current list of IPs
                previous_device_ips = {ip: True for ip in ip_addresses}

            # If enforcement is enabled, check the device count limit
            if current_enforcement_setting == "enable" and current_device_count > 2:
                loggers["network"].error(
                    "More than 2 devices detected. Network enforcement enabled. Aborting script..."
                )
                exit_program()
                os._exit(0)  # Kill the script

        except Exception as e:
            loggers["network"].error(
                f"Unexpected error in device detection: {e}")
            exit_program()


#one time only when running
# def scan_network(network_interface, smartwatch_ip):
#     """Scan the network for connected devices and enforce network rules."""
#     previous_enforcement_setting = load_network_enforcement_setting(
#     )  # Store the initial enforcement setting
#     previous_device_ips = {}
#     try:
#         # Load the most up-to-date enforcement setting
#         current_enforcement_setting = load_network_enforcement_setting()

#         # Check if the enforcement setting has changed
#         if current_enforcement_setting != previous_enforcement_setting:
#             loggers["network"].info(
#                 f"Network enforcement setting changed to: {current_enforcement_setting}")
#             # Update the previous setting
#             previous_enforcement_setting = current_enforcement_setting

#         # Initialize the network scanner
#         # disc = Discover()

#         # Retrieve the IP range for the specified network interface
#         ip_range = get_network_ip_cidr(network_interface)
#         loggers["network"].info(f"Scanning IP range: {ip_range}")

#         # Perform the network scan
#         # devices = disc.scan(ip_range=ip_range)
#         devices = run_netdiscover(network_interface, ip_range, 30)

#         # Extract IP addresses of detected devices
#         ip_addresses = [device[0] for device in devices]
#         # print(ip_addresses)
#         # vendor_names = [device[2] for device in devices]
#         current_device_count = len(ip_addresses)
#         # loggers["network"].info(f"Number of devices: {current_device_count}")
#         # loggers["network"].info(f"Devices detected: {ip_addresses}")

#         # Allowed IPs: smartwatch, and default gateway
#         def_gateway = get_default_gateway()
#         allowed_ips = {smartwatch_ip, def_gateway}

#         # Check for any other devices on the network
#         for ip in ip_addresses:
#             if ip not in allowed_ips:
#                 if ip not in previous_device_ips:
#                     # If enforcement is disabled, log new devices and add them to dictionary
#                     if current_enforcement_setting == "disable":
#                         loggers["network"].info(
#                             f"Unknown device connected with IP: {ip}. Network enforcement is disabled.")
#                         # Mark device as detected
#                         previous_device_ips[ip] = True
#                 elif current_enforcement_setting == "enable":
#                     # If enforcement is enabled and the device is not allowed, abort the script
#                     loggers["network"].error(
#                         f"Unauthorized device detected: {ip}. Aborting script...")
#                     exit_program()
#                     os._exit(0)  # Kill the script

#         # Log changes in device count if the device list has changed
#         if len(ip_addresses) != current_device_count:
#             loggers["network"].info(
#                 f"Devices detected: {current_device_count}")

#         # Check if more than 2 devices are detected and enforcement is enabled
#         if current_enforcement_setting == "enable" and current_device_count > 2:
#             loggers["network"].error(
#                 "More than 2 devices detected. Network enforcement enabled. Aborting script..."
#             )
#             exit_program()
#             os._exit(0)  # Kill the script
#         elif current_device_count <= 2:
#             loggers["network"].info(
#                 "No additional devices detected. Continuing..."
#             )

#         # Log the enforcement setting status
#         if current_enforcement_setting == "disable":
#             loggers["network"].info(
#                 "Network enforcement is disabled. Continuing to log devices.")

#     except Exception as e:
#         loggers["network"].error(f"Unexpected error in network scanning: {e}")
#         exit_program()

def update_user_settings(enforcement_setting):
    """Update the user_settings.json file with the new enforcement setting."""
    try:
        with open(USER_SETTING, 'r') as f:
            user_settings = json.load(f)

        # Update the network_enforcement setting
        user_settings["network_enforcement"] = enforcement_setting

        with open(USER_SETTING, 'w') as f:
            json.dump(user_settings, f, indent=4)

        loggers["network"].info(f"User settings updated: network_enforcement = {enforcement_setting}")

    except Exception as e:
        loggers["network"].error(f"Error updating user settings: {e}")

def scan_network(network_interface, smartwatch_ip):
    """Scan the network for connected devices and enforce network rules."""
    # Set initial network enforcement setting to 'disable' for first-time users
    current_enforcement_setting = "disable"

    try:
        # Initialize the network scanner
        # disc = Discover()

        # Retrieve the IP range for the specified network interface
        ip_range = get_network_ip_cidr(network_interface)
        loggers["network"].info(f"Scanning IP range: {ip_range}")

        # Perform the network scan
        # devices = disc.scan(ip_range=ip_range)
        devices = run_netdiscover(network_interface, ip_range, 30)

        # Extract IP addresses of detected devices
        ip_addresses = [device[0] for device in devices]
        current_device_count = len(ip_addresses)

        # Allowed IPs: smartwatch, and default gateway
        def_gateway = get_default_gateway()
        allowed_ips = {smartwatch_ip, def_gateway}

        # Variable to track if unauthorized devices are found
        unauthorized_devices = []

        # Check for any other devices on the network
        for ip in ip_addresses:
            if ip not in allowed_ips:
                # Track unauthorized devices
                unauthorized_devices.append(ip)

        # Log changes in device count if the device list has changed
        if len(ip_addresses) != current_device_count:
            loggers["network"].info(
                f"Devices detected: {current_device_count}")

        # If there are unauthorized devices and enforcement is enabled, ask user for input
        if unauthorized_devices:
            loggers["network"].info(f"Unauthorized devices detected: {unauthorized_devices}")
            user_input = input("Extra devices detected. Leave empty to continue, or type 'no' to abort: ").strip().lower()
            if user_input == "no":
                loggers["network"].info("User aborted due to unauthorized devices.")
                exit_program()
                os._exit(0)  # Kill the script
            else:
                # If the user chooses to continue, set enforcement to 'disable'
                current_enforcement_setting = "disable"
                loggers["network"].info("User chose to continue. Setting network enforcement to 'disable'.")

        # Check if more than 2 devices are detected and enforcement is enabled
        if current_enforcement_setting == "enable" and current_device_count > 2:
            loggers["network"].error(
                "More than 2 devices detected. Network enforcement enabled. Aborting script..."
            )
            exit_program()
            os._exit(0)  # Kill the script
        elif current_device_count <= 2:
            loggers["network"].info(
                "No additional devices detected. Continuing..."
            )

        # If no unauthorized devices and the enforcement is not triggered, ask user to enable/disable enforcement
        if not unauthorized_devices:
            user_input = input(f"Network enforcement is currently '{current_enforcement_setting}'. Do you want to enable or disable it? (leave empty to continue): ").strip().lower()
            if user_input == "enable":
                current_enforcement_setting = "enable"
                loggers["network"].info("Network enforcement enabled.")
            elif user_input == "disable":
                current_enforcement_setting = "disable"
                loggers["network"].info("Network enforcement disabled.")

        # Update the user settings in the JSON file based on user's choice
        update_user_settings(current_enforcement_setting)

        # Log the enforcement setting status
        if current_enforcement_setting == "disable":
            loggers["network"].info(
                "Network enforcement is disabled. Continuing to log devices.")

    except Exception as e:
        loggers["network"].error(f"Unexpected error in network scanning: {e}")
        exit_program()
