import argparse
import threading
from app.setup.setup_environment import setup_required_tools, enable_adb_root
from app.logs.logger_config import (
    initialize_loggers,
    clear_output_folder,
)
from app.preacquisition import initiate, network_management
from app.setup.choices import *

# Global variables
emulated = None
network_interface = "wlan0"

# Initialize all loggers
loggers = initialize_loggers()


def parser_options():
    """Parse the command-line arguments for physical or emulated device."""

    parser = argparse.ArgumentParser(
        description="Choose between physical or emulated watch connection."
    )
    # Add mutually exclusive group for either -p (physical) or -e (emulated)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "-p", "--physical", action="store_true", help="Use physical watch"
    )
    group.add_argument(
        "-e", "--emulated", action="store_true", help="Use emulated watch"
    )
    # Add an optional argument for the network interface when using physical
    parser.add_argument(
        "-i",
        "--interface",
        type=str,
        default="wlan0",
        help="Specify network interface for physical watch (default is wlan0)",
    )
    # Add an optional argument to clear log files
    parser.add_argument(
        "--clear-logs",
        action="store_true",
        help="Clear all log files in the output folder",
    )
    return parser.parse_args()


def display_menu(device_name, choice=None):
    """Display the main menu for the user after successful connection."""

    menu_options = [
        " You are connected to: " + str(device_name),
        "",
        "Acquisition",
        "1. Auto run acquisition commands",
        "2. Manually run acquisition commands",
        "3. Download contents retrieved",
        "",
        "Others",
        "4. adb shell",
        "5. Settings",
        "0. Exit"
    ]

    # Calculate the maximum length for dynamic borders
    max_length = max(len(option) for option in menu_options)
    separator_length = max_length + 4  # Adding space for borders

    # Create the equal sign separators for section headers
    menu_options[2] = f"{'=' * ((separator_length - len(menu_options[2]) - 2) // 2)} {menu_options[2]} {'=' * ((separator_length - len(menu_options[2]) - 2 + 1) // 2)}"
    menu_options[7] = f"{'=' * ((separator_length - len(menu_options[7]) - 2) // 2)} {menu_options[7]} {'=' * ((separator_length - len(menu_options[7]) - 2 + 1) // 2)}"

    # Add equal sign separators at the start and end
    menu_options.insert(0, "=" * separator_length)
    menu_options.insert(2, "=" * separator_length)

    while True:
        print_boxed_menu(menu_options)

        try:
            if choice is None:
                choice = input("\nEnter your choice: ")
                print()  # Add an extra line for spacing
                loggers["app"].info(f"User selected option: {choice}")

            # Call the appropriate function based on the user's choice
            if choice == "1":
                run_auto_acquisition()
            elif choice == "2":
                run_manual_acquisition()
            elif choice == "3":
                download_retrieved_content()
            elif choice == "4":
                run_adb_shell()
            elif choice == "5":
                settings()
            elif choice == "0":
                exit_program()
                break
            else:
                loggers["app"].warning("Invalid selection. Please select a valid category number.")
            choice = None  # Reset to None for re-prompting
            
        except Exception as e:
            loggers["app"].error(f"An error occurred: {str(e)}")
            choice = None  # Reset choice for re-prompting

def print_boxed_menu(options):
    """Prints the menu inside a simple ASCII box."""
    max_length = max(len(option) for option in options)
    border_length = max_length + 2  # Adding 2 for padding
    border = "+" + "-" * border_length + "+"  # Use '-' for the top and bottom

    print("\n" + border)
    for option in options:
        print(f"| {option.ljust(max_length)} |")
    print(border)


def main():
    global emulated, network_interface  # Include the new variable

    # Parse command-line options
    option = parser_options()
    # Clear log files if the option is set
    if option.clear_logs:
        clear_output_folder()
        loggers["app"].warning("Log clearing operation completed.")
    
    setup_required_tools()

    if option.physical:
        emulated = False
        network_interface = option.interface
        loggers["app"].info("Selected: Physical watch")
        loggers["app"].info(f"Network Interface Specified: {network_interface}")
        success, watch_ip = initiate.initialise(network_interface)
        if not success:
            loggers["app"].error("Connection aborted. Exiting...")
            return
        
        current_network_cidr = network_management.get_network_ip_cidr(network_interface)
        #device_detection_thread = threading.Thread(target=connect.detect_devices)
        device_detection_thread = threading.Thread(target=network_management.detect_devices, args=(current_network_cidr, watch_ip, network_interface))
        device_detection_thread.daemon = True
        device_detection_thread.start()
        
    elif option.emulated:
        emulated = True
        loggers["app"].info("Selected: Emulated watch")
        device = network_management.check_adb_devices()
        
        if len(device) < 1:
            loggers["app"].info("No device found. Exiting")
            return
        elif len(device) > 1:
            loggers["app"].info("Please only have 1 android device running at one time")
            return
        else:
            device_name = device[0]
            loggers["app"].info(f"Emulated device chosen: {device_name}")
    else:
        loggers["app"].error("Invalid Option")
        return

    try:
        if enable_adb_root():
            loggers["app"].info("Device rooted: True")
        else:
            loggers["app"].warning("Device rooted: False")
            loggers["app"].warning("Device is not rooted; some commands may not work properly.")
        loggers["app"].warning("To safely disconnect, select option 5 from the menu or press Ctrl+C to exit the script.")

        if emulated:
            display_menu(device_name)
        else:
            device_name = network_management.get_physical_device_name()
            if device_name:
                display_menu(device_name)
            else:
                loggers["app"].error("Unable to retrieve physical device name, please ensure you entered the correct port.")
                exit_program()

    except KeyboardInterrupt:
        loggers["app"].warning("Keyboard Interrupt: Script ended abruptly")
        should_exit = True  # Set exit state
        exit_program()

if __name__ == "__main__":
    main()
