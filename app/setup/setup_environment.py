import shutil
import subprocess
import sys
from app.logs.logger_config import initialize_loggers  # Import the logging setup function

# Initialize all loggers
loggers = initialize_loggers()


# Function to run system commands with error handling
def run_command(command):
    try:
        result = subprocess.run(command, check=True, text=True, capture_output=True)
        loggers['env_setup'].info(result.stdout)  # Log standard output to app.log
    except subprocess.CalledProcessError as e:
        loggers['env_setup'].error(f"Error while running command: {' '.join(command)}")
        loggers['env_setup'].error(e.stderr)
        sys.exit(1)


# Function to check and install required tools (adb, iwlist)
def setup_required_tools():
    """Check if adb and iwlist are installed, and install them if necessary."""
    # Check and install adb
    if not shutil.which("adb"):
        loggers['env_setup'].info("adb is not installed. Installing...")
        if shutil.which("apt"):
            run_command(["sudo", "apt", "install", "-y", "adb"])
        elif shutil.which("dnf"):
            run_command(["sudo", "dnf", "install", "-y", "adb"])
        elif shutil.which("pacman"):
            run_command(["sudo", "pacman", "-S", "--noconfirm", "android-tools"])
        else:
            loggers['env_setup'].error("Unsupported package manager. Please install 'adb' manually.")
            sys.exit(1)
    else:
        loggers['env_setup'].info("adb is already installed.")

    # Check and install iwlist
    if not shutil.which("iwlist"):
        loggers['env_setup'].info("iwlist is not installed. Installing...")
        if shutil.which("apt"):
            run_command(["sudo", "apt", "install", "-y", "wireless-tools"])
        elif shutil.which("dnf"):
            run_command(["sudo", "dnf", "install", "-y", "wireless-tools"])
        elif shutil.which("pacman"):
            run_command(["sudo", "pacman", "-S", "--noconfirm", "wireless-tools"])
        else:
            loggers['env_setup'].error("Unsupported package manager. Please install 'wireless-tools' manually.")
            sys.exit(1)
    else:
        loggers['env_setup'].info("iwlist is already installed.")

