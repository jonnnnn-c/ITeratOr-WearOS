import os
import json
import subprocess
from app.preacquisition import network_management
from app.logs.logger_config import initialize_loggers
from app.acquisition import (
    device_information, 
    device_isolation, 
    hash_generator,
    logical_data_extraction, 
    process_analyzer
)
from app.setup.settings import *

from app.setup import settings
from datetime import datetime

# Initialize all loggers
loggers = initialize_loggers()

# Set output folder and output file path
upload_dir = settings.OUTPUT_DIR
output_file_path = os.path.join(upload_dir, "case_information.txt")


def case_details():
    """
    Collects detailed case, examiner, and organization information
    and saves them to a specified file.

    Returns:
        dict: A dictionary containing the collected information.
    """
    # Initialize the data structure
    data = {
        "case": {
            "case_name": None,
            "case_number": None,
            "created_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "case_type": None,
        },
        "examiner": {
            "name": None,
            "phone": None,
            "email": None,
            "note": None,
        },
        "organization": {
            "name": None,
            "point_of_contact": None,
            "phone": None,
            "email": None,
        },
    }

    # Collect case details
    print("\n" + "=" * 50)
    print("Optional: Case Details")
    print("=" * 50)
    print(f"**Type in the necessary information or press Enter to skip any input. \nDetails will be saved to {output_file_path}**\n")
    
    data["case"]["case_name"] = input("Case Name: ").strip()
    loggers["app"].info(f"Case Name: {data['case']['case_name'] or 'Not provided'}")

    case_number = input("Case Number (integer): ").strip()
    data["case"]["case_number"] = int(case_number) if case_number.isdigit() else None
    loggers["app"].info(f"Case Number: {data['case']['case_number'] or 'Not provided'}")

    data["case"]["case_type"] = input("Case Type: ").strip()
    loggers["app"].info(f"Case Type: {data['case']['case_type'] or 'Not provided'}")

    # Collect examiner details
    print("\n" + "=" * 50)
    print("Examiner Details")
    print("=" * 50)
    data["examiner"]["name"] = input("Examiner Name: ").strip()
    loggers["app"].info(f"Examiner Name: {data['examiner']['name'] or 'Not provided'}")

    data["examiner"]["phone"] = input("Examiner Phone: ").strip()
    loggers["app"].info(f"Examiner Phone: {data['examiner']['phone'] or 'Not provided'}")

    data["examiner"]["email"] = input("Examiner Email: ").strip()
    loggers["app"].info(f"Examiner Email: {data['examiner']['email'] or 'Not provided'}")

    data["examiner"]["note"] = input("Examiner Note: ").strip()
    loggers["app"].info(f"Examiner Note: {data['examiner']['note'] or 'Not provided'}")

    # Collect organization details
    print("\n" + "=" * 50)
    print("Organization Details")
    print("=" * 50)
    data["organization"]["name"] = input("Organization Name: ").strip()
    loggers["app"].info(f"Organization Name: {data['organization']['name'] or 'Not provided'}")

    data["organization"]["point_of_contact"] = input("Point of Contact: ").strip()
    loggers["app"].info(f"Point of Contact: {data['organization']['point_of_contact'] or 'Not provided'}")

    data["organization"]["phone"] = input("Organization Phone: ").strip()
    loggers["app"].info(f"Organization Phone: {data['organization']['phone'] or 'Not provided'}")

    data["organization"]["email"] = input("Organization Email: ").strip()
    loggers["app"].info(f"Organization Email: {data['organization']['email'] or 'Not provided'}")

    # Save the information to the output file
    try:
        with open(output_file_path, "w") as file:
            file.write("Case Information\n")
            file.write("=" * 50 + "\n\n")
            file.write("Case:\n")
            file.write(f"  Case Name: {data['case']['case_name'] or 'Not provided'}\n")
            file.write(f"  Case Number: {data['case']['case_number'] or 'Not provided'}\n")
            file.write(f"  Created Date: {data['case']['created_date']}\n")
            file.write(f"  Case Type: {data['case']['case_type'] or 'Not provided'}\n\n")

            file.write("Examiner:\n")
            file.write(f"  Name: {data['examiner']['name'] or 'Not provided'}\n")
            file.write(f"  Phone: {data['examiner']['phone'] or 'Not provided'}\n")
            file.write(f"  Email: {data['examiner']['email'] or 'Not provided'}\n")
            file.write(f"  Note: {data['examiner']['note'] or 'Not provided'}\n\n")

            file.write("Organization:\n")
            file.write(f"  Name: {data['organization']['name'] or 'Not provided'}\n")
            file.write(f"  Point of Contact: {data['organization']['point_of_contact'] or 'Not provided'}\n")
            file.write(f"  Phone: {data['organization']['phone'] or 'Not provided'}\n")
            file.write(f"  Email: {data['organization']['email'] or 'Not provided'}\n")
        loggers["app"].info(f"Case information saved to {output_file_path}")
    except Exception as e:
        loggers["app"].error(f"Failed to save case information: {e}")

    return data


def run_auto_acquisition():
    """Run the auto acquisition commands based on user settings."""
    confirmation = input(
        "Are you sure you want to start the auto acquisition process? (y/n): ").strip().lower()

    if confirmation != 'y':
        loggers["app"].info("Auto acquisition canceled by user.")
        return

    loggers["app"].info("You selected auto run acquisition.")

    # Load settings to check which steps to run
    current_settings = load_user_settings()
    acquisition_steps = current_settings.get("auto_acquisition_steps", {})

    # 1: Device Information Step
    if acquisition_steps.get("device_information", True):
        loggers["acquisition"].info(
            "========== Step 1: Running device information commands ==========")
        device_information.document_device_state()

    # 2: Device Isolation Step
    if acquisition_steps.get("device_isolation", True):
        loggers["acquisition"].info(
            "========== Step 2: Running isolation of device commands ==========")
        device_isolation.isolate_device_state()

    # 3: Logical Data Extraction Step
    if acquisition_steps.get("logical_data_extraction", True):
        loggers["acquisition"].info(
            "========== Step 3: Running logical data extraction ==========")
        logical_data_extraction.run_data_extraction()

    # 4: Process Analysis Step
    if acquisition_steps.get("process_analysis", True):
        loggers["acquisition"].info(
            "========== Step 4: Running process analysis commands ==========")
        process_analyzer.analyze_device_processes()

    # 5: Freeze Processes Step
    if acquisition_steps.get("freeze_processes", True):
        loggers["acquisition"].info(
            "========== Step 5: Freezing device processes ==========")
        process_analyzer.freeze_device_processes()

    loggers["app"].info("Auto acquisition process completed.")


def run_manual_acquisition():
    """Run manual acquisition commands."""
    loggers["app"].info("You selected manual acquisition.")

    try:
        # Define the categories and their respective functions
        categories = {
            "Device Information": device_information.available_functions(),
            "Isolate Device": device_isolation.available_functions(),
            "Logical Data Extraction": logical_data_extraction.available_functions(),
            "Analyze Processes": process_analyzer.available_functions()
        }

        # Display available categories
        print("\nAvailable acquisition command categories:")
        for i, category in enumerate(categories.keys(), start=1):
            print(f"{i}. {category}")

        # Allow user to select a category with validation
        while True:
            try:
                category_input = input(
                    "\nSelect a category by number (or type 'exit' to quit): ").strip()
                if category_input.lower() == 'exit':
                    loggers["app"].info(
                        "User chose to exit the manual acquisition menu.")
                    return  # Exit the function if the user wants to quit

                category_choice = int(category_input) - 1

                # Check if the choice is valid
                if 0 <= category_choice < len(categories):
                    selected_category = list(categories.keys())[
                        category_choice]
                    selected_functions = categories[selected_category]
                    loggers["app"].info(
                        f"User selected category: {selected_category}")
                    break  # Exit the loop if valid choice
                else:
                    loggers["app"].warning(
                        "Invalid selection. Please select a valid category number.")
            except ValueError:
                loggers["app"].warning("Invalid input. Please enter a number.")

        # Display functions in the selected category
        print(f"\nAvailable functions in {selected_category}:")
        for i, (func_name, description) in enumerate(selected_functions.items(), start=1):
            print(f"  {i}. {description}")

        # Allow user to select a function with validation
        while True:
            try:
                function_input = input(
                    "\nSelect a command to run by number (or type 'exit' to quit): ").strip()
                if function_input.lower() == 'exit':
                    loggers["app"].info(
                        "User chose to exit the manual acquisition menu.")
                    return  # Exit the function if the user wants to quit

                function_choice = int(function_input) - 1

                # Check if the choice is valid
                if 0 <= function_choice < len(selected_functions):
                    selected_func_name = list(selected_functions.keys())[
                        function_choice]
                    loggers["app"].info(
                        f"User selected function: {selected_func_name}")
                    break  # Exit the loop if valid choice
                else:
                    loggers["app"].warning(
                        "Invalid selection. Please select a valid command number.")
            except ValueError:
                loggers["app"].warning("Invalid input. Please enter a number.")

        # Call the selected function dynamically using the module prefix
        try:
            if selected_category == "Device Information":
                loggers["app"].info(
                    f"Executing function: {selected_func_name} in {selected_category}\n")
                getattr(device_information, selected_func_name)()
            elif selected_category == "Isolate Device":
                loggers["app"].info(
                    f"Executing function: {selected_func_name} in {selected_category}\n")
                getattr(device_isolation, selected_func_name)()
            elif selected_category == "Logical Data Extraction":
                loggers["app"].info(
                    f"Executing function: {selected_func_name} in {selected_category}\n")
                getattr(logical_data_extraction, selected_func_name)()
            elif selected_category == "Analyze Processes":
                loggers["app"].info(
                    f"Executing function: {selected_func_name} in {selected_category}\n")
                getattr(process_analyzer, selected_func_name)()
        except Exception as e:
            loggers["app"].error(
                f"Error executing function {selected_func_name}: {str(e)}")
            print(f"An error occurred while executing the function: {str(e)}")

    except KeyboardInterrupt:
        loggers["app"].info(
            "KeyboardInterrupt detected. Exiting manual acquisition menu.")
    except Exception as e:
        loggers["app"].error(f"An unexpected error occurred: {str(e)}")
        print(f"An unexpected error occurred: {str(e)}")

    loggers["app"].info("Manual acquisition session closed.")


def run_adb_shell():
    """Start an interactive adb shell session with real-time command execution and logging."""
    loggers["app"].info(
        "Starting adb shell session. Type 'exit' to leave the shell.")

    try:
        # Start adb shell session
        while True:
            # Prompt user for command input
            command = input("adb shell> ").strip()

            if command.lower() == 'exit':
                loggers["app"].info("User exited adb shell session.")
                break

            try:
                # Log the command and execute it in adb shell
                loggers["app"].info(f"Executing command: {command}")

                # Execute the command in adb shell
                result = subprocess.run(
                    ['adb', 'shell', command],
                    capture_output=True,
                    text=True
                )

                # Process and print output
                output = result.stdout.strip()
                error = result.stderr.strip()

                if output:
                    loggers["app"].info(f"Output for '{command}': {output}")
                if error:
                    print(f"Error: {error}")
                    loggers["app"].error(f"Error for '{command}': {error}")

            except KeyboardInterrupt:
                loggers["app"].info(
                    "KeyboardInterrupt detected. Exiting adb shell.")
                break

    except Exception as e:
        loggers["app"].error(f"Failed to start adb shell session: {str(e)}")
        print(f"An error occurred: {str(e)}")

    except KeyboardInterrupt:
        loggers["app"].info("KeyboardInterrupt detected. Exiting adb shell.")

    loggers["app"].info("ADB shell session closed.")


def download_retrieved_content():
    """Download the contents retrieved during acquisition."""
    loggers["app"].info("Downloading contents retrieved.")


def run_hash_generation():
    """Run the hash generation process."""
    try:
        hash_generator.main()
    except Exception as e:
        loggers["app"].error(f"Error during hash generation: {str(e)}")


def check_for_given_file(given_file):
    """Check for the existence of the given file.
    Return True if it exists, else return False."""

    # Check if the settings file exists
    if not os.path.isfile(given_file):
        return False  # File does not exist
    else:
        return True  # File exists


def settings():
    """Configure user settings and save them to a JSON file."""
    # Load current settings
    current_settings = load_user_settings()
    loggers["app"].info(f"Current settings loaded from {USER_SETTING}")
    loggers["app"].info(json.dumps(current_settings))

    try:
        while True:
            # Display menu
            print("\nWhich setting would you like to edit?")
            print("1. Toggle Network Enforcement")
            print("2. Edit Auto Acquisition Steps")
            print("3. Toggle GENAI Process Descriptions")
            print("0. Exit")

            choice = input("Enter your choice (0-3): ").strip()
            loggers["app"].info(f"User selected option: {choice}")

            if choice == '1':
                # Network Enforcement Setting
                current_value = current_settings.get('network_enforcement', 'unknown')
                loggers["app"].info(f"Current Network Enforcement setting: '{current_value}'")

                print("\nSelect a setting for enforcing network:")
                print("1. Enable network enforcement ('enable')")
                print("2. Disable network enforcement ('disable')")

                option = input("Enter your choice (1 or 2): ").strip()

                while option not in ["1", "2"]:
                    loggers["app"].warning("Invalid input for Network Enforcement.")
                    option = input("Enter your choice (1 or 2): ").strip()

                network_enforcement = "enable" if option == "1" else "disable"
                current_settings['network_enforcement'] = network_enforcement
                loggers["app"].info(
                    f"Network enforcement setting updated to '{network_enforcement}'."
                )

            elif choice == '2':
                # Auto Acquisition Steps
                print("\nCurrent Auto Acquisition Steps:")
                for step, enabled in current_settings['auto_acquisition_steps'].items():
                    formatted_step = step.replace('_', ' ').title()
                    status = "enabled" if enabled else "disabled"
                    print(f" - {formatted_step}: {status}")
                loggers["app"].info(f"Current Auto Acquisition Steps: {current_settings['auto_acquisition_steps']}")

                print("\nEnter the steps you want to enable/disable (comma-separated, e.g., 'Device Information, Process Analysis') or type 'all' to toggle all:")
                steps_input = input("Steps to toggle (leave blank to skip): ").strip()

                toggled_steps = []

                if steps_input.lower() == "all":
                    for step in current_settings['auto_acquisition_steps']:
                        current_settings['auto_acquisition_steps'][step] = not current_settings['auto_acquisition_steps'][step]
                        new_status = "enabled" if current_settings['auto_acquisition_steps'][step] else "disabled"
                        toggled_steps.append(f"{step.replace('_', ' ').title()}: {new_status}")
                else:
                    steps_to_toggle = [step.strip().replace(' ', '_').lower() for step in steps_input.split(',')]
                    for step in steps_to_toggle:
                        if step in current_settings['auto_acquisition_steps']:
                            current_settings['auto_acquisition_steps'][step] = not current_settings['auto_acquisition_steps'][step]
                            new_status = "enabled" if current_settings['auto_acquisition_steps'][step] else "disabled"
                            toggled_steps.append(f"{step.replace('_', ' ').title()}: {new_status}")
                        else:
                            loggers["app"].warning(f"Invalid step: {step.replace('_', ' ').title()}.")

                if toggled_steps:
                    loggers["app"].info(f"Toggled auto acquisition steps: {', '.join(toggled_steps)}")
                else:
                    loggers["app"].info("No steps were toggled.")

            elif choice == '3':
                # GENAI Process Descriptions
                current_value = current_settings.get('generate_descriptions', 'unknown')
                loggers["app"].info(f"Current Generate Descriptions setting: '{current_value}'")

                print("\nSelect a setting for generating descriptions:")
                print("1. All processes ('all')")
                print("2. Unknown processes only ('unknown')")
                print("3. Turn off description generation ('off')")

                option = input("Enter your choice (1, 2, or 3): ").strip()

                while option not in ["1", "2", "3"]:
                    loggers["app"].warning("Invalid input for Generate Descriptions setting.")
                    option = input("Enter your choice (1, 2, or 3): ").strip()

                generate_descriptions = "all" if option == "1" else "unknown" if option == "2" else "off"
                current_settings['generate_descriptions'] = generate_descriptions
                loggers["app"].info(f"Generate descriptions setting updated to '{generate_descriptions}'.")

            elif choice == '0':
                loggers["app"].info("User selected to exit settings configuration.")
                break

            else:
                loggers["app"].warning("Invalid option selected.")

            # Save updated settings
            with open(USER_SETTING, 'w') as file:
                json.dump(current_settings, file, indent=4)
            
            print()
            loggers["app"].info(f"Settings saved to {USER_SETTING}.")
            loggers["app"].info(f"Updated settings:\n{json.dumps(current_settings, indent=4)}")

    except KeyboardInterrupt:
        loggers["app"].warning("Settings configuration interrupted by user.")
        with open(USER_SETTING, 'w') as file:
            json.dump(current_settings, file, indent=4)
        loggers["app"].info("Settings saved and exiting.")


def load_user_settings():
    """
    Load user settings from a JSON file.
    """
    try:
        with open(USER_SETTING, 'r') as f:
            settings = json.load(f)
        return settings
    except FileNotFoundError:
        loggers["acquisition"].error("User settings file not found.")
        return {}
    except json.JSONDecodeError:
        loggers["acquisition"].error("Error decoding JSON from user settings file.")
        return {}


def exit_program():
    """Exit the application."""
    loggers["app"].info("Exiting the application...")
    network_management.disconnect_all_devices()  # Assuming this exists in your codebase
