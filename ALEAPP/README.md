# ALEAPP Development

## 1. Setup environment with Anaconda

1. <b>Download Anaconda</b> https://www.anaconda.com/download

2. <b>Create an environment</b>

    This environment should be different to the one you use in ITeratOr's.

    This environment is created with pip so running `pip install` will default to this environment's pip, and not your PATH if you have pip installed already.
    ```
    conda create -n aleapp pip
    conda activate aleapp
    ```

3. <b>Install the modules for running aleappGUI.py</b>

    Make sure the environment is activated before running the command below.
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

    The following files below are crucial to the compilation:
    - aleapp-file_version_info.txt
    - aleapp.py
    - aleapp.spec
    - hook-plugin_loader.py
    - plugin_loader.py

    Run the following command below<br/>
    ```
    pyinstaller aleapp.spec
    ```    
    Pyinstaller will create a folder `build` that contains the required libraries and `dist` that contains the final executable.


## 5. Using ITeratOr's aleapp.exe

1. <b>Locate aLeapp folder</b>
    - In the Autopsy path eg. `Autopsy-4.21.0/autopsy/`, you will find `aLeapp` folder containing `aleapp.exe`, `LICENSE` and `Version.txt` files.

2. <b>Replace the executable</b>
    - Replace the `aleapp.exe` with the new `aleapp.exe` you have compiled in `dist`.

    - Run Autopsy normally, and it now has the ability to process Habitify, Youtube Music, Zoho Notebook, GPS Navigation (WearOS) artifacts.

    - A folder replica of `aLeapp` that we used can be found in this repository under ALEAPP/aLeapp.

# Writing your own aleapp artifacts

## Our scripts
- ALEAPP/scripts/artifacts/habitify.py
- ALEAPP/scripts/artifacts/youtubeMusic.py
- ALEAPP/scripts/artifacts/zohoNotebook.py
- ALEAPP/scripts/artifacts/gpsNavigation.py

## Template

1. <b>Declaring metadata `__artifacts_v2__`</b>

    At the start of the script, you have to define the metadata for your script. The main function will look for these metadata and collate the functions in `artifacts/`
    ```
    __artifacts_v2__ = {
        "appName": {
            "name": "app name",
            "description": "describe what your script does",
            "author": "@yourname",  
            "version": "x.x.x",  
            "date": "yyyy-mm-dd",  
            "requirements": "none",
            "category": "can be anything",
            "notes": "any notes you want future users to pay attention to",
            "paths": ('*/path/to/app/in/device/filename.filetype'),
            "function": "actual function name"
        }
    }
    ```

2. <b>Imports</b>

    You must import `ArtifactHtmlReport`. 
    
    `ilapfuncs` contain many useful functions that your script might need.

    ```
    from datetime import *
    from scripts.artifact_report import ArtifactHtmlReport
    from scripts.ilapfuncs import logfunc, tsv, is_platform_windows, open_sqlite_db_readonly, convert_ts_int_to_utc
    ```

3. <b>Function</b>

    This is the function you're exporting, all 5 parameters must be there.

    ```get_applicationName(files_found, report_folder, seeker, wrap_text, time_offset)```


4. <b>Generate Report</b>

    These are the lines that generate the report, we have commented our scripts to help you understand better.
    ```
    report = ArtifactHtmlReport('Report Name') # displayed at the sidebar
    report.start_artifact_report(report_folder, 'Report Header') # displayed at the top of the report
    report.add_script()
    data_headers = ("Column A", "Column B", "Column C")
    report.write_artifact_data_table(data_headers, data_list, file_found, html_escape=False)
    report.end_artifact_report()
    ```

# Version
This project is developed using ALEAPP v3.2.3, and the project can be found here:
https://github.com/abrignoni/ALEAPP/releases/tag/v3.2.3

Version of referenced Autopsy (4.21.0) uses ALEAPP v3.1.6

You can pull the latest release from their repository, and replicate the same steps for building the `aleapp.exe`. It will function the same as how we replaced the original Autopsy `aleapp.exe`.