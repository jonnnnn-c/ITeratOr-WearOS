import logging
import os

# Global variables
log_folder = "output"

# Log files (add more names if needed)
log_files = {"app.log", "env_setup.log", "preacquisition.log", "dumpsys.log"}


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
        formatter = logging.Formatter(
            "%(asctime)s [%(name)s] [%(levelname)s] - %(message)s"
        )
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


def clean_output_folder():
    """Clear the contents of all log files in the 'output' folder and reinitialize loggers."""

    # Check if the folder exists
    if os.path.exists(log_folder) and os.path.isdir(log_folder):
        for log_file in log_files:
            file_path = os.path.join(log_folder, log_file)
            if os.path.isfile(file_path):
                with open(file_path, "w"):
                    pass  # This clears the contents of the file
