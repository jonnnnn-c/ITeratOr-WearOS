# ITeratOr
A.	Overview

- Our project consists of three phases: pre-acquisition, acquisition, and analysis. ITeratOr, our tool, manages the pre-acquisition and acquisition stages, while the analysis phase aims to enhance existing ALEAPP technology. We assume the smartwatch is already rooted due to technical constraints; otherwise, disassembly would be necessary. Additionally, we will only access the watch, which is assumed to be unlocked, without interfacing with the paired phone.

B.	Pre-Acquisition Phase

- Before analysis begins, the smartwatch must connect to the same network as the forensic machine. To ensure the network's security, our tool conducts a series of checks to verify connection integrity. These checks include confirming robust encryption protocols, such as WPA2-Enterprise or WPA2-Personal, the router's firmware version, and logging network activity for accountability. Moreover, our tool continuously monitors the network for unauthorized devices, particularly during on-site acquisitions, to mitigate risks of tampering or evidence destruction, such as if another device attempts to access or delete data from the watch.

- Tests will be carried out on a physical WearOS watch, where two test scenarios will be simulated: one secure and one unprotected network. This aims to validate the tool’s capabilities in distinguishing between different network security and offer advice to users on possible actions if the network is insecure.

C.	Acquisition Phase

- To ensure data integrity, we modelled our strategy demonstrated by earlier researchers, prioritizing the capture of volatile data, such as RAM contents, first [13]. After this, we attempt to freeze and suspend all running processes to prevent unintended changes. This is done after the memory capture to avoid inadvertent memory changes. Directory hashes will be generated for all parent directories prior to performing a logical backup, establishing a baseline for the device's original state.

- Once the baseline is established, the tool will extract essential artifacts, including data partition dumps, parent and its subdirectories, and user profiles from the smartwatch. For each extraction, the program generates a file or directory hash to confirm that it remains unaltered. At the end of the acquisition, log file metadata with timestamps for all executed instructions will be extracted, ensuring accountability throughout the process.

- Tests will be transitioned to an emulated WearOS environment, which allows us to root the device and access additional features required by our tool. Hash value checks will be performed before and after executing commands to ensure system integrity and prevent unauthorized alterations. Artifacts acquired from our sample will be evaluated using open-source resources to ensure their validity. Additionally, artifacts will be cross-referenced with our test scenario to verify that our tool successfully extracted the appropriate artifacts.

D.	Analysis Phase

- In the analysis phase, we aim to enhance ALEAPP’s capabilities by developing new scripts to parse additional applications that are currently unsupported. Due to time constraints, we will prioritize parsing four popular applications from the Play Store that offer valuable insights, such as note-taking and GPS data utilities. By integrating this data into ALEAPP, we will provide analysts with a more comprehensive and actionable dataset, enabling deeper analysis of data from commonly used applications by smartwatch owners. Our objective is to augment existing analytical tools rather than create an entirely new solution.
    
- For testing, applications on the watch will be populated with realistic sample data to reflect actual usage patterns. Data will first be parsed into the ALEAPP GUI, where it will subsequently be accessed.


## Getting started
1. Run a Linux Virtual Environment with 'Virtualize Intel VT-x/EPT or AMD-V/RVI' enabled.
    
    https://www.reddit.com/r/vmware/comments/k7hd4z/virtualized_amdvrvi_is_not_supported_on_this/

2. Clone the repository
    ```
    git clone https://github.com/jonnnnn-c/digital-forensic.git
    ```

3. Download requirements.txt
    ```
    pip install -r requirements.txt
    ```

4. Setup GENAPI key for freeze process function (OPTIONAL)
    
    https://aistudio.google.com/app/apikey
    
    - Sign in to your google account
    - Click "Create API key"
    - Click "Create API key in new project"
    - Copy api key and put it `settings.py` file, under `GENAI_API_KEY`

5. Start app
    ```
    usage: main.py [-h] (-p | -e) [-i INTERFACE] [--clear-logs]

    Choose between physical or emulated watch connection.

    options:
    -h, --help            show this help message and exit
    -p, --physical        Use physical watch
    -e, --emulated        Use emulated watch
    -i INTERFACE, --interface INTERFACE
                          Specify network interface for physical watch (default is wlan0)
    --clear-logs          Clear all log files in the output folder
    ```


## Setting up android environment
1. Create emulators in Android Studio:
- `x1 Android phone` (e.g., Medium Phone, VanillaIceCream)
- `x1 WearOS watch` (e.g., Wear OS Large Round, UpsideDownCake)
- <b>Note:</b> Use images in <b>"recommended</b> section for the phone if not you would not be able to pair with the watch

2. Start up the watch using the following command:
    ```
    emulator -avd <AVD_NAME e.g., Wear_OS_Large_Round_API_34> -writable-system
    ```

3. In another terminal, perform the following command:
    ```
    # elevated privileges (root) to aid with app troubleshooting
    adb root

    # enable writable system
    adb remount
    
    # after remount need reboot
    adb reboot
    ```

4. In another terminal, start up the phone with the same command previously mentioned (step 2)

5. Setup all the necessary information needed on both devices for simulation.

6. Next, setup a snapshot so it's easier to do testing. Stop the phone.

7. Perform the following commands for the watch to save a snapshot of its current state.
    ```
    # will always take the single current running AVD instance, cannot specify which one
    adb emu avd snapshot save <SNAPSHOT_NAME e.g. snap_1>

    # checking if snapshot is loadable
    emulator -avd Pixel_8_Pro_API_34 -check-snapshot-loadable <SNAPSHOT_NAME e.g. snap_1>
    ```
8. To load the device with its snapshot:
    ```
    # Start from snapshot
    emulator -avd <AVD_NAME> -writable-system -snapshot <SNAPSHOT_NAME e.g. snap_1>
    ```


## Setup Wireless Debugging (on physical & emulated) 
- Enable Developer Mode
    ```
    Settings > System > About > Versions > Build Number (press 7 times)
    ```
- Enable Wireless Debugging
    ```
    Settings > Developer options > Wireless debugging 
    ```


## Faking Package / Process
You can choose one of the following methods to simulate a running package or process on a WearOS device:

### Running a Background Process in ADB Shell
To create a simple infinite loop that outputs a message, use the following command in the ADB shell:

```
adb shell "while true; do echo 'Fake process running'; sleep 60; done" &
```
This command will continuously print "Fake process running" every 60 seconds, allowing you to simulate a background process effectively.

### 2. Setting Up a Fake App
To create a fake app that mimics legitimate behavior on your WearOS device, follow these steps:

1. <b>Create an Empty Wear App in Android Studio:</b>

    - Start a new project in Android Studio and select "Wear OS" as the application type.

2. <b>Modify the App Details:</b>

    - Name: Set the app name to fakewearos (or a name of your choice).
    - Package Name: Change the package name to com.google.fakewearos.
        - This choice helps the app blend in with existing packages, making it appear more legitimate compared to the default package name com.example.fakewearos.

3. <b>Rename the Package (if needed):</b>
    - If you need to rename the package again, refer to this helpful guide: Rename Package in Android Studio.

### 3. Installing an App from the Google Play Store on the Watch
To install apps directly from the Google Play Store on your WearOS watch, follow these steps:

1. <b>Pair Your Watch with a Phone:</b>

    - Use Android Studio to ensure your WearOS watch is properly paired with an Android phone.

2. <b>Sign In to Your Google Account:</b>

    - On your watch, sign in with your Google account. This process will prompt you to continue on your phone for verification.

3. <b>Download Apps from the Watch:</b>

    - Once your account is set up, you can browse and download any compatible apps directly from the Google Play Store on your watch.


## When developing
- Separate everything into folders and functions to make development easier
- Use the logger.info or logger command to note each critical setp or command used during script execution
    - https://docs.python.org/3/howto/logging.html


## Log files

The following log files, located in the 'output' folder, provide useful information about what happened when the tool ran. It captures critical details about the activities that took place during its execution, allowing us to better understand what happened at each stage.

| **Log File**           | **Description**                                                   |
|------------------------|-------------------------------------------------------------------|
| `app.log`              | General app activity (e.g., menu selections, user actions).       |
| `env_setup.log`        | Environment setup details (e.g., ADB present).                    |
| `network.log`          | Device connection-related events (e.g., connect, disconnect, network security check).|
| `acquisition.log`      | Actions during acquisition (e.g., memory dumps, process freezing, file extraction). |