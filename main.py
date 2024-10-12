import argparse
from app.preacquisition import pair
from app.acquisition.dumpsys import *
from app.setup.setup_environment import setup_required_tools
from app.logs.logger_config import (
    initialize_loggers,
    clean_output_folder,
)  # Import the logger initialization function

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

    # Add an optional argument to clean log files
    parser.add_argument(
        "--clean-logs",
        action="store_true",
        help="Clean all log files in the output folder",
    )

    return parser.parse_args()


def display_menu(logger):
    """Display the main menu for the user after successful connection."""
    
    while True:
        print("\nChoose an option:")
        print("1. Run Dumpsys")
        print("2. Another Option")
        print("3. Exit")

        choice = input("Enter your choice: ")

        if choice == "1":
            loggers["dumpsys"].info("Running Dumpsys...")
            dump_watch_data()

        elif choice == "2":
            loggers["app"].info("You selected another option (to be implemented).")
            print("You selected another option (to be implemented).")
            # Add functionality for another option here

        elif choice == "3":
            loggers["app"].info("Exiting the application.")
            disconnect_all_devices()  # Assuming this exists in your codebase
            break

        else:
            loggers["app"].warning("Invalid choice made by user.")
            print("Invalid choice. Please try again.")


def main():
    global emulated, network_interface

    # Parse command-line options
    option = parser_options()

    # Clean log files if the option is set
    if option.clean_logs:
        clean_output_folder()
        loggers["app"].info("Log cleaning operation completed.")

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

    else:
        loggers["app"].error("Invalid Option")
        return  # Exit early in case of invalid options

    # Display the main menu once the connection is established
    display_menu(loggers)


if __name__ == "__main__":
    main()
