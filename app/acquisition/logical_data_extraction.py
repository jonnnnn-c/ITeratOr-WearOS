import os
import hashlib
from app.setup import settings, choices
from app.logs.logger_config import initialize_loggers, run_adb_command, append_to_output_file

# Initialize all loggers
loggers = initialize_loggers()

# Set output folder and output file path
upload_dir = settings.LOGICAL_DATA_EXTRACTION_DIR
output_file_path = os.path.join(upload_dir, "data_extraction_hashes.txt")


def list_directories():
    """List all directories in the ADB file system root."""
    output = run_adb_command(["adb", "shell", "ls", "-d", "/*/"], "Listing all directories")
    directories = [line.strip() for line in output.splitlines() if line.strip()]
    loggers["acquisition"].info(f"Found directories in device: {directories}\n")
    return directories

def hash_adb_path(adb_path):
    """Generate a hash for a file or a folder in the ADB filesystem using sha256sum."""
    try:
        check_command = ["adb", "shell", "test", "-d", adb_path, "&&", "echo", "dir", "||", "echo", "file"]
        result = run_adb_command(check_command, "Checking if path is a directory or file")

        path_type = result.strip() if result else None

        if path_type == 'dir':
            loggers["acquisition"].info(f"Hashing directory: {adb_path}")
            list_command = ["adb", "shell", "find", adb_path, "-type", "f", "-o", "-type", "l"]
            try:
                file_paths = run_adb_command(list_command, "Listing all files in directory")
                if file_paths is None:
                    loggers["acquisition"].warning(f"No files found in directory: {adb_path}. Skipping hashing.")
                    return None
            except Exception as e:
                loggers["acquisition"].error(f"Failed to list files in directory {adb_path}: {e}")
                loggers["acquisition"].warning(f"Skipping hashing for directory: {adb_path}")
                return None

            # Use sha256sum to hash each file in the directory
            file_paths = file_paths.strip().splitlines()  # Split the output into lines
            hash_results = []
            for file_path in sorted(file_paths):
                sha256_command = ["adb", "shell", "sha256sum", file_path]
                file_hash = run_adb_command(sha256_command, f"Calculating hash for file: {file_path}")
                if file_hash:
                    hash_results.append(file_hash.strip().split()[0])  # Get only the hash part
                    loggers["acquisition"].info(f"Hash for {file_path}: {file_hash.strip()}")

            # Combine hashes for all files to create a final directory hash
            combined_hash_input = '\n'.join(hash_results).encode()
            final_hash = hashlib.sha256(combined_hash_input).hexdigest()
            loggers["acquisition"].info(f"Final hash for directory {adb_path}: {final_hash}")
            return final_hash

        elif path_type == 'file':
            loggers["acquisition"].info(f"Hashing file: {adb_path}")
            sha256_command = ["adb", "shell", "sha256sum", adb_path]
            file_hash = run_adb_command(sha256_command, f"Calculating hash for file: {adb_path}")
            if file_hash:
                final_hash = file_hash.strip().split()[0]  # Get only the hash part
                loggers["acquisition"].info(f"Final hash for file {adb_path}: {final_hash}")
                return final_hash

        else:
            raise ValueError("The specified path is neither a directory nor a file.")

    except Exception as e:
        loggers["acquisition"].error(f"Error while hashing {adb_path}: {e}")
        return None

def hash_file(file_path):
    """Generate and log the SHA-256 hash of a file."""
    try:
        hasher = hashlib.sha256()
        with open(file_path, "rb") as f:
            while chunk := f.read(8192):
                hasher.update(chunk)
        file_hash = hasher.hexdigest()
        
        # Log the hash and write it to the output file
        loggers["acquisition"].info(f"Hash for {file_path}: {file_hash}")
        with open(output_file_path, "a") as output_file:
            output_file.write(f"{file_path}: {file_hash}\n")
    except Exception as e:
        loggers["acquisition"].error(f"Failed to hash file {file_path}: {e}")

def hash_folder(folder_path):
    """Generate a hash for a folder based on the hashes of the files inside using sha256sum."""
    try:
        hasher = hashlib.sha256()
        total_files = 0
        total_size = 0

        loggers["acquisition"].info(f"Hashing folder: {folder_path}")
        # Use find to get all files in the folder
        # list_command = ["find", folder_path, "-type", "f"]
        list_command = ["find", folder_path, "-type", "f", "-o", "-type", "l"]
        file_paths = run_adb_command(list_command, "Listing all files in folder")

        if file_paths is None:
            loggers["acquisition"].warning(f"No files found in folder: {folder_path}. Skipping hashing.")
            return None

        # Process each file found
        file_paths = file_paths.strip().splitlines()  # Split output into lines
        hash_results = []
        for file_path in sorted(file_paths):
            # Calculate the hash for each file using sha256sum
            sha256_command = ["sha256sum", file_path]
            file_hash = run_adb_command(sha256_command, f"Calculating hash for file: {file_path}")
            
            if file_hash:
                hash_results.append(file_hash.strip().split()[0])  # Get only the hash part
                file_size = os.path.getsize(file_path)
                total_files += 1
                total_size += file_size
                loggers["acquisition"].info(f"Hash for {file_path}: {file_hash.strip()} (Size: {file_size} bytes)")
            else:
                loggers["acquisition"].warning(f"Failed to read {file_path}.")

        # Combine hashes for all files to create a final folder hash
        combined_hash_input = '\n'.join(hash_results).encode()
        final_hash = hashlib.sha256(combined_hash_input).hexdigest()

        loggers["acquisition"].info(f"Final hash for folder {folder_path}: {final_hash} (Total files: {total_files}, Total size: {total_size} bytes)")
        return final_hash

    except Exception as e:
        loggers["acquisition"].error(f"Error while hashing folder {folder_path}: {e}")
        return None


def extract_folder(path, description):
    """Extract a specific folder from the device."""
    try:
        # Calculate the original hash for the folder before pulling
        original_hash = hash_adb_path(path)
        
        if original_hash is None:
            loggers["acquisition"].warning(f"Skipping extraction for {description} ({path}) due to hash failure.")
            return  # Skip extraction if hashing failed
        
        loggers["acquisition"].info(f"Original hash for {description} ({path}): {original_hash}")

        # Pull the folder from the device
        run_adb_command(["adb", "pull", path, upload_dir], f"Extract {description} ({path})")
        loggers["acquisition"].info(f"{description} extracted from {path}.")

        # Now recalculate the hash for the folder after pulling it
        pulled_folder_path = os.path.join(upload_dir, path.strip("/"), os.path.basename(path))
        pulled_hash = hash_folder(pulled_folder_path)
        loggers["acquisition"].info(f"Recalculated hash for {description} after pull: {pulled_hash}")
        
        # Compare the original hash and the recalculated hash
        if original_hash == pulled_hash:
            loggers["acquisition"].info(f"Hash match: The contents of {description} did not change.")
        else:
            loggers["acquisition"].warning(f"Hash mismatch: The contents of {description} changed.")

    except Exception as e:
        loggers["acquisition"].error(f"Failed to extract {description} from {path}: {e}")


def run_data_extraction():
    """Run data extraction based on user choice."""
    loggers["acquisition"].info("Starting data extraction process.")
    
    # Prompt the user for their choice
    print("Choose an extraction option:")
    print("1 - Important folders")
    print("2 - All directories")
    print("3 - Custom folders")
    choice = input("Enter your choice (1, 2, or 3): ").strip()
    loggers["acquisition"].info(f"User chose option {choice}\n")
    
    # Execute extraction based on the user's choice
    if choice == "1":
        loggers["acquisition"].info("Extracting important folders...")
        
        # Load user settings and retrieve important folders
        user_settings = choices.load_user_settings()
        IMPORTANT_FOLDERS = user_settings.get("important_folders")
        
        for folder in IMPORTANT_FOLDERS:
            extract_folder(folder, "important folder")
    
    elif choice == "2":
        loggers["acquisition"].info("Extracting all directories...")
        all_folders = list_directories()  # Dynamically retrieve all directories
        for folder in all_folders:
            extract_folder(folder, "directory")

    elif choice == "3":
        # List all available directories with numbers
        all_folders = list_directories()  # Dynamically retrieve all directories
        print("Select the directories you want to extract by typing the corresponding numbers.")
        for idx, folder in enumerate(all_folders, start=1):
            print(f"{idx} - {folder}")
        
        # Let the user type the numbers of the directories they want to extract
        selected_numbers = input("Enter the numbers of the directories to extract (comma-separated): ").strip()
        selected_numbers = [int(num) - 1 for num in selected_numbers.split(",")]  # Convert to 0-based index
        
        # Extract the selected folders
        for index in selected_numbers:
            folder = all_folders[index]
            loggers["acquisition"].info(f"Extracting folder {folder}...")
            extract_folder(folder, "custom folder")
    
    else:
        print("Invalid choice. Please enter 1, 2, or 3.")
        loggers["acquisition"].warning("User entered an invalid extraction option.")
        return
    
	# Hash extracted files for integrity
	# Check if the upload directory exists before hashing files
    if os.path.exists(upload_dir) and os.path.isdir(upload_dir):
        loggers["acquisition"].info("Generating hashes for extracted files.")
        for root, dirs, files in os.walk(upload_dir):
            for name in files:
                file_path = os.path.join(root, name)
                hash_file(file_path)
        loggers["acquisition"].info("Data extraction completed with hashes generated.")
    else:
	    loggers["acquisition"].warning(f"The upload directory does not exist: {upload_dir}. Skipping hash generation.")
	

def available_functions():
    """List of available functions for freezing processes and extracting data."""
    try:
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)
            loggers["acquisition"].debug(f"Created directory: {upload_dir}")

        return {
            "list_directories": "List all the directories found on the device",
            "run_data_extraction": "Extract data with user-selected options (important, all, or custom folders)"
        }
    except Exception as e:
        loggers["acquisition"].error(f"An error occurred while listing available functions: {e}")
        return {}  # Return an empty dictionary if something goes wrong

