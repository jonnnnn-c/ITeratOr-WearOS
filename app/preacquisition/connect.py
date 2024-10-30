import re
import subprocess
import time
import os
from netdiscover import *
from app.logs.logger_config import initialize_loggers
from app.setup.choices import exit_program

# Initialize all loggers
loggers = initialize_loggers()

def get_physical_device_name():
    """Get the device name of the physical device."""
    try:
        # Run the adb command to get the device name
        output = subprocess.check_output(
            ["adb", "shell", "getprop", "ro.product.model"], text=True
        )
        return output.strip()  # Remove any surrounding whitespace/newlines
    except subprocess.CalledProcessError as e:
        loggers["preacquisition"].error(f"Failed to get device name: {e}")
        return "Unknown Device"

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

def get_current_network(interface):
    """Retrieve the ESSID of the currently connected wireless network."""
    try:
        result = subprocess.run(['iwgetid', interface], capture_output=True, text=True, check=True)
        essid = result.stdout.strip()
        return essid if essid else None
    except subprocess.CalledProcessError as e:
        loggers["network"].error(f"Error retrieving current network: {e}")
    return None

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
        firmware_version_pattern = r'(?i)firmware.*?(\d+\.\d+\.\d+|\d+)'  # Adjust regex as needed
        match = re.search(firmware_version_pattern, output)

        if match:
            loggers["network"].info(f"Router firmware version found: {match.group(0)}")
            return match.group(0)  # Return the firmware version
        else:
            loggers["network"].error("Firmware version not found in the router's webpage.")
            return None

    except subprocess.CalledProcessError as e:
        loggers["network"].error(f"Error fetching router page: {e}")
        return None

def pair_device():
    """Prompt for IP address, port to pair the device using ADB."""
    ip_address = input("Enter the IP address of the smartwatch: ")
    
    while True:
        port_input = input("Enter the port number for pairing (1-65535): ")
        if port_input.isdigit():
            port = int(port_input)
            if is_valid_port(port):
                break
            else:
                loggers["preacquisition"].error("Invalid port. Please enter a number between 1 and 65535.")
        else:
            loggers["preacquisition"].error("Invalid input. Please enter a valid integer for the port.")

    try:
        pair_command = f"{ip_address}:{port}"
        subprocess.run(['adb', 'pair', pair_command], check=True)
        loggers["preacquisition"].info(f"Successfully paired with device at {ip_address}.")
        return True, ip_address  # Return success and IP for the next function
    except subprocess.CalledProcessError as e:
        loggers["preacquisition"].error(f"Error pairing with device at {ip_address}: {e}")
        return False, None  # Return failure

def connect_to_device(ip_address):
    """Connect to the device using ADB after pairing."""
    while True:
        port_input = input("Enter the port number for connecting (default is 5555, press Enter to use default): ")
        
        # Set default port if no input is given
        if port_input.strip() == "":
            port = 5555
            loggers["preacquisition"].info("Using default port 5555.")
            break
        elif port_input.isdigit():
            port = int(port_input)
            if is_valid_port(port):
                break
            else:
                loggers["preacquisition"].error("Invalid port. Please enter a number between 1 and 65535.")
        else:
            loggers["preacquisition"].error("Invalid input. Please enter a valid integer for the port.")

    try:
        connect_command = f"{ip_address}:{port}"
        subprocess.run(['adb', 'connect', connect_command], check=True)
        loggers["preacquisition"].info(f"Connected to device at {ip_address}.")
        return True  # Return success
    except subprocess.CalledProcessError as e:
        loggers["preacquisition"].error(f"Error connecting to device at {ip_address}: {e}")
        return False  # Return failure

def iwlist_security_check(interface, current_network):
    """Use iwlist to check Wi-Fi protocol and encryption key status."""
    try:
        result = subprocess.run(['iwlist', interface, 'scan'], capture_output=True, text=True, check=True)

        secure_network_found = False
        current_essid = None
        encryption_type = "None"

        for line in result.stdout.splitlines():
            if "ESSID" in line:
                current_essid = line.split(":")[1].strip().strip('"')
                
                # Skip invalid or empty ESSIDs
                if not current_essid or any(char < ' ' for char in current_essid):
                    continue

            if "Encryption key" in line:
                encryption = line.split(":")[1].strip()
                if encryption == "on":
                    secure_network_found = True

            if "IE: IEEE 802.11i/WPA2" in line:
                encryption_type = "WPA2"
                loggers["network"].info(f"Network: {current_essid}, Encryption: WPA2")
            elif "IE: IEEE 802.11i/WPA" in line:
                encryption_type = "WPA"
                loggers["network"].info(f"Network: {current_essid}, Encryption: WPA")
            elif "IE: WPA3" in line:
                encryption_type = "WPA3"
                loggers["network"].info(f"Network: {current_essid}, Encryption: WPA3")

            if current_essid == current_network and secure_network_found:
                loggers["network"].info(f"Current network {current_network} is secure with {encryption_type} encryption.")
                return True

        if not secure_network_found:
            loggers["network"].error("Current network not found in scan results or is not secure.")
            return False

        return True

    except subprocess.CalledProcessError as e:
        loggers["network"].error(f"Error scanning with iwlist: {e}")
        return False

def check_adb_devices():
    """Check for connected ADB devices and return a list of device identifiers."""
    try:
        result = subprocess.run(['adb', 'devices'], capture_output=True, text=True, check=True)
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


def detect_devices():
    """Detect devices on the network using python-netdiscover."""
    while True:
        try:
            # Initialize the network scanner
            disc = Discover()
            
            # Perform the network scan
            devices = disc.scan(ip_range="192.168.249.0/24")
            
            # Extract IP addresses of detected devices (no need to decode)
            ip_addresses = [device['ip'] for device in devices]
            
            loggers["network"].info(f"Devices detected: {len(ip_addresses)}")
            
            if len(ip_addresses) > 2:  # More than 2 additional devices
                loggers["network"].error("More than 2 devices detected. Aborting script...")
                exit_program()
                os._exit(0)

        except Exception as e:
            loggers["network"].error(f"Unexpected error in device detection: {e}")
            exit_program()
        
        #time.sleep(1)  # Wait before the next scan


def scan_network():
    """Scan the network for connected devices."""
    try:
            # Initialize the network scanner
            disc = Discover()
            
            # Perform the network scan
            devices = disc.scan(ip_range="192.168.249.0/24")
            
            # Extract IP addresses of detected devices (no need to decode)
            ip_addresses = [device['ip'] for device in devices]
            
            loggers["network"].info(f"Devices detected: {len(ip_addresses)}")
            
            if len(ip_addresses) > 2:  # More than 2 additional devices
                loggers["network"].error("More than 2 devices detected. Aborting script...")
                exit_program()
                os._exit(0)
    except Exception as e:
    	loggers["network"].error(f"Unexpected error in device detection: {e}")
    	exit_program()

def get_default_gateway():
    """Retrieve the default gateway for the device."""
    try:
        result = subprocess.run(['ip', 'route'], capture_output=True, text=True, check=True)
        for line in result.stdout.splitlines():
            if 'default' in line:
                return line.split()[2]  # The third field is the default gateway IP
    except subprocess.CalledProcessError as e:
        loggers["network"].error(f"Error retrieving default gateway: {e}")
    return None

def verify_network_devices(current_device_ip, watch_ip):
    """Ensure the current device, smartwatch, and the default gateway are present on the network."""
    time.sleep(15)
    scan_network()
    # Get the default gateway
    default_gateway = get_default_gateway()
    loggers["network"].info(f"Default Gateway: {default_gateway}")
    return True
