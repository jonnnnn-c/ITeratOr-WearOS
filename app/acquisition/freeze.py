import subprocess
import sys
from app.logs.logger_config import initialize_loggers

# Initialize all loggers
loggers = initialize_loggers()


def run_adb_command(command):
    """Function to run ADB commands and handle errors."""
    try:
        result = subprocess.run(command, check=True, text=True, capture_output=True)
        loggers["acquisition"].info(f"Command succeeded: {' '.join(command)}")
        loggers["acquisition"].info(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        loggers["acquisition"].error(
            f"Error while running command: {' '.join(command)}"
        )
        loggers["acquisition"].error(e.stderr)
        return False


def freeze_processes():
    """Freeze all running user apps on the device."""
    loggers["acquisition"].info("Freezing all running user applications.")
    result = run_adb_command(["adb", "shell", "am", "kill-all"])
    if result:
        loggers["acquisition"].info("Successfully killed all running apps.")
    else:
        loggers["acquisition"].error("Failed to kill all running apps.")


def disable_bluetooth():
    """Disable Bluetooth to prevent external communication."""
    loggers["acquisition"].info("Disabling Bluetooth.")
    result = run_adb_command(
        ["adb", "shell", "service", "call", "bluetooth_manager", "8"]
    )
    if result:
        loggers["acquisition"].info("Bluetooth disabled successfully.")
    else:
        loggers["acquisition"].error("Failed to disable Bluetooth.")


def disable_location_services():
    """Disable location services to prevent unnecessary updates."""
    loggers["acquisition"].info("Disabling location services.")
    result = run_adb_command(
        ["adb", "shell", "settings", "put", "secure", "location_mode", "0"]
    )
    if result:
        loggers["acquisition"].info("Location services disabled successfully.")
    else:
        loggers["acquisition"].error("Failed to disable location services.")


def stop_background_services():
    """Stop any non-essential background services."""
    loggers["acquisition"].info("Stopping non-essential background services.")
    services_to_stop = [
        "com.google.android.gms",
        "com.android.vending",
    ]  # Example services
    for service in services_to_stop:
        result = run_adb_command(["adb", "shell", "am", "force-stop", service])
        if result:
            loggers["acquisition"].info(f"Successfully stopped {service}.")
        else:
            loggers["acquisition"].error(f"Failed to stop {service}.")


def set_airplane_mode():
    """Enable airplane mode to block all network communication."""
    loggers["acquisition"].info("Enabling airplane mode.")
    result = run_adb_command(
        ["adb", "shell", "settings", "put", "global", "airplane_mode_on", "1"]
    )
    if result:
        loggers["acquisition"].info("Airplane mode enabled.")
        # Broadcast the airplane mode change
        run_adb_command(
            [
                "adb",
                "shell",
                "am",
                "broadcast",
                "-a",
                "android.intent.action.AIRPLANE_MODE",
            ]
        )
    else:
        loggers["acquisition"].error("Failed to enable airplane mode.")


def freeze_device():
    """Freeze the WearOS device to prevent data changes during acquisition."""
    loggers["acquisition"].info("Initiating device freeze process...")

    # Sequentially run the freezing steps
    freeze_processes()
    disable_bluetooth()
    disable_location_services()
    stop_background_services()
    set_airplane_mode()

    loggers["acquisition"].info("Device freeze process completed.")
