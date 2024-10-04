#!/bin/bash

# Function to check for iwlist and install it if necessary
install_wireless_tools() {
  if ! iwlist --version &> /dev/null; then
    echo "iwlist is not installed. Installing..."

    # Determine Linux distribution and package manager
    if which apt &> /dev/null; then
      sudo apt install -y wireless-tools
    elif which dnf &> /dev/null; then
      sudo dnf install -y wireless-tools
    elif which pacman &> /dev/null; then
      sudo pacman -S --noconfirm wireless-tools
    else
      echo "Unsupported package manager. Please install 'wireless-tools' manually."
      exit 1
    fi
  fi
}

# Check for iwlist, install if needed, and display status
install_wireless_tools

echo "iwlist status: installed - $(command -v iwlist || echo 'Not installed')"