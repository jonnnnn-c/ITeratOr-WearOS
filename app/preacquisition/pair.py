from app.logs.logger_config import initialize_loggers
from app.preacquisition.connect import *

# Initialize all loggers
loggers = initialize_loggers()


def pair(network_interface):
    logger.info("Pairing to WearOS Smartwatch")

    current_network = get_current_network(network_interface)
    if not current_network:
        logger.error("Could not retrieve the current network. Exiting...")
        return False  # Return False on failure

    logger.info(f"Currently connected to: {current_network}")

    if not iwlist_security_check(network_interface, current_network):
        logger.error("Security scan failed. Aborting connection.")
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
                logger.error("Failed to connect to the device.")
        else:
            logger.error("Failed network verification. Aborting connection.")
    else:
        logger.error("Failed to pair with the device.")
    
    return False  # Return False if any step failed
