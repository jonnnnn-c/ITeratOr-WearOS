import os
import json
import socket
from app.setup import (
    settings,
    choices
)
from app.logs.logger_config import (
    initialize_loggers,
    run_adb_command,
    append_to_output_file,
)
import google.generativeai as genai  # type: ignore

# Initialize all loggers
loggers = initialize_loggers()

# Set output folder and output file path
upload_dir = settings.ANALYZE_PROCESSES_DIR
output_file_path = os.path.join(upload_dir, "process_analyzer_output.txt")


# ANALYZING STUFF

def get_running_processes():
    """Retrieve the list of running processes."""
    try:
        output = run_adb_command(
            ["adb", "shell", "ps -A -o PID,PPID,USER,NAME"],
            "Retrieve running processes",
        )

        if output is None:
            return []

        processes = []
        for line in output.splitlines()[1:]:  # Skip the header
            cols = line.split()
            if len(cols) >= 4:
                pid, ppid, user, process_name = cols[0], cols[1], cols[2], cols[3]
                processes.append((pid, ppid, user, process_name))

        processes.sort(key=lambda x: x[1])  # Sort by PPID
        return processes

    except Exception as e:
        loggers["acquisition"].error(f"Failed to get list of running processes: {e}")
        return False


def get_system_packages():
    """Retrieve the list of system packages."""
    try:
        output = run_adb_command(
            ["adb", "shell", "pm list packages -s"], "Retrieve system packages"
        )

        if output is None:
            return set()

        return {line.split(":")[1].strip() for line in output.splitlines()}

    except Exception as e:
        loggers["acquisition"].error(f"Failed to get list of system packages: {e}")
        return False


def search_descriptions(package_names, timeout=15):
    """Search for descriptions of packages online with a timeout to prevent hanging."""
    if not settings.GENAI_API_KEY:
        loggers["acquisition"].warning(
            "GENAI API key not found. Skipping description retrieval."
        )
        return [
            {"process_name": name, "description": "No description available"}
            for name in package_names
        ]

    try:
        socket.create_connection(("www.google.com", 80), timeout=timeout)
    except OSError:
        loggers["acquisition"].warning(
            "No internet connection. Skipping description retrieval."
        )
        return [
            {"process_name": name, "description": "No description available"}
            for name in package_names
        ]

    prompt = f"""{package_names} The following is the result of adb ps -A, and I have no idea what these processes are; 
        could you please provide a brief description of what they may be and what their purpose is? If you're unsure, 
        it might be a user-installed item; you can search for it in the app store or Google. 

        Use this JSON schema:

        processes = {{'process_name': process_name_1, 'description': A brief description of process_name_1.}}
        Return: list[processes]
    """

    genai.configure(api_key=settings.GENAI_API_KEY)
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config={"response_mime_type": "application/json"},
    )

    try:
        response = model.generate_content(prompt)
        descriptions_list = json.loads(response.text)
        return descriptions_list

    except Exception as e:
        loggers["acquisition"].error(
            f"Failed to retrieve descriptions due to error: {e}"
        )

        return [
            {"process_name": name, "description": "No description available"}
            for name in package_names
        ]


# Function to get package version
def get_package_version(package_name):
    """Retrieve the version of a specific package if available."""
    try:
        output = run_adb_command(
            ["adb", "shell", f"dumpsys package {package_name} | grep versionName"],
            f"Retrieve version for {package_name}",
            error=False
        )
        if output:
            version_info = output.split("=")[-1].strip()
            return version_info
        else:
            return "N/A"
    except Exception as e:
        loggers["acquisition"].error(f"Failed to retrieve version for package {package_name}: {e}")
        return "N/A"


# Function to categorize processes
def categorize_processes(processes, system_packages):
    """
    Categorize processes into critical, unknown, and system apps.
    Retrieve descriptions based on user settings.
    """
    loggers["acquisition"].info("Starting process categorization.\n")

    critical_processes = []
    unknown_processes = []
    system_apps = []

    # Load user settings
    user_settings = choices.load_user_settings()
    generate_descriptions = user_settings.get("generate_descriptions", "unknown")  # Default to "unknown"
    
    for pid, ppid, user, process_name in processes:
        # Retrieve version information
        version = get_package_version(process_name)
        
        if ppid == "1" or user in ("root", "system"):
            critical_processes.append((pid, ppid, user, process_name, version, ""))
            loggers["acquisition"].debug(
                f"Classified as critical process: {process_name} (PID: {pid})"
            )
            continue

        if process_name in system_packages:
            system_apps.append((pid, ppid, user, process_name, version, ""))
            loggers["acquisition"].debug(
                f"Classified as system app: {process_name} (PID: {pid})"
            )
            continue

        unknown_processes.append((pid, ppid, user, process_name, version, ""))
        loggers["acquisition"].debug(
            f"Classified as unknown process: {process_name} (PID: {pid})"
        )

    if settings.GENAI_API_KEY:
        loggers["acquisition"].info(
            "API key found. Attempting to retrieve descriptions for processes."
        )
        # Determine which processes to retrieve descriptions for
        processes_to_describe = []
        if generate_descriptions == "all":
            processes_to_describe = critical_processes + system_apps + unknown_processes
        elif generate_descriptions == "unknown":
            processes_to_describe = unknown_processes
        elif generate_descriptions == "no":
            loggers["acquisition"].warning(
                "GENAI Process Descriptions turned off. No descriptions will be retrieved."
            )
        else:
            loggers["acquisition"].warning(
                "Invalid value for generate_descriptions. No descriptions will be retrieved."
            )
        all_process_names = [process[3] for process in processes_to_describe]
        descriptions_list = search_descriptions(all_process_names)
        descriptions_dict = {
            item["process_name"]: item["description"] for item in descriptions_list
        }
        # Add descriptions for critical processes
        for i in range(len(critical_processes)):
            pid, ppid, user, process_name, version, _ = critical_processes[i]
            process_description = descriptions_dict.get(
                process_name, "No description found"
            )
            critical_processes[i] = (pid, ppid, user, process_name, version, process_description)
            loggers["acquisition"].debug(
                f"Retrieved description for critical process: {process_name}"
            )
        # Add descriptions for system apps
        for i in range(len(system_apps)):
            pid, ppid, user, process_name, version, _ = system_apps[i]
            process_description = descriptions_dict.get(
                process_name, "No description found"
            )
            system_apps[i] = (pid, ppid, user, process_name, version, process_description)
            loggers["acquisition"].debug(
                f"Retrieved description for system app: {process_name}"
            )
        # Add descriptions for unknown processes
        for i in range(len(unknown_processes)):
            pid, ppid, user, process_name, version, _ = unknown_processes[i]
            process_description = descriptions_dict.get(
                process_name, "No description found"
            )
            unknown_processes[i] = (pid, ppid, user, process_name, version, process_description)
            loggers["acquisition"].debug(
                f"Retrieved description for unknown process: {process_name}"
            )

        loggers["acquisition"].info("Descriptions retrieval completed.")
    else:
        loggers["acquisition"].warning(
            "GENAI API key not found. Descriptions will not be retrieved for processes."
        )
        critical_processes = [
            (pid, ppid, user, process_name, version, "No description available")
            for pid, ppid, user, process_name, version, _ in critical_processes
        ]
        system_apps = [
            (pid, ppid, user, process_name, version, "No description available")
            for pid, ppid, user, process_name, version, _ in system_apps
        ]
        unknown_processes = [
            (pid, ppid, user, process_name, version, "No description available")
            for pid, ppid, user, process_name, version, _ in unknown_processes
        ]
        
    loggers["acquisition"].info("Process categorization completed.")
    
    return critical_processes, system_apps, unknown_processes


def print_processes_table(
    processes, title, file_path, max_lengths=(5, 5, 10, 45, 20, 50)
):
    """Retrieve table of categorized processes."""
    loggers["acquisition"].info(f"Writing table for '{title}' to file: {file_path}")
    (
        max_pid_length,
        max_ppid_length,
        max_user_length,
        max_name_length,
        max_vers_length,
        max_desc_length,
    ) = max_lengths

    try:
        with open(file_path, "a") as file:
            # Write title and header to file
            file.write(f"\n{title}:\n")
            file.write(
                f"{'PID':<{max_pid_length}}  {'PPID':<{max_ppid_length}}  {'User':<{max_user_length}}  {'Name':<{max_name_length}}  {'Name':<{max_vers_length}}  {'Description'}\n"
            )
            file.write("-" * (sum(max_lengths) + 10) + "\n")

            # Print title and header to console
            print(f"\n{title}:")
            print(
                f"{'PID':<{max_pid_length}}  {'PPID':<{max_ppid_length}}  {'User':<{max_user_length}}  {'Process Name':<{max_name_length}}  {'Version':<{max_vers_length}}  {'Description'}"
            )
            print("-" * (sum(max_lengths) + 10))

            for process in processes:
                pid, ppid, user, process_name, version, process_description = process

                pid_lines = [
                    pid[i : i + max_pid_length]
                    for i in range(0, len(pid), max_pid_length)
                ]
                ppid_lines = [
                    ppid[i : i + max_ppid_length]
                    for i in range(0, len(ppid), max_ppid_length)
                ]
                user_lines = [
                    user[i : i + max_user_length]
                    for i in range(0, len(user), max_user_length)
                ]
                name_lines = [
                    process_name[i : i + max_name_length]
                    for i in range(0, len(process_name), max_name_length)
                ]
                vers_lines = [
                    version[i : i + max_vers_length]
                    for i in range(0, len(version), max_vers_length)
                ]
                description_lines = [
                    process_description[i : i + max_desc_length]
                    for i in range(0, len(process_description), max_desc_length)
                ]

                max_lines = max(
                    len(pid_lines),
                    len(ppid_lines),
                    len(user_lines),
                    len(name_lines),
                    len(vers_lines),
                    len(description_lines),
                )

                for i in range(max_lines):
                    pid_part = pid_lines[i] if i < len(pid_lines) else ""
                    ppid_part = ppid_lines[i] if i < len(ppid_lines) else ""
                    user_part = user_lines[i] if i < len(user_lines) else ""
                    name_part = name_lines[i] if i < len(name_lines) else ""
                    vers_part = vers_lines[i] if i < len(vers_lines) else ""
                    desc_part = (
                        description_lines[i] if i < len(description_lines) else ""
                    )

                    # Write each line to the file
                    file.write(
                        f"{pid_part:<{max_pid_length}}  {ppid_part:<{max_ppid_length}}  {user_part:<{max_user_length}}  {name_part:<{max_name_length}}  {vers_part:<{max_vers_length}}  {desc_part}\n"
                    )

                    # Print each line to console
                    print(
                        f"{pid_part:<{max_pid_length}}  {ppid_part:<{max_ppid_length}}  {user_part:<{max_user_length}}  {name_part:<{max_name_length}}  {vers_part:<{max_vers_length}}  {desc_part}"
                    )

            file.write("-" * (sum(max_lengths) + 10) + "\n")
            print("-" * (sum(max_lengths) + 10))

        loggers["acquisition"].info(
            f"Table for '{title}' successfully written to file.\n"
        )

    except Exception as e:
        loggers["acquisition"].error(
            f"Failed to write table for '{title}' to file: {e}\n"
        )


def analyze_device_processes():
    """Write a table of categorized running processes to a file."""
    try:
        # Just to help create folder
        available_functions()
        processes = get_running_processes()

        if not processes:
            loggers["acquisition"].error(
                "No processes retrieved or ADB connection error."
            )
            return

        system_packages = get_system_packages()
        critical_processes, system_apps, unknown_processes = categorize_processes(
            processes, system_packages
        )

        print_processes_table(
            critical_processes,
            "Critical Processes (likely legitimate)",
            output_file_path,
        )
        print_processes_table(
            system_apps, "System Apps (likely legitimate)", output_file_path
        )
        print_processes_table(unknown_processes, "Unknown Processes", output_file_path)

        # Clear the previous content and write new tables to the output file
        open(output_file_path, "a").close()
        
        loggers["acquisition"].info("Process analyzer completed.\n")
        
    except Exception as e:
        loggers["acquisition"].error(
            f"An error occurred while analyzing device processes: {e}"
        )

# FREEZING STUFF

def get_packages_to_suspend():
    """Prompt the user to enter package names to suspend, or skip if left blank."""
    packages = input("\nEnter package names to suspend (comma-separated), or leave blank to skip: ")
    if not packages.strip():
        return []

    # Split input by comma and remove any extra whitespace
    return [pkg.strip() for pkg in packages.split(",") if pkg.strip()]


def get_process_status(package_name):
    """Check if a specified process is running on the device."""
    try:
        output = run_adb_command(
            ["adb", "shell", f"pidof {package_name}"], f"Checking if {package_name} is running"
        )
        
        # Handle None or empty output gracefully
        if output is None or output.strip() == "":
            loggers["acquisition"].info(f"Process '{package_name}' is not running.")
            return False
        else:
            return True

    except Exception as e:
        loggers["acquisition"].error(f"Failed to check status for process {package_name}: {e}")
        return False


def log_process_status(package_name, is_running):
    """Log the running status of the specified process."""
    if is_running:
        loggers["acquisition"].info(f"Process '{package_name}' is currently running.")
    else:
        loggers["acquisition"].info(f"Process '{package_name}' is not running.")


def suspend_device_processes():
    """suspend the specified processes based on user input."""
    loggers["acquisition"].info("Starting process freezing procedure.")
    
    # Retrieve packages to suspend from user input
    packages_to_suspend = get_packages_to_suspend()

    if not packages_to_suspend:
        loggers["acquisition"].info("No packages were selected for freezing. Exiting.")
        return
    
    loggers["acquisition"].info(f"Packages selected for freezing: {packages_to_suspend}\n")

    for package_name in packages_to_suspend:
        loggers["acquisition"].info(f"Checking status for process '{package_name}'.")

        # Check if the process is currently running
        is_running = get_process_status(package_name)
        log_process_status(package_name, is_running)

        if is_running:
            loggers["acquisition"].info(f"Attempting to suspend process '{package_name}'.")
            try:
                # suspend the running process
                run_adb_command(
                    ["adb", "shell", "am", "force-stop", package_name],
                    f"Freezing process: {package_name}"
                )

                # Verify that the process is no longer running
                is_stopped = not get_process_status(package_name)
                if is_stopped:
                    loggers["acquisition"].info(f"Process '{package_name}' has been successfully frozen.")
                    append_to_output_file(output_file_path, f"\nProcess '{package_name}' has been frozen.")
                else:
                    loggers["acquisition"].warning(f"Process '{package_name}' is still running after attempt to suspend.")
                    append_to_output_file(output_file_path, f"\nProcess '{package_name}' is still running; freezing unsuccessful.")

            except Exception as e:
                loggers["acquisition"].error(f"Failed to suspend process '{package_name}': {e}")
        else:
            loggers["acquisition"].info(f"Process '{package_name}' was not running; no action taken.")
            append_to_output_file(output_file_path, f"Process '{package_name}' was not running, no action taken.")

    loggers["acquisition"].info("Process freezing procedure completed.")


def available_functions():
    """List of available functions for freezing processes."""
    try:
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)
            loggers["acquisition"].debug(f"Created directory: {upload_dir}")

        return {
            "get_running_processes": "Retrieve the list of running processes",
            "get_system_packages": "Retrieve the list of system packages",
            "analyze_device_processes": "Retrieve table of categorized processes",
            "suspend_device_processes": "suspend the specified processes based on user input"
        }
        
    except Exception as e:
        loggers["acquisition"].error(
            f"An error occurred while listing available functions: {e}"
        )
        return {}  # Return an empty dictionary if something goes wrong


