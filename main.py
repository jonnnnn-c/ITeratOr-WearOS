import argparse

from app.setup.setup_environment import setup_required_tools, enable_adb_root
from app.logs.logger_config import (
    initialize_loggers,
    clear_output_folder,
)
from app.preacquisition import pair, connect
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

    # TODO: maybe add an option to disable certain commands for auto run (e.g. freeze)
    menu_options = [
        f"You are connected to: {str(device_name)}",
        "",
        "1. Auto run acquisition commands",
        "2. Manually run acquisition commands",
        "3. Others",  # Placeholder for adb shell or other options
        "4. Download contents retrieved",  # Log and adb pull
        "5. Exit",
    ]

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
                run_other_commands()
            elif choice == "4":
                download_retrieved_content()
            elif choice == "5":
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
    border = "+" + "-" * (max_length + 2) + "+"

    print("\n" + border)
    for option in options:
        print(f"| {option.ljust(max_length)} |")
    print(border)


def main():
    global emulated, network_interface

    # Parse command-line options
    option = parser_options()
    # Clear log files if the option is set
    if option.clear_logs:
        clear_output_folder()
        loggers["app"].warning("Log clearing operation completed.")
    # Set up environment (install necessary tools like adb, iwlist)
    setup_required_tools()

    if option.physical:
        emulated = False
        network_interface = option.interface
        loggers["app"].info("Selected: Physical watch")
        loggers["app"].info(f"Using network interface: {network_interface}")
        # Connect and pair with the physical device
        if not pair.pair(network_interface):  # Check if pairing was successful
            loggers["app"].error("Connection aborted. Exiting...")
            return  # Exit if connection fails
    elif option.emulated:
        emulated = True
        loggers["app"].info("Selected: Emulated watch")
        # No pairing needed for emulated watch
        # Check if there are any adb devices, if not quit
        device = connect.check_adb_devices()
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
        return  # Exit early in case of invalid options

    # Display the main menu once the connection is established
    try:
        # Run adb root and check if it was successful, used mainly for emulated devices
        if enable_adb_root():
            loggers["app"].info("Device rooted: True")
        else:
            loggers["app"].warning("Device rooted: False")
            loggers["app"].warning(
                "Device is not rooted; some commands may not work properly."
            )
        loggers["app"].warning(
            "To safely disconnect, select option 5 from the menu or press Ctrl+C to exit the script."
        )

        if emulated:
            display_menu(device_name)
        else:
            display_menu(connect.get_physical_device_name())
    except KeyboardInterrupt:
        loggers["app"].warning("Keyboard Interrupt: Script ended abruptly")
        exit_program()


if __name__ == "__main__":
    main()
