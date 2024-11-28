import re
import subprocess
import os
import ipaddress
import json
import time

from prettytable import PrettyTable # type: ignore
from netdiscover import *  # type: ignore
from app.logs.logger_config import initialize_loggers
from app.setup.choices import exit_program, check_for_given_file
from app.setup.settings import *
from app.preacquisition.run_netdiscover import *
from app.setup.setup_environment import *
from app.setup.choices import *

from app.setup import (
    settings
)

# Initialize all loggers
loggers = initialize_loggers()

def validate_input():
    """Ask the user whether to continue or abort the script after vulnerability detection."""
    while True:
        user_input = input("\nRouter is vulnerable. Do you want to continue? (Press Enter to continue, type 'no' to abort):\n> ").strip().lower()
        if user_input == '' or user_input == 'no':
            return user_input
        else:
            loggers["network"].warning("Invalid input. Please type 'no' to abort or press Enter to continue.")


def run_network_command(command):
    """Function to run system commands with error handling"""
    try:
        result = subprocess.run(command, check=True, text=True, capture_output=True)
        loggers["network"].info(f"Command succeeded: {' '.join(command)}")
        return result.stdout  # Return the output if the command completed successfully

    except subprocess.CalledProcessError as e:
        loggers["network"].error(f"Error while running command: {' '.join(command)}, error: {e.stderr}")
        return False  # Return False if an exception was raised


def realtime_run_network_command(command):
    """Function to run system commands with real-time output and error handling"""
    try:
        # Use subprocess.Popen to allow real-time output
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        # Create a variable to store the real-time output
        real_time_output = ""

        # Print the output in real-time and capture it
        for line in process.stdout:
            print(line, end='')  # Print each line of output as it is generated
            real_time_output += line  # Capture the output for later use

        # Capture stderr if there's an error
        stderr = process.stderr.read()
        if stderr:
            print(stderr, end='')
            real_time_output += stderr  # Capture error output

        # Wait for the process to finish
        process.wait()

        if process.returncode == 0:
            loggers["network"].info(f"Command succeeded: {' '.join(command)}")
            return real_time_output  # Return the captured output as a string
        else:
            loggers["network"].error(f"Command failed: {' '.join(command)}")
            return False

    except Exception as e:
        loggers["network"].error(f"Error while running command: {' '.join(command)}, error: {e}")
        return False


def nmap_scan_for_vulnerabilities(ip_address):
    """Scan the IP address for vulnerabilities using nmap and save output to a file."""
    try:
        # Ensure the output directory exists
        output_dir = "output/network"
        os.makedirs(output_dir, exist_ok=True)
        output_file_path = os.path.join(output_dir, "router_vulnerabilities.txt")
        
        # Run nmap with common vulnerability scripts
        command = [
            "nmap", "-A", "-sV", "--script", "vuln,discovery,firewall-bypass,default", "-p-", "--reason", "--osscan-guess", "--traceroute", ip_address
        ]
        
        # Attempt to run the command and allow keyboard interruption
        try:
            result = realtime_run_network_command(command)
        except KeyboardInterrupt:
            loggers["network"].warning("Nmap scan interrupted by user.\n")
            return False
        
        # If the process completed successfully
        if result:
            # Write the result to the output file
            with open(output_file_path, "w") as file:
                file.write(result)
            
            # Check if vulnerabilities were found and if "CVE" is in the result
            if "VULNERABLE" in result or "CVE" in result:
                
                # Print table after the command succeeded log
                table = PrettyTable()
                table.field_names = ["Router IP", "Vulnerabilities Found"]
                table.add_row([ip_address, "Yes"])
                loggers["network"].info(f"Router Information:\n\n{table}\n")
                
                loggers["network"].warning("[VULNERABLE ROUTER] Vulnerabilities detected in nmap scan. Output at output/network/router_vulnerabilities.txt")

                # Validate user input before continuing
                user_choice = validate_input()
                if user_choice == 'no':
                    loggers["network"].info(f"\nUser aborted due to router vulnerabilities.")
                    exit_program()
                    os._exit(0)
                return True
            else:
                # Print table after the command succeeded log
                table = PrettyTable()
                table.field_names = ["Router IP", "Vulnerabilities Found"]
                table.add_row([ip_address, "No"])
                loggers["network"].info(f"Router Information:\n\n{table}\n")

                loggers["network"].info("\nNo vulnerabilities detected in nmap scan.")
                return False
        else:
            loggers["network"].error("Nmap scan failed or returned no output.")
            return False
    except Exception as e:
        loggers["network"].error(f"Error during nmap scan: {e}")
        return False


def check_router_vulnerabilities(router_ip):
    """Check the router for vulnerabilities using nmap."""
    # Run an nmap vulnerability scan on the router
    if nmap_scan_for_vulnerabilities(router_ip):
        loggers["network"].warning("Vulnerabilities detected in the router.")
    else:
        loggers["network"].info("No vulnerabilities detected in the router.")


def get_current_network_essid(interface):
    """Retrieve the ESSID of the currently connected wireless network."""
    essid = run_network_command(['iwgetid', '-r', interface]).strip()
    if essid is None:
        loggers["network"](
            f"Error retrieving current ESSID for interface {interface}")
    return essid


def get_wifi_networks(interface='wlan0'):
    """Uses iwlist to scan for WiFi networks and returns structured information."""
    try:
        # Run iwlist scan commands
        scan_result = run_network_command(
            ['sudo', 'iwlist', interface, 'scan'])
        # loggers["network"].debug(f"iwlist scan output:\n{scan_result}")
        return parse_iwlist_output(scan_result)
    except subprocess.CalledProcessError as e:
        loggers["network"].warning(f"Error: {e}")
        return []


def parse_iwlist_output(output):
    """Parses the output of iwlist scan command."""
    networks = []
    network_info = {}

    # Regular expressions for extracting WiFi data
    regex_patterns = {
        'Cell': re.compile(r'Cell \d+ - Address: ([\dA-F:]{17})'),
        'ESSID': re.compile(r'ESSID:"([^"]*)"'),
        'Frequency': re.compile(r'Frequency:(\d+\.\d+)'),
        'Signal level': re.compile(r'Signal level=(-?\d+) dBm'),
        'Quality': re.compile(r'Quality=(\d+)/(\d+)'),
        'Encryption key': re.compile(r'Encryption key:(on|off)'),
        'Channel': re.compile(r'Channel:(\d+)'),
        'Mode': re.compile(r'Mode:(\w+)'),
        'Bit Rates': re.compile(r'Bit Rates:(.+)'),
        'Encryption type': re.compile(r'IE: IEEE 802.11i/WPA2 Version 1|IE: WPA Version 1|IE: WPA Version 2')
    }

    # Split output line by line
    for line in output.splitlines():
        line = line.strip()

        if regex_patterns['Cell'].search(line):
            # Save the previous network info if it exists
            if network_info:
                networks.append(network_info)
            # Start a new network info dictionary
            network_info = {
                'Address': regex_patterns['Cell'].search(line).group(1)}

        # Match each line against known patterns
        for key, pattern in regex_patterns.items():
            match = pattern.search(line)
            if match:
                # Handle multiple matches, like quality or bit rates
                if key == 'Quality':
                    network_info['Quality'] = f"{match.group(1)}/{match.group(2)}"
                elif key == 'Bit Rates':
                    network_info[key] = match.group(1).strip().split(';')
                elif key == 'Encryption key':
                    network_info['Encryption Status'] = 'Enabled' if match.group(
                        1) == 'on' else 'Disabled'
                elif key == 'Encryption type':
                    network_info['Encryption Type'] = "WPA2" if "WPA2" in match.group(
                        0) else "WPA"
                else:
                    network_info[key] = match.group(1)

    # Add the last parsed network
    if network_info:
        networks.append(network_info)

    return networks


def iwlist_security_check(interface, current_network):
    """Use iwlist to check Wi-Fi protocol and encryption key status."""
    try:
        loggers["network"].info(
            f"Starting Wi-Fi security check on interface '{interface}' for network '{current_network}'.")

        # Get WiFi networks using the new function
        networks = get_wifi_networks(interface)

        secure_network_found = False
        encryption_type = "Unknown"
        encryption_status = "Insecure"  # Initialize encryption_status as insecure

        # Prepare table for displaying results
        table = PrettyTable()
        table.field_names = [
            "Network (ESSID)", "MAC Address", "Encryption", "Security Status"]

        # Process each network
        for network in networks:
            essid = network.get("ESSID", "")

            # Process only if the ESSID matches the current network
            if essid == current_network:
                encryption_status = network.get(
                    "Encryption Status", "Disabled")
                encryption_type = network.get("Encryption Type", "None")

                if encryption_status == "Enabled" and encryption_type in {"WPA", "WPA2", "WPA3"}:
                    secure_network_found = True
                    security_status = "Secure"
                    loggers["network"].info(
                        f"Network '{essid}' is secure with {encryption_type} encryption."
                    )
                else:
                    security_status = "Insecure"
                    loggers["network"].error(
                        f"Network '{essid}' is detected, but encryption is off or unknown. Connection is insecure."
                    )

                mac = network.get("Address")
                if not mac:
                    loggers["network"].error(f"MAC Address not found.")
                    return False
                
                # Add results to the table
                table.add_row([essid, mac, encryption_type, security_status])
                break  # Stop once the desired network is verified

        # If no matching secure network is found, add a single "Insecure" row at the end
        if not secure_network_found:
            loggers["network"].error(
                f"Current network '{current_network}' not found in scan results OR is not secure.")

        # Output to console
        print(f"\n{'='*50}\nCurrent Wi-Fi Security Check Results\n{'='*50}")
        loggers["network"].info("Current Wi-Fi Security Check Results")
        loggers["network"].info(f"Current Wi-Fi Information:\n\n{table}\n")  # This prints the table directly

        # Output table to file
        upload_dir = settings.NETWORK_DIR
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)
            loggers["network"].debug(f"Created directory: {upload_dir}")

        output_file = os.path.join(upload_dir, "current_wifi.txt")
        with open(output_file, "w") as file:
            file.write(f"{'='*50}\nCurrent Wifi\n{'='*50}\n\n")
            file.write(str(table))  # Directly write the table to file

        loggers["network"].info(
            f"Current Wi-Fi security check results saved to '{output_file}'.")
        return secure_network_found

    except Exception as e:
        loggers["network"].error(
            f"Error during current Wi-Fi scan on interface '{interface}': {e}")
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
    print("\nHow to find the necessary information to pair with WearOS smartwatch")
    print("1. On your WearOS smartwatch, go to Settings > Developer Options > Wireless Debugging.")
    print("2. Connect to a Wi-Fi network if not already connected.")
    print("3. Click 'Pair new device'.")
    print("4. Enter the IP address and port number when prompted.")

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
        else:
            loggers["network"].error(
                "Invalid input for port. Please enter a valid integer.")

    # Attempting pairing using adb
    pair_command = f"{ip_address}:{port}"
    loggers["network"].info(f"Attempting to pair with device at {pair_command} using ADB.\n")

    try:
        subprocess.run(['adb', 'pair', pair_command], check=True)
        print()
        loggers["network"].info(f"Successfully paired with device at {ip_address}.")
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
    print("\nHow to find the necessary information to connect with WearOS smartwatch")
    print("1. On your WearOS smartwatch, go to Settings > Developer Options > Wireless Debugging.")
    print("2. Enter the IP address and port number when prompted.")

    while True:
        # Prompt for port number with default option
        port_input = input(
            "\nEnter the port number to connect with the smartwatch:\n"
            "(Example: [1-65535])\n> "
        ).strip()

        # Use default port 5555 if input is empty
        if port_input == "":
            port = 5555
            loggers["network"].info("No port entered. Using default port 5555.")
        # Validate and set the port if a valid integer is entered
        elif port_input.isdigit():
            port = int(port_input)
            if is_valid_port(port):
                loggers["network"].info(f"Valid port number entered: {port}")
            else:
                loggers["network"].error("Invalid port number. Please enter a value between 1 and 65535.")
                continue
        else:
            loggers["network"].error("Invalid input for port. Please enter a valid integer.")
            continue

        try:
            connect_command = f"{ip_address}:{port}"
            loggers["network"].info(f"Attempting to connect to device at {connect_command} using ADB.")
            result = run_network_command(['adb', 'connect', connect_command])

            # Check if any ADB devices are connected
            connected_devices = check_adb_devices()
            if connected_devices:
                # Run the adb connect command
                return True
                # if result:
                    # loggers["network"].info(f"Successfully connected to device at {ip_address}.")
            else:
                loggers["network"].error(f"Error connecting to device at {ip_address}")

        except subprocess.CalledProcessError as e:
            loggers["network"].error(f"Error connecting to device at {ip_address}: {e}")

        # Re-prompt for port if connection or device detection failed
        print("\nReattempting connection setup...")


def get_default_gateway():
    """Retrieve the default gateway for the device."""
    try:
        result = subprocess.run(
            ['ip', 'route'], capture_output=True, text=True, check=True
        )
        # result = run_network_command(['ip', 'route'])
        for line in result.stdout.splitlines():
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
    loggers["network"].info("Please wait while we perform the network scan...\n")
    # time.sleep(10)  # Simulate waiting for scan

    # Step 2: Scan for the smartwatch on the network
    scan_network(network_interface, watch_ip)

    # Step 3: Get the default gateway for arp scan and log it
    default_gateway = get_default_gateway()

    if not default_gateway:
        return False  # Return False if default gateway isn't found

    # Step 4: Final message
    print()
    loggers["network"].info("Network devices verification completed successfully.")
    return True


def get_physical_device_name():
    """Get the device name of the physical device."""
    try:
        # Run the adb command to get the device name
        # output = subprocess.check_output(
        #     ["adb", "shell", "getprop", "ro.product.model"], text=True
        # )
        output = run_network_command(
            ["adb", "shell", "getprop", "ro.product.model"])
        if output:
            loggers["network"].info(
                f"Successfully retrieved device name: {output.strip()}")
            return output.strip()
        else:
            return False
    except subprocess.CalledProcessError as e:
        loggers["network"].error(f"Failed to get device name: {e}")
        return False


def disconnect_all_devices():
    """Disconnect all ADB devices."""
    try:
        subprocess.run(['adb', 'disconnect'], check=True)
        loggers["network"].info("All ADB devices have been disconnected.")
    except subprocess.CalledProcessError as e:
        loggers["network"].error(f"Error disconnecting ADB devices: {e}")


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


# def load_network_enforcement_setting():
    # """Load network enforcement setting from user_settings.json."""
    # settings_file = USER_SETTING
    # try:
    #     with open(settings_file, "r") as file:
    #         settings = json.load(file)
    #         # Default to "disable" if not specified
    #         return settings.get("network_enforcement", "disable")
    # except (FileNotFoundError, json.JSONDecodeError) as e:
    #     loggers["network"].error(f"Error loading user settings: {e}")
    #     default_settings = {"network_enforcement": "disable"}
    #     with open(settings_file, 'w') as file:
    #         json.dump(default_settings, file, indent=4)
    #         print(f"{settings_file} created with default settings.")
    #     return "disable"


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
        result = run_network_command(['ip', 'addr', 'show', interface])
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


def detect_devices(ip_range, smartwatch_ip, network_interface):
    """
    Continuously monitor the network for unauthorized devices and enforce network rules.
    """
    previous_enforcement_setting = load_user_settings().get("network_enforcement")
    def_gateway = get_default_gateway()
    allowed_ips = [smartwatch_ip, def_gateway]
    while True:
        try:
            # Load the latest enforcement setting
            time.sleep(1)
            current_enforcement_setting = load_user_settings().get("network_enforcement")

            # Log if the enforcement setting has changed
            if current_enforcement_setting != previous_enforcement_setting:
                loggers["network"].info(
                    f"Network enforcement setting changed to: {current_enforcement_setting}")
                previous_enforcement_setting = current_enforcement_setting

            if current_enforcement_setting == "disable":
                continue
            
            # Perform a network scan
            devices = run_netdiscover(network_interface, ip_range, 10)
            ip_addresses = {device[0] for device in devices}
            current_device_count = len(ip_addresses)
            unauthorized_devices = []

            #one liner for unauthorized devices
            # unauthorized_devices = [(ip, mac, vendor_name) for ip, mac, vendor_name in [(device[0], device[1], ' '.join(device[2].strip().split()[2:])) for device in devices] if ip not in allowed_ips]

            for device in devices:
                ip, mac, vendor = device[0], device[1], device[2].strip()  # Remove any leading/trailing whitespace
                # Extract only the vendor name after any unnecessary numbers or whitespace
                vendor_name = ' '.join(vendor.split()[2:])  # Assuming vendor name starts after first two entries
                if ip not in allowed_ips:
                    # Track unauthorized devices
                    unauthorized_devices.append((ip, mac, vendor_name))

            # Log any unauthorized devices detected
            if unauthorized_devices and current_enforcement_setting == "enable":
                for device in unauthorized_devices:
                    loggers["network"].error(
                        f"[UNKNOWN] Unauthorized Device Detected - IP: {device[0]}, MAC: {device[1]}, Vendor: {device[2]}")
                exit_program()
                os._exit(0)  # Terminate the script immediately
                
            # Log any change in the number of detected devices
            # if detectted_device_ips != ip_addresses:
            #     loggers["network"].info(
            #         f"Device count changed: {current_device_count} devices detected.")
            #     detected_device_ips = ip_addresses

            # Check device count limit if enforcement is enabled
            if current_enforcement_setting == "enable" and current_device_count > 2:
                loggers["network"].error(
                    "More than 2 devices detected. Enforcement enabled; aborting...")
                exit_program()
                os._exit(0)  # Terminate the script

            # Brief pause between scans
            # time.sleep(30)

        except Exception as e:
            loggers["network"].error(
                f"Unexpected error in device detection: {e}")
            exit_program()


def update_user_settings(enforcement_setting):
    """Update the user_settings.json file with the new enforcement setting."""
    try:
        with open(USER_SETTING, 'r') as f:
            user_settings = json.load(f)

        # Update the network_enforcement setting
        user_settings["network_enforcement"] = enforcement_setting

        with open(USER_SETTING, 'w') as f:
            json.dump(user_settings, f, indent=4)

        print()
        loggers["network"].info(
            f"User settings updated: network_enforcement = {enforcement_setting}")

    except Exception as e:
        loggers["network"].error(f"Error updating user settings: {e}")


def scan_network(network_interface, smartwatch_ip):
    """
    Scan the network for connected devices and enforce network rules 
    when connecting for the first time
    """

    # Set initial network enforcement setting to 'disable' for first-time users
    current_enforcement_setting = "disable"
    timeout = 30
    try:
        # Retrieve the IP range for the specified network interface
        ip_range = get_network_ip_cidr(network_interface)
        loggers["network"].info(f"Scanning IP range: {ip_range}")

        print()

        # Perform the network scan and retrieve details of each device
        devices = run_netdiscover(network_interface, ip_range, timeout)
        loggers["network"].info(f"Running netdiscover on interface '{network_interface}' for network '{ip_range}'")

        # Allowed IPs with labels: smartwatch and default gateway
        def_gateway = get_default_gateway()
        allowed_ips = {smartwatch_ip: "[smartwatch]", def_gateway: "[default gateway]"}
        
        # Variable to track if unauthorized devices are found
        unauthorized_devices = []

        # Initialize PrettyTable
        table = PrettyTable()
        table.field_names = ["IP Address", "Label", "MAC Address", "Vendor"]

        # Log the total number of detected devices
        current_device_count = len(devices)
        
        # Check each detected device for authorization
        for device in devices:
            ip, mac, vendor = device[0], device[1], device[2].strip()  # Remove any leading/trailing whitespace
            # Extract only the vendor name after any unnecessary numbers or whitespace
            vendor_name = ' '.join(vendor.split()[2:])  # Assuming vendor name starts after first two entries
            
            # Check if IP is in allowed IPs, and if so, add the label
            label = allowed_ips.get(ip, "[Unknown]")  # Defaults to "[Unknown]" if not in allowed_ips
            table.add_row([ip, label, mac, vendor_name])  # Add the device details to the table

            if ip in allowed_ips:
                loggers["network"].info(f"Detected Device - IP: {ip} {label}, MAC: {mac}, Vendor: {vendor_name}")

            if ip not in allowed_ips:
                # Track unauthorized devices
                unauthorized_devices.append((ip, mac, vendor_name))
                loggers["network"].info(
                    f"Detected Device - IP: {ip} [Unknown], MAC: {mac}, Vendor: {vendor_name}")

        # Display the table of detected devices
        loggers["network"].info(f"Detected Devices:\n\n{table}\n")

        # If unauthorized devices are found, prompt user if enforcement is enabled
        if unauthorized_devices:
            unauthorized_ips = [ip for ip, _, _ in unauthorized_devices]
            loggers["network"].warning(f"[UNKNOWN] Unauthorized devices detected: {unauthorized_ips}")
            
            user_input = get_valid_input(
                "Extra devices detected. Leave empty to DISABLE, or type 'no' to abort:\n> ",
                valid_choices=["", "no"],
                allow_empty=True
            )
            if user_input == "no":
                loggers["network"].info(
                    "\nUser aborted due to unauthorized devices.")
                exit_program()
                os._exit(0)  # Kill the script
            else:
                # If the user chooses to continue, set enforcement to 'disable'
                current_enforcement_setting = "disable"
                loggers["network"].info(
                    "User chose to continue. Setting network enforcement to 'disable'.")

        # Check if more than 2 devices are detected and enforcement is enabled
        if current_enforcement_setting == "enable" and current_device_count > 2:
            loggers["network"].error(
                "More than 2 devices detected. Network enforcement enabled. Aborting script..."
            )
            exit_program()
            os._exit(0)  # Kill the script
        elif current_device_count <= 2:
            loggers["network"].info(
                "No additional devices detected. Continuing...")

        # If no unauthorized devices and the enforcement is not triggered, ask user to enable/disable enforcement
        if not unauthorized_devices:
            user_input = get_valid_input(
                f"Network enforcement is currently '{current_enforcement_setting}'. Do you want to enable or disable it? (leave empty to disable):\n> ",
                valid_choices=["", "enable", "disable"],
                allow_empty=True
            )
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
                "Network enforcement is disabled.")

    except Exception as e:
        loggers["network"].error(f"Unexpected error in network scanning: {e}")
        exit_program()

def get_valid_input(prompt, valid_choices, allow_empty=True):
    """Helper function to get a valid user input from a set of valid choices."""
    while True:
        user_input = input(prompt).strip().lower()
        if user_input == "" and allow_empty:
            return ""  # Return empty string if empty input is allowed
        elif user_input in valid_choices:
            return user_input
        else:
            loggers["network"].warning(f"Invalid input. Please choose from {valid_choices}.")