import os
import hashlib
from app.acquisition.check_hash import *
from app.setup import settings, choices
from app.logs.logger_config import initialize_loggers, run_adb_command, run_adb_command_output

# Initialize all loggers
loggers = initialize_loggers()

# Set output folder and output file path
upload_dir = settings.DATA_EXTRACTION_DIR
logical_upload_dir = settings.LOGICAL_DATA_EXTRACTION_DIR
physical_upload_dir = settings.PHYSICAL_DATA_EXTRACTION_DIR

# log_output_file_path = os.path.join(log_upload_dir, "data_extraction_hashes.txt")


def list_files_in_directory(item_path):
    """List all files with their full paths in the directory log_acq/{item_path}"""
    full_path = os.path.join("log_acq", item_path)  # Construct the full path
    
    # Check if the path exists
    if not os.path.exists(full_path):
        print(f"The directory {full_path} does not exist.")
        return
    
    # Traverse through the directory
    for root, dirs, files in os.walk(full_path):
        for file in files:
            # Get the full path of the file
            file_full_path = os.path.join(root, file)
            return file_full_path


def is_directory(item_path):
    """Check if a given path is a directory on the device."""
    command = f'adb shell "if [ -d {item_path} ]; then echo dir; else echo file; fi"'
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return result.stdout.strip() == "dir"


def logical_acquisition():
    try:
        """Perform logical acquisition with user choice for pulling all folders, all except excluded, or only important folders."""
        if not os.path.exists(logical_upload_dir):
            os.makedirs(logical_upload_dir)
            loggers["acquisition"].debug(f"Created directory for partition images: {logical_upload_dir}")

        # List the root directory contents
        loggers["acquisition"].info("Listing root directory contents using 'adb shell ls /'")
        root_contents = subprocess.run("adb shell ls /", shell=True, capture_output=True, text=True)
        if root_contents.returncode != 0 or not root_contents.stdout.strip():
            loggers["acquisition"].error("Failed to list root directory. Ensure the device is connected.")
            return

        loggers["acquisition"].info(f"Root directory contents:\n{root_contents.stdout.strip()}")

        # Specify folders to exclude and important folders
        excluded_folders = settings.EXCLUDED_FOLDERS
        important_folders = settings.IMPORTANT_FOLDERS

        # Loop until a valid choice is made
        while True:
            # Display acquisition options to the user
            print("\n" + "=" * 50)
            print("Choose pull option:")
            print("=" * 50)
            print("1. Pull all available files and directories (this might take a long time and could hang on large files)")
            print("2. Pull all files and directories except those listed as excluded (recommended for root directories)")
            print("3. Pull only the most important folders (no root access required)")
            choice = input("Enter your choice (1/2/3): ").strip()

            if choice == "1":
                loggers["acquisition"].info("Selected: Pull everything (all files and directories)")
                items_to_pull = [item.strip() for item in root_contents.stdout.split("\n") if item.strip()]
                break
            elif choice == "2":
                loggers["acquisition"].info(f"Selected: Pull everything except excluded folders ({', '.join(excluded_folders)})")
                items_to_pull = [item.strip() for item in root_contents.stdout.split("\n") if item.strip() and item.strip() not in excluded_folders]
                break
            elif choice == "3":
                loggers["acquisition"].info(f"Selected: Pull only important folders ({', '.join(important_folders)})")
                items_to_pull = []
                for folder in important_folders:
                    if folder.startswith("/"):
                        items_to_pull.append(folder.lstrip("/"))
                    else:
                        items_to_pull.extend([item.strip() for item in root_contents.stdout.split("\n") if item.strip() == folder])
                break
            else:
                loggers["acquisition"].warning("Invalid choice. Please select a valid option.")

        
        print()
        
        # Pull each directory/file individually
        for item in items_to_pull:
            item_path = f"/{item}"  # Ensure absolute path
            local_item_path = os.path.join(logical_upload_dir, item)  # Local path replicates hierarchy

            # Ensure directory structure is replicated for pulling
            os.makedirs(os.path.dirname(local_item_path), exist_ok=True)

            if is_directory(item_path):
                run_adb_command_output(
                    f"adb pull {item_path} {local_item_path}",
                    f"Pulling directory: {item_path}"
                )

                # result_hash_local = hash_folder(f"log_acq{item_path}")
                result_hash_local = hash_folder(f"{logical_upload_dir}{item}")
                result_hash_adb = hash_adb_path(item)

                if result_hash_local:
                    for local_file, local_hash in result_hash_local.items():
                        if local_file in result_hash_adb:
                            if local_hash != result_hash_adb[local_file]:
                                loggers["acquisition"].error(f"Integrity check failed: Hash mismatch")
                                return
                    loggers["acquisition"].info(f"Integrity check passed: Hash match")
                else:
                    loggers["acquisition"].warning(f"Empty folder, no need for integrity check")

            else:
                try:
                    run_adb_command_output(
                        f"adb pull {item_path} {local_item_path}",
                        f"Pulling file: {item_path}"
                    )
                except:
                    print("here")
                
                result_hash_local = hash_file(f"{logical_upload_dir}{item}")
                result_hash_adb = hash_adb_path(item)

                if result_hash_adb == result_hash_local:
                    loggers["acquisition"].info(f"Integrity check passed: Hash match")
                else:
                    loggers["acquisition"].error(f"Integrity check failed: Hash mismatch")
            
            print()
            
    except Exception as e:
        loggers["acquisition"].error(f"Error during physical acquisition: {e}")


def physical_acquisition():
    """Perform physical acquisition by imaging device partitions."""
    try:
        # Ensure output directory exists
        if not os.path.exists(physical_upload_dir):
            os.makedirs(physical_upload_dir)
            loggers["acquisition"].debug(f"Created directory for partition images: {physical_upload_dir}")

        # Fetch partition list
        result = run_adb_command(
            ["adb", "shell", "cat", "/proc/partitions"],
            "Retrieving: partition list"
        )

        loggers["acquisition"].info("Available partitions:")
        loggers["acquisition"].info(f"\n{result}")

        # Parse partitions and create images
        for line in result.strip().splitlines()[2:]:  # Skip header lines
            parts = line.split()
            if len(parts) < 4:
                continue
            partition_name = parts[3]  # Partition name (e.g., mmcblk0p1)
            partition_path = f"/dev/block/{partition_name}"  # Full path on the device
            output_img = os.path.join(physical_upload_dir, f"{partition_name}.img")  # Local image path
            
            command = f'adb shell "su 0 dd if={partition_path}" > "{output_img}"'
            print()
            run_adb_command_output(
                command,
                f"Imaging partition: {partition_name}"
            )

            # Verify integrity with hash comparison
            local_hash = hash_file(output_img)
            adb_hash = hash_adb_path(partition_path)

            if local_hash == adb_hash:
                loggers["acquisition"].info(f"Integrity check passed: Hash match")
            else:
                loggers["acquisition"].error(f"Integrity check failed: Hash mismatch")
    
    except Exception as e:
        loggers["acquisition"].error(f"Error during physical acquisition: {e}")


def run_data_extraction():
    """Run data extraction based on user choice."""
    loggers["acquisition"].info("Starting data extraction process.")
    
    # Define options including a new option for both acquisitions
    options = {
        "1": "Logical Data Acquisition",
        "2": "Physical Data Acquisition",
        "3": "Both Logical and Physical Data Acquisition"  # New option
    }
    
    # Prompt the user for their choice
    while True:
        print("\n" + "=" * 50)
        print("Choose the type of data extraction:")
        print("=" * 50)
        for key, value in options.items():
            print(f"{key} - {value}")
        
        choice = input("Select an option (1, 2, or 3): ").strip()
        
        # Check if the choice is valid
        if choice in options:
            selected_option = options[choice]
            loggers["acquisition"].info(f"User chose: {selected_option}")
            
            # Execute extraction based on the user's choice
            if choice == "1":
                loggers["acquisition"].info("Starting logical acquisition.")
                logical_acquisition()
                break
            
            elif choice == "2":
                loggers["acquisition"].info("Starting physical acquisition.")
                physical_acquisition()
                break
            
            elif choice == "3":
                loggers["acquisition"].info("Starting both logical and physical acquisitions.")
                logical_acquisition()
                physical_acquisition()
                break
            
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")
            loggers["acquisition"].warning("User entered an invalid extraction option.")


def available_functions():
    """List of available functions for freezing processes and extracting data."""
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
        loggers["acquisition"].debug(f"Created directory: {upload_dir}")

    try:
        return {
            "logical_acquisition": "Perform logical acquisition with user choice for pulling which folders",
            "physical_acquisition": "Perform physical acquisition by imaging device partitions"
        }
    except Exception as e:
        loggers["acquisition"].error(f"An error occurred while listing available functions: {e}")
        return {}  # Return an empty dictionary if something goes wrong

