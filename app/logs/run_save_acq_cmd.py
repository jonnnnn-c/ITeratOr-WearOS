import subprocess
import os
from app.logs.logger_config import initialize_loggers
from app.setup import paths

# Initialize all loggers
loggers = initialize_loggers()


def run_adb_command(command, task):
    """Function to run ADB commands and handle errors."""
    try:
        # Log task performed
        loggers["acquisition"].info(task)
        result = subprocess.run(
            command, 
            check=True,
            text=True, 
            capture_output=True
        )
        # Log command used for task
        loggers["acquisition"].info(
            f"[SUCCESS] Command succeeded: {' '.join(command)}\n")
        return result.stdout.strip()

    except subprocess.CalledProcessError as e:
        loggers["acquisition"].error(
            f"[FAILED] Error while running command: {' '.join(command)}\n")
        return None


def append_to_output_file(output_file_path, data, action="a", add_newline=True):
    """Append data to the output file with an optional newline."""
    try:
        with open(output_file_path, action) as f:
            # Write data with or without newline based on the parameter
            if add_newline:
                f.write(data + "\n\n")
            else:
                f.write(data)
    except Exception as e:
        loggers["acquisition"].error(f"Failed to write to file {output_file_path}: {e}")

