import logging
import os

log_folder = 'output'

# Function to get a logger for a specified file
def get_logger_for_file(log_filename):
    """Create a logger that logs to a specific file."""
    
    # Ensure the 'output' folder exists
    os.makedirs(log_folder, exist_ok=True)  # Create 'output' folder if it doesn't exist
    log_file_path = os.path.join(log_folder, log_filename)  # Create the full file path
    
    # Create a logger
    logger = logging.getLogger(log_filename)

    # If the logger doesn't already have handlers (to prevent duplicate logs)
    if not logger.handlers:
        logger.setLevel(logging.DEBUG)

        # Create handlers (file and console)
        file_handler = logging.FileHandler(log_file_path)
        console_handler = logging.StreamHandler()

        # Create formatters and add to handlers
        formatter = logging.Formatter('%(asctime)s [%(name)s] [%(levelname)s] - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # Add handlers to the logger
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger

# Function to initialize all loggers and store them in a dictionary
def initialize_loggers():
    loggers = {
        'app': get_logger_for_file('app.log'),
        'env_setup': get_logger_for_file('env_setup.log'),
        'preacquisition': get_logger_for_file('preacquisition.log'),
        'dumpsys': get_logger_for_file('dumpsys.log')
    }
    return loggers

def clean_output_folder():
    """Clear the contents of all log files in the 'output' folder and reinitialize loggers."""
    
    # Check if the folder exists
    if os.path.exists(log_folder) and os.path.isdir(log_folder):
        for filename in os.listdir(log_folder):
            file_path = os.path.join(log_folder, filename)
            if os.path.isfile(file_path) and filename.endswith('.log'):  # Ensure it's a log file
                with open(file_path, 'w'):  # Open the file in 'w' mode to truncate it
                    pass  # This clears the contents of the file
    
    return initialize_loggers()

    
# clean_output_folder()