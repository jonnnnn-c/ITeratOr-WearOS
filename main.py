import argparse

from app.logs.logger_config import logger

from app.preacquisition import pair

from app.acquisition.dumpsys import *


# Global variables
emulated = None
network_interface = "wlan0"


def display_menu():
    """Display the main menu for the user after successful connection."""
    while True:
        print("\nChoose an option:")
        print("1. Run Dumpsys")
        print("2. Another Option")
        print("3. Exit")

        choice = input("Enter your choice: ")

        if choice == "1":
            dump_watch_data()
        elif choice == "2":
            print("You selected another option (to be implemented).")
            # Add functionality for another option here
        elif choice == "3":
            print("Exiting...")
            disconnect_all_devices()
            break
        else:
            print("Invalid choice. Please try again.")


def parser_options():
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

    return parser.parse_args()


def main():
    global emulated

    # Check which option was selected
    option = parser_options()

    if option.physical:
        emulated = False
        network_interface = option.interface
        
        logger.info("Selected: Physical watch")
        logger.info(f"Using network interface: {network_interface}")
        
        # Connect and pair
        if not pair.pair(network_interface):  # Check if pairing was successful
            logger.error("Connection aborted. Exiting...")
            return  # Exit if not successful

    elif option.emulated:
        emulated = True
        logger.info("Selected: Emulated watch")
        
        # Emulated so don't need to connect and pair

    else:
        logger.error("Invalid Option")

    # Display menu after connection established
    display_menu()

if __name__ == "__main__":
    main()
