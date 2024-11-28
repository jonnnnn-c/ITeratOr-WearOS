# ALEAPP Development

1. Setup environment with Anaconda


```
conda create -n aleapp pip
conda activate aleapp
pip install -r requirements.txt
conda install pyinstaller
```

2. Run command

```
python aleappGUI.py
```

Select `/target_images` folder for Directory to parse<br/>
Select `/dump_reports` folder for Output Folder<br/>
Load Profile and select `YT-ZH-HBTFY-GPS-Config.alprofile`<br/>
Click 'Process' to run the extraction

3. View report

Click 'Open Report & Close' to view the report.

4. Compile executable for Autopsy

Run the following command below<br/>
Pyinstaller will create a folder "/build" that contains the required libraries and "/dist" that contains the final executable.
```
pyinstaller aleapp.spec
```

5. Using ITeratOr's aleapp.exe

In the Autopsy path eg. "Autopsy-4.21.0/autopsy/", you will find "aLeapp" folder containing aleapp.exe, LICENSE and Version.txt files.<br/>
Replace the aleapp.exe with the new aleapp.exe you have compiled in "/dist".<br/>
Run Autopsy normally, and it now has the ability to process Habitify, Youtube Music, Zoho Notebook, GPS Navigation (WearOS) apps.<br/>
A folder replica of aLeapp that we used  can be found in this same directory.

# Original Scripts

- scripts/artifacts/habitify.py
- scripts/artifacts/youtubeMusic.py
- scripts/artifacts/zohoNotebook.py
- scripts/artifacts/gpsNavigation.py

# Version
This project is using ALEAPP v3.2.3, and the project can be found here:
https://github.com/abrignoni/ALEAPP/releases/tag/v3.2.3

Version of referenced Autopsy (4.21.0) uses ALEAPP v3.1.6