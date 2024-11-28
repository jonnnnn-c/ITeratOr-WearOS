import argparse
import threading
from app.setup.setup_environment import setup_required_tools, enable_adb_root
from app.logs.logger_config import (
    initialize_loggers,
    clear_output_folder,
)
from app.preacquisition import initiate, network_management
from app.setup.choices import *
from app.setup.compress_folder import *
import re
import ipaddress

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


def display_menu(case_number, device_name, case_name, choice=None):
    """Display the main menu for the user after successful connection."""

    # Handle case_number display: Use "Not Set" if it's None or empty
    case_number_display = "Not Set" if not case_number else str(case_number)

    # Handle case_name display: Use "Not Set" if it's None or empty
    case_name_display = "Not Set" if not case_name else case_name

    # Define the menu options, including investigator's name above the case number
    menu_options = [
        " You are connected to: " + str(device_name),
        "Case Number: " + case_number_display,
        "Case Name: " + case_name_display,
        "",
        "Acquisition",
        "1. Auto run acquisition commands",
        "2. Manually run acquisition commands",
        "3. Compress Output Folder",
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
    menu_options[4] = f"{'=' * ((separator_length - len(menu_options[4]) - 2) // 2)} {menu_options[4]} {'=' * ((separator_length - len(menu_options[4]) - 2 + 1) // 2)}"
    menu_options[9] = f"{'=' * ((separator_length - len(menu_options[9]) - 2) // 2)} {menu_options[9]} {'=' * ((separator_length - len(menu_options[9]) - 2 + 1) // 2)}"

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
                # Call compress_folder with necessary arguments
                folder_path = OUTPUT_DIR[:-1]  # Assuming OUTPUT_DIR is defined in settings
                output_dir = ROOT_DIR  # Assuming ROOT_DIR is defined in settings

                # Loop to validate compression type
                while True:
                    print("\n" + "=" * 50)
                    print("Select Compression Type:")
                    print("=" * 50)
                    print("1. ZIP")
                    print("2. TAR")
                    print("3. TAR.GZ")
                    print("4. Exit to go back")
                    
                    user_choice = input("Enter the number corresponding to your choice: ").strip()

                    if user_choice == "1":
                        compression_type = "zip"
                        break  # Valid input; exit the loop
                    elif user_choice == "2":
                        compression_type = "tar"
                        break
                    elif user_choice == "3":
                        compression_type = "tar.gz"
                        break
                    elif user_choice == "4":
                        compression_type = "exit"
                        break
                    else:
                        print("Invalid choice. Please enter 1, 2, 3, or 4.")
                        loggers["app"].warning("User entered an invalid compression option.")

                if compression_type != "exit":
                    try:
                        compress_folder(case_name, folder_path, output_dir, compression_type, case_number)
                        loggers["app"].info(f"Folder successfully compressed using {compression_type}.")
                    except Exception as e:
                        loggers["app"].error(f"Failed to compress folder: {e}")
                else:
                    loggers["app"].info("User cancelled output folder compression.")

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
        success, watch_ip, case_number, case_name = initiate.initialise(network_interface)
        if not success:
            loggers["app"].error("Connection aborted. Exiting...")
            return
        
        try:
            # Run the 'ip' command to get interface details
            result = subprocess.run(
                ['ip', 'addr', 'show', network_interface],
                capture_output=True,
                text=True,
                check=True
            )
            # result = run_network_command(['ip', 'addr', 'show', interface])
            # Extract IP address and subnet mask in CIDR format (e.g., '192.168.1.5/24')
            match = re.search(r'inet (\d+\.\d+\.\d+\.\d+/\d+)', result.stdout.strip())

            if match:
                # Get the IP address in CIDR format
                ip_cidr = match.group(1)

                # Convert to network address (network IP)
                network = ipaddress.ip_network(ip_cidr, strict=False)
                network_ip_cidr = str(network)
                
        except subprocess.CalledProcessError as e:
            loggers["network"].error(
                f"Error retrieving network IP and subnet for {network_interface}: {e}")
            return "192.168.0.0/24"  # Default fallback subnet

        # current_network_cidr = network_management.get_network_ip_cidr(network_interface)
        #device_detection_thread = threading.Thread(target=connect.detect_devices)
        device_detection_thread = threading.Thread(target=network_management.detect_devices, args=(network_ip_cidr, watch_ip, network_interface))
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
            loggers["app"].info("Device rooted: True\n")
        else:
            loggers["app"].warning("Device rooted: False")
            loggers["app"].warning("Device is not rooted; some commands may not work properly.\n")
        loggers["app"].info("To safely disconnect, select option 0 from the menu or press Ctrl+C to exit the script.")

        if emulated:
            case_data = case_details()
            case_number = case_data["case"]["case_number"]
            case_name = case_data["case"]["case_name"]
            display_menu(case_number, device_name, case_name)
        else:
            device_name = network_management.get_physical_device_name()
            if device_name:
                display_menu(case_number, device_name, case_name)
            else:
                loggers["app"].error("Unable to retrieve physical device name, please ensure you entered the correct port.")
                exit_program()

    except KeyboardInterrupt:
        loggers["app"].warning("Keyboard Interrupt: Script ended abruptly")
        should_exit = True  # Set exit state
        exit_program()

if __name__ == "__main__":
    main()
