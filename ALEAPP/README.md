# ALEAPP Development

## 1. Setup environment with Anaconda

1. <b>Download Anaconda</b> https://www.anaconda.com/download

2. <b>Create an environment</b>
    ```
    conda create -n aleapp pip
    conda activate aleapp
    ```

3. <b>Install the modules for running aleappGUI.py</b>

    Make sure the environment is activated before running the command below
    ```
    pip install -r requirements.txt
    ```

## 2. Command to run ALEAPP

This command is to run aleappGUI.py which is used for ease of demonstration (and development) of our scripts.
```
python aleappGUI.py
```

Select `/target_images` folder for Directory to parse<br/>
Select `/dump_reports` folder for Output Folder<br/>
Load Profile and select `YT-ZH-HBTFY-GPS-Config.alprofile`<br/>
Click 'Process' to run the extraction

## 3. View report

Click 'Open Report & Close' to view the report.

## 4. Compile executable for Autopsy

1. <b>Install pyinstaller</b>
    ```
    conda install pyinstaller
    ```
    pyinstaller is not in requirements.txt because it will cause version conflicts.

2. <b>Build aleapp.exe</b>

    Run the following command below<br/>
    Pyinstaller will create a folder "/build" that contains the required libraries and "/dist" that contains the final executable.
    ```
    pyinstaller aleapp.spec
    ```

## 5. Using ITeratOr's aleapp.exe

1. In the Autopsy path eg. "Autopsy-4.21.0/autopsy/", you will find "aLeapp" folder containing aleapp.exe, LICENSE and Version.txt files.<br/>

2. Replace the aleapp.exe with the new aleapp.exe you have compiled in "/dist".<br/>

3. Run Autopsy normally, and it now has the ability to process Habitify, Youtube Music, Zoho Notebook, GPS Navigation (WearOS) apps.<br/>

4. A folder replica of aLeapp that we used  can be found in this same directory.

# Original Scripts

- scripts/artifacts/habitify.py
- scripts/artifacts/youtubeMusic.py
- scripts/artifacts/zohoNotebook.py
- scripts/artifacts/gpsNavigation.py

# Version
This project is using ALEAPP v3.2.3, and the project can be found here:
https://github.com/abrignoni/ALEAPP/releases/tag/v3.2.3

Version of referenced Autopsy (4.21.0) uses ALEAPP v3.1.6