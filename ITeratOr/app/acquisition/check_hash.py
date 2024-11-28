import os
import subprocess

import hashlib
import subprocess
import os

from app.logs.logger_config import initialize_loggers

# Initialize all loggers
loggers = initialize_loggers()


def escape_special_characters(file_path):
    """Manually escape special characters like |, >, <, etc. with backslashes."""
    # Define a list of special characters to escape
    special_chars = ['|', '>', '<', '&', ';', '$', '(', ')', '{', '}', '`', '*', '?', '[', ']', '!', '"', "'"]
    
    # Escape each special character by adding a backslash before it
    for char in special_chars:
        file_path = file_path.replace(char, '\\' + char)
    
    return file_path

def run_adb_command(command, description=""):
    """Runs a command via subprocess and returns the output as a string."""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            loggers["acquisition"].error(f"Error during {description}: {result.stderr.strip()}")
            return None
        return result.stdout.strip()
    except Exception as e:
        loggers["acquisition"].error(f"Error while running command {description}: {e}")
        return None

def hash_adb_path(adb_path):
    """Generate a hash for a file or a folder in the ADB filesystem using sha256sum."""
    try:
        check_command = f"adb shell test -d {adb_path} && echo dir || echo file"
        result = run_adb_command(check_command)

        if not result:
            loggers["acquisition"].error(f"Failed to determine path type for: {adb_path}.")
            return None

        path_type = result.strip()

        if path_type == 'dir':
            loggers["acquisition"].info(f"Hashing files in adb directory: {adb_path}")
            list_command = f"adb shell find {adb_path} -type f -o -type l"
            file_paths = run_adb_command(list_command)
        
            file_paths = file_paths.splitlines()  # Split string into a list of file paths (if needed)
            hash_results = {}
            
            if file_paths:
                for file_path in sorted(file_paths):
                    # Construct the sha256sum command for ADB
                    escaped_file_path = escape_special_characters(file_path) # shlex.quote safely escapes special characters
                    
                    # Construct the sha256sum command for ADB with the escaped file path
                    sha256_command = f"adb shell sha256sum '{escaped_file_path}'"
                    file_hash = run_adb_command(sha256_command)
                    
                    if file_hash:
                        # Split the output and assign hash to dictionary
                        hash_results[file_path] = file_hash.split()[0]  # Use square brackets for dictionary key-value assignment
            else:
                return False
            
            return hash_results

        elif path_type == 'file':
            loggers["acquisition"].info(f"Hashing files in adb: {adb_path}")
            sha256_command = f"adb shell sha256sum '{adb_path}'"
            file_hash = run_adb_command(sha256_command)
            if file_hash:
                final_hash = file_hash.split()[0]  # Get only the hash part
                return final_hash

        else:
            loggers["acquisition"].error(f"Invalid path type for {adb_path}. It should be a file or directory.")
            return None

    except Exception as e:
        loggers["acquisition"].error(f"Error hashing {adb_path}: {e}")
        return None



def hash_file(file_path):
    """Generate the SHA-256 hash of a file."""
    try:
        loggers["acquisition"].info(f"Hashing files in local: {file_path}")
        hasher = hashlib.sha256()
        with open(file_path, "rb") as f:
            while chunk := f.read(8192):
                hasher.update(chunk)
        file_hash = hasher.hexdigest()
        
        # Print the hash result
        return file_hash
    except Exception as e:
        loggers["acquisition"].error(f"Failed to hash file {file_path}: {e}")
        return None

def hash_folder(folder_path):
    """Generate a hash for a folder based on the hashes of the files inside."""
    try:

        loggers["acquisition"].info(f"Hashing files in local directory: {folder_path}")
        # Use find to get all files in the folder
        list_command = f"find {folder_path} -type f -o -type l"
        file_paths = run_adb_command(list_command)

        if file_paths:
            # Process each file found
            file_paths = file_paths.splitlines()
            hash_results = {}
            for file_path in sorted(file_paths):
                # Calculate the hash for each file using sha256sum
                sha256_command = f"sha256sum '{file_path}'"
                file_hash = run_adb_command(sha256_command)
                
                if file_hash:
                    hash_results[file_path] = file_hash.split()[0]  # Get only the hash part
        else:
            return False

        return hash_results

    except Exception as e:
        loggers["acquisition"].error(f"Error while hashing folder {folder_path}: {e}")
        return None
