import os
from app.setup import paths
from app.logs.logger_config import initialize_loggers, run_adb_command, append_to_output_file

# Initialize all loggers
loggers = initialize_loggers()

# Set output folder and output file path
upload_dir = paths.FREEZE_PROCESSES_DIR
output_file_path = os.path.join(upload_dir, "process_freeze_status.txt")


def list_installed_packages():
    """List all installed package names on the device."""
    try:
        output = run_adb_command(
            ["adb", "shell", "pm", "list", "packages"],
            "Retrieving list of installed packages"
        )
        packages = [line.replace("package:", "").strip() for line in output.splitlines()]
        loggers["acquisition"].info("Successfully retrieved installed packages.")
        return packages
    except Exception as e:
        loggers["acquisition"].error(f"Failed to list installed packages: {e}")
        return []


def get_process_status(package_name):
    """Get the running status of the process."""
    try:
        output = run_adb_command(
            ["adb", "shell", "ps"],
            "Checking running processes"
        )
        return package_name in output
    except Exception as e:
        loggers["acquisition"].error(f"Failed to check process status: {e}")
        return False


def log_process_status(package_name, is_running):
    """Log the status of the process before freezing."""
    status = "running" if is_running else "not running"
    append_to_output_file(output_file_path, f"Process '{package_name}' is {status}.")


def freeze_process(package_name):
    """Freeze the specified process on the device."""
    is_running = get_process_status(package_name)
    log_process_status(package_name, is_running)

    if is_running:
        run_adb_command(
            ["adb", "shell", "am", "force-stop", package_name],
            f"Freezing process: {package_name}"
        )
        append_to_output_file(output_file_path, f"Process '{package_name}' has been frozen.")
    else:
        append_to_output_file(output_file_path, f"Process '{package_name}' was not running, no action taken.")


def available_functions():
    """List of available functions for freezing processes."""
    try:
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)
            loggers["acquisition"].debug(f"Created directory: {upload_dir}")

        return {
            "freeze_process": "Freeze a specified process by package name",
            "list_installed_packages": "List all installed package names on the device",
        }
    except Exception as e:
        loggers["acquisition"].error(f"An error occurred while listing available functions: {e}")
        return {}  # Return an empty dictionary if something goes wrong

def freeze_device_processes():
    """Isolate and freeze specified processes."""
    loggers["acquisition"].info("Running process freeze commands\n")

    # List all installed packages and let the user select one
    available_functions()
    
    packages = list_installed_packages()
    
    if not packages:
        loggers["acquisition"].warning("No packages found.")
        return

    # Display the list of packages to the user
    print("Installed Packages:")
    for i, package in enumerate(packages, start=1):
        print(f"{i}. {package}")

    # Allow user to select a package
    try:
        choice = int(input("\nSelect a package number to freeze: ")) - 1
        if 0 <= choice < len(packages):
            package_name = packages[choice]
            freeze_process(package_name)
        else:
            print("Invalid selection. No action taken.")
            loggers["acquisition"].warning("Invalid package selection made by user.")
    except ValueError:
        print("Invalid input. Please enter a number.")
        loggers["acquisition"].warning("Non-integer input provided for package selection.")

    loggers["acquisition"].info("Process freezing completed.\n")