import subprocess
import re

def run_netdiscover(interface, network_ip, timeout=10):
    """
    Runs netdiscover on the given network interface and returns a list of IP, MAC, and Vendor information.
    
    :param interface: Network interface to scan (default: wlan0)
    :param timeout: Timeout for the netdiscover command (default: 10 seconds)
    :return: List of tuples with (IP, MAC, Vendor)
    """
    # Command to run netdiscover
    command = ["sudo", "netdiscover", "-i", interface, "-r", network_ip, "-P"]

    # Run netdiscover and capture the output
    try:
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=timeout)
        output = result.stdout
    except subprocess.TimeoutExpired:
        print("Netdiscover command timed out!")
        return []
    except Exception as e:
        print(f"Error running netdiscover: {e}")
        return []

    # Parse the output using regex to extract IP, MAC, and Vendor
    devices = []
    # Regex pattern to capture IP, MAC, and Vendor
    pattern = r"(\d+\.\d+\.\d+\.\d+)\s+([0-9A-Fa-f:]+)\s+([^\n]+)"
    matches = re.findall(pattern, output)

    for match in matches:
        ip, mac, vendor = match
        devices.append((ip, mac, vendor.strip()))

    return devices

# Example usage
# devices = run_netdiscover()
# if devices:
#     print("Devices found:")
#     for device in devices:
#         print(f"IP: {device[0]}, MAC: {device[1]}, Vendor: {device[2]}")
# else:
#     print("No devices found.")

# Devices detected: 192.168.226.202 [DEfault gateawy], hhg [Unknown]
# No additinal devices deteced
# Defau;t gateway set
# wifi protocol safe 

# add logger messages to ur network things