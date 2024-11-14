import subprocess
import re

from app.logs.logger_config import initialize_loggers

# Initialize all loggers
loggers = initialize_loggers()

def run_netdiscover(interface, network_ip, timeout=10):
    """
    Runs netdiscover on the given network interface and returns a list of IP, MAC, and Vendor information.
    
    :param interface: Network interface to scan (e.g., wlan0)
    :param network_ip: Network IP range to scan (e.g., 192.168.1.0/24)
    :param timeout: Timeout for the netdiscover command (default: 10 seconds)
    :return: List of tuples with (IP, MAC, Vendor)
    """
    # Command to run netdiscover
    command = ["sudo", "netdiscover", "-i", interface, "-r", network_ip, "-P"]
    loggers["network"].info(f"Running netdiscover on interface '{interface}' for network '{network_ip}' with timeout {timeout} seconds.")
    
    # Run netdiscover and capture the output
    try:
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=timeout)
        output = result.stdout
        
        # Check if the command returned an error
        if result.stderr:
            loggers["network"].warning(f"Netdiscover encountered an error:\n{result.stderr}")
            
    except subprocess.TimeoutExpired:
        loggers["network"].error("Netdiscover command timed out!")
        return []
    except Exception as e:
        loggers["network"].error(f"Error running netdiscover: {e}")
        return []

    # Parse the output using regex to extract IP, MAC, and Vendor
    devices = []
    pattern = r"(\d+\.\d+\.\d+\.\d+)\s+([0-9A-Fa-f:]+)\s+([^\n]+)"
    matches = re.findall(pattern, output)

    for match in matches:
        ip, mac, vendor = match
        vendor = vendor.strip()
        devices.append((ip, mac, vendor))
        # loggers["network"].debug(f"Detected Device - IP: {ip}, MAC: {mac}, Vendor: {vendor}")

    return devices

# Example usage
# devices = run_netdiscover("wlan0", "192.168.1.0/24")
# if devices:
#     print("Devices found:")
#     for device in devices:
#         print(f"IP: {device[0]}, MAC: {device[1]}, Vendor: {device[2]}")
# else:
#     print("No devices found.")
