# nmap_scan.py
import subprocess
import logging

loggers = {
    "network": logging.getLogger("network")
}
loggers["network"].setLevel(logging.INFO)

def run_network_command(command):
    """Run a network command without a timeout."""
    try:
        # Run the command without a timeout
        result = subprocess.run(command, capture_output=True, text=True)
        result.check_returncode()  # Check if the command was successful
        return result.stdout
    except subprocess.CalledProcessError as e:
        loggers["network"].error(f"Command failed: {e}")
        return None

def nmap_scan_for_vulnerabilities(ip_address):
    """Scan the IP address for vulnerabilities using nmap."""
    try:
        # Run nmap with common vulnerability scripts
        command = [
            "nmap", "-sV", "--script", "vuln", ip_address
        ]
        result = run_network_command(command)  # No timeout for nmap scan

        # Check if vulnerabilities were found
        if result and "VULNERABLE" in result:
            loggers["network"].warning("Vulnerabilities detected in nmap scan:\n" + result)
            return True
        elif result:
            loggers["network"].info("No vulnerabilities detected in nmap scan.")
            return False
        else:
            loggers["network"].error("Nmap scan failed or returned no output.")
            return False
    except Exception as e:
        loggers["network"].error(f"Error during nmap scan: {e}")
        return False
