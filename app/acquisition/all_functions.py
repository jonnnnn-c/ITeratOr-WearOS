def available_functions():
    """List of available functions to document device state with descriptions."""
    
    return {
        "Initial Documentation and Device State": {
            "get_device_info": "Capture device model, android version, and serial number",
            "get_network_info": "Capture network interfaces, and WiFi info",
            "get_battery_status": "Capture battery status",
            "get_storage_info": "Capture storage information",
            "get_installed_packages": "List installed applications",
            "get_running_processes": "Get active processes",
            "get_running_services": "Get running services",
            "get_network_connections": "Get current network connections",
            "get_system_log": "Capture system logs (logcat)",
            "capture_screenshot": "Capture a screenshot of the device",
            "get_encryption_status": "Capture encryption status"
        },
        "Isolate the Device (Network Disable/Airplane Mode)": {
            "x": "x"
        },
        "Capture Volatile Data (RAM and Processes)": {
            "x": "x"
        },
        "Freeze and Suspend Running Processes": {
            "x": "x"
        },
        "Logical Data Extraction": {
            "x": "x"
        }
    }
