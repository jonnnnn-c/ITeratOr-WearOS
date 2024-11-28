import os
import subprocess
import hashlib
from app.setup import settings
from app.logs.logger_config import initialize_loggers, run_adb_command, append_to_output_file

# Initialize all loggers
loggers = initialize_loggers()

# Define paths
output_file_path = os.path.join(settings.OUTPUT_DIR, "extracted_folders")

def list_directories():
    """List all directories in the ADB file system."""
    output = run_adb_command(["adb", "shell", "ls", "-d", "*/"], "Listing all directories")
    directories = [line.strip() for line in output.splitlines()]
    loggers["acquisition"].info(f"Found directories: {directories}")
    return directories

def pull_directory(directory):
    """Pull the specified directory to the output folder."""
    dir_name = os.path.basename(directory)
    output_path = os.path.join(output_file_path, dir_name)

    # Ensure output directory exists
    os.makedirs(output_path, exist_ok=True)

    loggers["acquisition"].info(f"Pulling directory {directory} to {output_path}")
    run_adb_command(["adb", "pull", directory, output_path], f"Pulling directory {directory} to {output_path}")

def compute_hash(directory):
    """Compute the SHA256 hash of all files in the directory."""
    sha256 = hashlib.sha256()
    for root, _, files in os.walk(directory):
        for file in sorted(files):
            file_path = os.path.join(root, file)
            with open(file_path, "rb") as f:
                while chunk := f.read(8192):
                    sha256.update(chunk)
    return sha256.hexdigest()

def main():
    if not os.path.exists(output_file_path):
        os.makedirs(output_file_path)

    directories = list_directories()
    original_hashes = {}
    extracted_hashes = {}

    # Pull each directory and compute its hash
    for directory in directories:
        pull_directory(directory)
        original_hash = compute_hash(directory)
        original_hashes[directory] = original_hash

        # Compute hash for the extracted directory
        #extracted_directory = os.path.join(output_file_path, os.path.basename(directory))
        extracted_directory = os.path.join(output_file_path, "extracted_folders")
        extracted_hash = compute_hash(extracted_directory)
        extracted_hashes[directory] = extracted_hash

        # Compare hashes
        if original_hash == extracted_hash:
            loggers["acquisition"].info(f"Data integrity verified for {directory}.\n\n")
        else:
            loggers["acquisition"].warning(f"Hash mismatch for {directory}!\n\n")
            loggers["acquisition"].warning(f"Original hash: {original_hash}\n\n")
            loggers["acquisition"].warning(f"Extracted hash: {extracted_hash}\n\n")

if __name__ == "__main__":
    main()

