from app.logs.logger_config import *
from app.preacquisition.connect import *

def pair():
    print("Pairing to Wear OS Smartwatch")
    
    interface = 'wlan0'  # Change this to your actual wireless interface if different

    current_network = get_current_network(interface)
    if not current_network:
        print("Could not retrieve the current network. Exiting...")
        return False  # Return False on failure

    print(f"Currently connected to: {current_network}")

    if not iwlist_security_check(interface, current_network):
        print("Security scan failed. Aborting connection.")
        return False  # Return False on failure
    
    # Get the current device's IP address
    current_device_ip = subprocess.getoutput("hostname -I | awk '{print $1}'").strip()
    
    # Ask for router IP to check firmware version
    router_ip = input("Enter the router's IP address to check firmware version (or leave blank to skip): ")
    if router_ip:
        firmware_version = check_firmware_version(router_ip)

    # Pair with the smartwatch
    success, watch_ip = pair_device()  # Get success status and IP
    if success:
        # Verify the network devices
        if verify_network_devices(current_device_ip, watch_ip):
            if connect_to_device(watch_ip):
                return True  # Successfully connected
            else:
                print("Failed to connect to the device.")
        else:
            print("Failed network verification. Aborting connection.")
    else:
        print("Failed to pair with the device.")
    
    return False  # Return False if any step failed
