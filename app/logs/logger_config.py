import logging

# Configure logging
def setup_logger():
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s [%(name)s] [%(levelname)s] - %(message)s',
        handlers=[
            logging.StreamHandler(),  # Output to the console
            logging.FileHandler('app.log')  # Optionally, log to a file
        ]
    )
    
    return logging.getLogger()

logger = setup_logger()
