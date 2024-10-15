# Forensic Acquisition Process for WearOS Devices

### 1. Freezing Processes
- **Objective**: Ensure all active processes are completely halted to prevent changes during acquisition.
- **Improvement**: Consider pausing or suspending network services to prevent external data updates.

### 2. RAM Capture Tools
- **Objective**: Use forensic-sound tools for RAM extraction.
- **Recommendations**: Utilize tools like **Volatility** or **LiME (Linux Memory Extractor)** for reliable results in an emulated environment.

### 3. Hashing
- **Objective**: Ensure data integrity during acquisition.
- **Improvement**: 
  - Generate hashes for entire filesystems when feasible.
  - For larger directories, hash individual files to monitor changes granularly.
  - Use stronger hashing algorithms like **SHA-256** instead of **MD5**.

### 4. Logs and Timestamps
- **Objective**: Capture essential log data for validation.
- **Improvement**: Log error conditions and system resource usage (CPU, memory) during acquisition to verify process integrity.

### 5. Integrity of the Acquisition Process
- **Objective**: Validate that acquired data matches original hashes.
- **Improvement**: Implement post-acquisition checks for both volatile and non-volatile data integrity.

## Considerations for Using `adb` Commands

### Using `disable-user` for Freezing Apps
- **Effect**: Disables the app for the user, halting processes and services.
- **Drawbacks**:
  - Modifies system state, potentially seen as tampering.
  - Risks data loss from app state saving or background task clearing.
  - Requires re-enabling apps post-analysis.
  
### Process Freezing with Root
- **Command**: Use commands like `kill` for more granular freezing.
- **Note**: Rooting the device may alter the system state and can be viewed as a tampering action.

## Use Case Considerations for `adb backup`
- **User Data Focus**: Useful for acquiring app data and user profiles, especially on non-rooted devices.
- **Root Access**: On rooted devices, consider other methods like `adb pull` for comprehensive data acquisition.
- **Time Efficiency**: `adb backup` can quickly gather data without manual targeting.

## Physical Acquisition of Device Storage
**Key Partitions to Target**:
- `/system`: Contains Android OS.
- `/data`: User apps and data.
- `/cache`: Temporary data and logs.
- `/recovery`: System recovery data.
- `/boot`: Kernel and bootloader.

## Challenges and Responses

1. **Changes to System Logs**:
   - **Challenge**: Actions like freezing apps generate log entries.
   - **Response**: Document every action to justify its necessity.

2. **Altering Device State**:
   - **Challenge**: Freezing processes changes the device’s live state.
   - **Response**: Justify alterations as necessary for data preservation.

3. **Preservation of Volatile Data**:
   - **Challenge**: Freezing methods may cause volatile data loss.
   - **Response**: Capture volatile data before freezing.

4. **Potential for App Reboots or Self-Restarts**:
   - **Challenge**: Some apps may restart after being force-stopped.
   - **Response**: Use airplane mode to prevent data syncs during freezing.

5. **Impact of Airplane Mode on Device State**:
   - **Challenge**: Airplane mode alters connectivity settings.
   - **Response**: Justify it as a precaution against external interference.

6. **Disabling System Services or Apps**:
   - **Challenge**: May disrupt system behavior.
   - **Response**: Use as a last resort and document reasons.

7. **Maintaining Chain of Custody**:
   - **Challenge**: Changes may raise custody concerns.
   - **Response**: Maintain detailed records of all actions taken.

## Order of Operations for Acquisition

1. **Initial Documentation and Device State**:
   - **Action**: Document device state (screenshots, logs).
   - **Reason**: Establish a baseline of the original state.

2. **Isolate the Device (Network Disable/Airplane Mode)**:
   - **Action**: Enable airplane mode or disable network interfaces.
   - **Reason**: Prevent external interference.

3. **Capture Volatile Data (RAM and Processes)**:
   - **Action**: Capture RAM contents and running processes.
   - **Reason**: Preserve ephemeral information.

4. **Freeze and Suspend Running Processes**:
   - **Action**: Freeze processes using `force-stop` or `disable-user`.
   - **Reason**: Prevent changes during acquisition.

5. **Generate Directory Hashes**:
   - **Action**: Create hashes for directories.
   - **Reason**: Ensure filesystem integrity.

6. **Logical Data Extraction**:
   - **Action**: Extract relevant data from the device.
   - **Reason**: Capture all persistent data.

7. **Capture Post-Freeze State**:
   - **Action**: Re-capture system logs post-freezing.
   - **Reason**: Validate the freezing process.

8. **Generate Hashes for Extracted Data**:
   - **Action**: Hash each extracted file/directory.
   - **Reason**: Demonstrate data integrity.

9. **Extract Log Metadata**:
   - **Action**: Collect timestamps and command details.
   - **Reason**: Ensure accountability throughout the acquisition.