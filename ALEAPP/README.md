# ALEAPP Development

1. Setup environment


```
conda create -n aleapp pip
conda activate aleapp
pip install -r requirements.txt
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


# Original Scripts

- scripts/artifacts/habitify.py
- scripts/artifacts/youtubeMusic.py
- scripts/artifacts/zohoNotebook.py
- scripts/artifacts/gpsNavigation.py

# Version
This project is using ALEAPP v3.2.3, and the project can be found here:
https://github.com/abrignoni/ALEAPP/releases

Version autopsy currently uses: ALEAPP v3.1.6