import json
import os
from app.preacquisition import connect
from app.logs.logger_config import initialize_loggers
from app.acquisition import device_information, device_isolation, hash_generator, process_analyzer

# Initialize all loggers
loggers = initialize_loggers()


def run_auto_acquisition():
    """Run the auto acquisition commands."""
    loggers["app"].info("You selected auto run acquisition.")

    device_information.document_device_state() # 1
    device_isolation.isolate_device_state() # 2
    # 3
    process_analyzer.analyze_device_processes() # 6
    process_analyzer.freeze_device_processes() # 6


def run_manual_acquisition():
    """Run manual acquisition commands."""
    loggers["app"].info("You selected manual acquisition.")

    # Define the categories and their respective functions
    categories = {
        "Device Information": device_information.available_functions(),
        "Isolate Device": device_isolation.available_functions(),
        "Analyze Processes": process_analyzer.available_functions()
    }

    # Display available categories
    print("\nAvailable acquisition command categories:")
    for i, category in enumerate(categories.keys(), start=1):
        print(f"{i}. {category}")

    # Allow user to select a category with validation
    while True:
        try:
            category_choice = int(input("\nSelect a category by number: ")) - 1

            # Check if the choice is valid
            if 0 <= category_choice < len(categories):
                selected_category = list(categories.keys())[category_choice]
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
            function_choice = int(
                input("\nSelect a command to run by number: ")) - 1

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
                f"Executing function: {selected_func_name} in {selected_category}")
            getattr(device_information, selected_func_name)()
        elif selected_category == "Isolate Device":
            loggers["app"].info(
                f"Executing function: {selected_func_name} in {selected_category}")
            getattr(device_isolation, selected_func_name)()
        elif selected_category == "Analyze Processes":
            loggers["app"].info(
                f"Executing function: {selected_func_name} in {selected_category}")
            getattr(process_analyzer, selected_func_name)()
    except Exception as e:
        loggers["app"].error(
            f"Error executing function {selected_func_name}: {str(e)}")
        print(f"An error occurred while executing the function: {str(e)}")


def run_other_commands():
    """Run other commands like adb shell."""
    loggers["app"].info("Running other commands (to be implemented).")


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
    settings_file = 'user_settings.json'
    
    # Check and create the settings file if necessary
    file_exists = check_for_given_file(settings_file)
    if not file_exists:
    	# Create the settings file with default values
        default_settings = {"network_enforcement": "disable"}
        with open(settings_file, 'w') as file:
            json.dump(default_settings, file, indent=4)
        print(f"{settings_file} created with default settings.")

    # Initialize a dictionary to hold user settings
    user_settings = {}

    # Prompt user for various settings options
    user_settings['network_enforcement'] = input(
        "Enter setting for enforcing network (e.g., 'enable/disable'): ")
    user_settings['option2'] = input(
        "Enter setting for option 2 (e.g., 'high/medium/low'): ")
    user_settings['option3'] = input(
        "Enter setting for option 3 (e.g., 'yes/no'): ")

    # Save settings to a JSON file
    with open(settings_file, 'w') as file:
        json.dump(user_settings, file, indent=4)

    print(f"Settings saved to {settings_file}")

    # Optionally, you can load and display the settings back to the user
    print("\nCurrent Settings:")
    print(json.dumps(user_settings, indent=4))


def exit_program():
    """Exit the application."""
    loggers["app"].info("Exiting the application...")
    connect.disconnect_all_devices()  # Assuming this exists in your codebase
