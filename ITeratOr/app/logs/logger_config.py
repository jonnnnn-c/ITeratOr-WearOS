import logging
import os
import shutil
import subprocess

# Global variables
log_folder = "output"

# Log files (add more names if needed)
# app.log	Tracks general application activity, such as user menu selections and tool interactions.
# env_setup.log	Records the setup process, verifying that necessary environments like ADB are properly configured.
# network.log	Logs connectivity-related events, including device connections, disconnections, and network security checks.
# acquisition.log	Captures key actions during information gathering, data acquisition, process suspensions, and related activities.
# compress.log	Details the outcomes of compression actions, including errors and successful operations.

log_files = {
    "app.log",
    "env_setup.log",
    "network.log",
    "acquisition.log",
    "compress.log"
}


def logging_formatter():
    return logging.Formatter(
        "%(asctime)s [%(name)s] [%(levelname)s] - %(message)s"
    )


def get_logger_for_file(log_filename):
    """Create a logger that logs to a specific file."""

    # Ensure the 'output' folder exists
    # Create 'output' folder if it doesn't exist
    os.makedirs(log_folder, exist_ok=True)
    # Create the full file path
    log_file_path = os.path.join(log_folder, log_filename)

    # Create a logger
    logger = logging.getLogger(log_filename)

    # If the logger doesn't already have handlers (to prevent duplicate logs)
    if not logger.handlers:
        logger.setLevel(logging.DEBUG)

        # Create handlers (file and console)
        file_handler = logging.FileHandler(log_file_path)
        console_handler = logging.StreamHandler()

        # Create formatters and add to handlers
        formatter = logging_formatter()
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # Add handlers to the logger
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger


def initialize_loggers():
    """Initialize loggers for all log files."""

    # Basically loggers[app] = app.log
    loggers = {
        log_file.split(".")[0]: get_logger_for_file(log_file) for log_file in log_files
    }
    return loggers


# Initialize all loggers
loggers = initialize_loggers()


def clear_output_folder():
    """Clear the contents of all log files in the 'output' folder and reinitialize loggers."""

    # Check if the folder exists
    if os.path.exists(log_folder) and os.path.isdir(log_folder):
        for log_file in log_files:
            file_path = os.path.join(log_folder, log_file)
            if os.path.isfile(file_path):
                with open(file_path, "w"):
                    pass  # This clears the contents of the file
                    loggers["app"].warning(
                        f"Cleared contents within {log_file} file.")

        # Delete all subfolders and their contents within the log folder.
        for subfolder in os.listdir(log_folder):
            full_path = os.path.join(log_folder, subfolder)
            if os.path.isdir(full_path):
                # Delete the directory and its contents
                shutil.rmtree(full_path)
                loggers["app"].warning(
                    f"Deleted the folder and its contents: {subfolder}")


def run_adb_command(command, task, error=True):
    """Function to run ADB commands and handle errors."""
    try:
        # Log task performed
        loggers["acquisition"].info(task)
        result = subprocess.run(
            command,
            check=True,
            text=False,  # default handle as bytes
            capture_output=True
        )

        if "screencap" in command:  # Add other commands that return binary data as needed
            return result.stdout
        else:
            # Log command used for task
            loggers["acquisition"].debug(
                f"[SUCCESS] Command succeeded: {' '.join(command)}\n")
            return result.stdout.decode('utf-8', errors='replace').strip()

    except subprocess.CalledProcessError as e:
        if error:
            loggers["acquisition"].error(
                f"[FAILED] Error while running command: {' '.join(command)}\n")
        else:
            loggers["acquisition"].warning(
                f"[WARNING] Error while running command: {' '.join(command)}\n")
        return None


def run_adb_command_output(command, task, error=True):
    """Function to run ADB commands and handle errors with adb output"""
    try:
        # Log task performed
        loggers["acquisition"].info(task)
        
        subprocess.run(
            command,
            shell=True
        )

        loggers["acquisition"].debug(
            f"[SUCCESS] Command succeeded: {command}")

    except subprocess.CalledProcessError as e:
        if error:
            loggers["acquisition"].error(
                f"[FAILED] Error while running command: {command}\n")
        else:
            loggers["acquisition"].warning(
                f"[WARNING] Error while running command: {command}\n")
        return None


def append_to_output_file(output_file_path, data, action="a", add_newline=True):
    """Append data to the output file with an optional newline."""
    try:
        with open(output_file_path, action) as f:
            if isinstance(data, bytes):
                f.write(data)
            else:
                if add_newline:
                    f.write(data + '\n\n')
                else:
                    f.write(data)
    except Exception as e:
        loggers["acquisition"].error(
            f"Failed to write to file {output_file_path}: {e}")
