# ITeratOr


## How to run

1. Run setup.sh to install the required packages on Linux.

    ```
    sudo chmod +x setup.sh
    ./setup.sh
    ```

2. Start app

    ```
    python3 ./main.py (-p | -e)
    
    -p  Use physical watch
    -e  Use emulated watch

## When developing
- separate everything into folders and functions to make development easier
- use the logger.info or logger command to note each critical setp or command used during script execution
    - https://docs.python.org/3/howto/logging.html

## Setting up environment
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