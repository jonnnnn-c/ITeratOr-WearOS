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

4. **Generate Directory Hashes**:
   - **Action**: Create hashes for directories.
   - **Reason**: Ensure filesystem integrity.

5. **Logical Data Extraction**:
   - **Action**: Extract relevant data from the device.
   - **Reason**: Capture all persistent data.

6. **Freeze and Suspend Running Processes**:
   - **Action**: Freeze processes using `force-stop` or `disable-user`.
   - **Reason**: Prevent changes during acquisition.

7. **Capture Post-Freeze State**:
   - **Action**: Re-capture system logs post-freezing.
   - **Reason**: Validate the freezing process.

8. **Generate Hashes for Extracted Data**:
   - **Action**: Hash each extracted file/directory.
   - **Reason**: Demonstrate data integrity.

9. **Extract Log Metadata**:
   - **Action**: Collect timestamps and command details.
   - **Reason**: Ensure accountability throughout the acquisition.

## Freezing Processes in Forensics: Necessity and Forensically Sound Approaches

### 1. Forensic Necessity of Freezing Processes
Freezing or stopping processes during acquisition is typically done for the following reasons:

- **Prevent Data Changes**: Ongoing processes can alter or delete critical data, especially volatile data stored in RAM or temporary files.
- **Consistency of State**: Freezing ensures that the data acquisition happens on a stable system without interference from background apps.

However, this also has drawbacks:

- **Alteration of Evidence**: Freezing processes can change the system state. For example, killing a process might cause logs or temporary data to be deleted or modified.
- **Risk of Crashing Essential Services**: Stopping critical system processes can lead to device instability, potentially corrupting evidence.

### 2. When is Freezing Necessary?
Freezing processes is **not always necessary** in digital forensics, but may be essential in these cases:

- **Volatile Data Capture**: If you're capturing volatile data (e.g., data in memory, running apps, network activity), freezing processes can help preserve that data. For example, messaging apps might overwrite data as new messages arrive.
  
- **Preserving App State**: If an app is actively running and interacting with its data (e.g., chat apps or browsers), freezing it can prevent modifications during acquisition.

- **Preventing Remote Wipes or Updates**: Freezing processes (like remote administration tools) may mitigate the risk of remote wiping or updates that could alter or destroy evidence.

### 3. When is Freezing **NOT** Necessary?
In some cases, freezing processes is **not necessary**:

- **Non-Volatile Data Acquisition**: If you're acquiring non-volatile data (e.g., files on disk, databases), the risk of data changes by ongoing processes is lower. It’s often better to avoid freezing unless there's a significant risk of data alteration.
  
- **Read-Only Acquisition**: If you’re working in a read-only mode (e.g., using ADB), freezing processes may not be required.

### 4. Forensically Sound Approach to Freezing Processes
To maintain forensic soundness, freezing processes should be done carefully and selectively. Here’s how:

#### a. Avoid Freezing if Possible
If ongoing processes aren’t actively modifying volatile or critical data, it’s forensically sound to **avoid freezing**. This minimizes the risk of altering the system state unnecessarily.

#### b. Freeze Only Volatile Data Processes
- Target processes that handle volatile data (e.g., messaging apps, browsers).
- **Whitelist System Services**: Avoid freezing critical system services that could cause a system crash or data corruption.

#### c. Document Everything
- **Log every action**: If you freeze processes, document the exact time and reason for doing so.
- **Generate Hashes**: Before and after freezing, generate hashes of critical data directories to ensure you can demonstrate that data wasn’t altered by your actions.

#### d. Use Read-Only Methods First
Before freezing, use **read-only tools** (e.g., ADB in read-only mode) to extract data without altering the file system. Use memory dumpers for capturing volatile data.

#### e. Controlled Freezing with `pm disable-user`
Instead of `force-stop`, use `pm disable-user`, which disables the app without killing it immediately. This method is less invasive and prevents the app from running during acquisition.


## 5. When to Freeze: Decision Framework

1. **Is volatile data critical to the case?**
   - If yes, freezing certain processes may be necessary.
   - If no, freezing may not be needed.

2. **Are the ongoing processes actively altering evidence?**
   - If yes, freezing those processes is advisable.
   - If no, avoid freezing to prevent unnecessary changes.

3. **Is there a risk of remote interference?**
   - If yes, freezing processes related to remote access or control might be necessary to prevent data loss.
   - If no, prioritize a non-invasive acquisition.
