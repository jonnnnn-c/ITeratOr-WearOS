import shutil
import subprocess
import sys
from app.logs.logger_config import initialize_loggers

# Initialize all loggers
loggers = initialize_loggers()


def run_command(command):
    """Function to run system commands with error handling"""

    try:
        result = subprocess.run(command, check=True, text=True, capture_output=True)

        # Check for specific error messages in the output (e.g., 'adbd cannot run as root')
        if "cannot run as root" in result.stdout:
            loggers["env_setup"].error(f"Error in command output: {result.stdout.strip()}")
            loggers["env_setup"].error(f"Error while running command: {' '.join(command)}")
            return False  # Explicitly return False if we detect an error in the output
        
        elif "failed to connect" in result.stdout:
            loggers["env_setup"].error(f"Error in command output: {result.stdout.strip()}")
            loggers["env_setup"].error(f"Error while running command: {' '.join(command)}")
            return False  # Explicitly return False if we detect an error in the output

        loggers["acquisition"].info(f"Command succeeded: {' '.join(command)}")
        # loggers["env_setup"].info(result.stdout)
        return result.stdout  # Return True if the command completed successfully

    except subprocess.CalledProcessError as e:
        loggers["env_setup"].error(f"Error while running command: {' '.join(command)}")
        loggers["env_setup"].error(e.stderr)  # This will work as 'e' is defined in the 'except' block
        return False  # Return False if an exception was raised


def setup_required_tools():
    """Check if adb and iwlist are installed, and install them if necessary."""

    # Check and install adb
    if not shutil.which("adb"):
        loggers["env_setup"].info("adb is not installed. Installing...")
        if shutil.which("apt"):
            run_command(["sudo", "apt", "install", "-y", "adb"])
        elif shutil.which("dnf"):
            run_command(["sudo", "dnf", "install", "-y", "adb"])
        elif shutil.which("pacman"):
            run_command(["sudo", "pacman", "-S", "--noconfirm", "android-tools"])
        else:
            loggers["env_setup"].error(
                "Unsupported package manager. Please install 'adb' manually."
            )
            sys.exit(1)
    else:
        loggers["env_setup"].info("adb is already installed.")

    # Check and install iwlist
    if not shutil.which("iwlist"):
        loggers["env_setup"].info("iwlist is not installed. Installing...")
        if shutil.which("apt"):
            run_command(["sudo", "apt", "install", "-y", "wireless-tools"])
        elif shutil.which("dnf"):
            run_command(["sudo", "dnf", "install", "-y", "wireless-tools"])
        elif shutil.which("pacman"):
            run_command(["sudo", "pacman", "-S", "--noconfirm", "wireless-tools"])
        else:
            loggers["env_setup"].error(
                "Unsupported package manager. Please install 'wireless-tools' manually."
            )
            sys.exit(1)
    else:
        loggers["env_setup"].info("iwlist is already installed.")


def enable_adb_root():
    """Function to run 'adb root' to gain root access."""

    loggers["env_setup"].info("Running 'adb root' to gain root access.")
    success = run_command(["adb", "root"])

    if success:
        loggers["env_setup"].info("'adb root' executed successfully.")
        return True  # Return True if the command succeeded
    else:
        loggers["env_setup"].error("'adb root' command failed.")
        return False  # Return False if the command failed
