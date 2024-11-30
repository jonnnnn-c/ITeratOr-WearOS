__artifacts_v2__ = {
    "GPS_Navigation": {
        "name": "GPS Navigation (WearOS)",
        "description": "Parse  files",
        "author": "@MarkCHC",  
        "version": "0.0.1",  
        "date": "2024-11-17",  
        "requirements": "none",
        "category": "GPS",
        "paths": ('*/com.somyac.watch.gpsnavigation/place.db', '*/com.somyac.watch.gpsnavigation/com_somyac_watch_libbase_info_inforuntime.dat', 
                  '*/com.somyac.watch.gpsnavigation/com_somyac_watch_gpsnavigation_core_appsettings__hintsettings.dat', 
                  '*/com.somyac.watch.gpsnavigation/com_somyac_watch_libbase_location_baselocationengine__settings.dat'),
        "function": "get_gpsNavigation"
    }
}

import base64
import json
from ast import literal_eval
from datetime import *
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, is_platform_windows, open_sqlite_db_readonly, convert_ts_int_to_utc

# Helper function
def parseValues(idx, value):
    # Target specific columns that require further processing
    base64_columns = [4]
    timestamp_columns = [0, 6]
    flags_columns = [2]
    flags = {
        1: 'Favourite',
        2: 'History'
    }
    if idx in timestamp_columns and value != None:
        # convert unix timestamp to readable timestamp
        value = convert_ts_int_to_utc(int(value)/1000)
    elif idx in flags_columns and value != None:
        # Rephrase numerical flag with its assigned location name in the app
        value = flags[value]
    elif idx in base64_columns and value != None:
        # decode utf-8 to remove b''
        value = base64.b64decode(value).decode('utf-8')
    return value

# exported function
def get_gpsNavigation(files_found, report_folder, seeker, wrap_text, time_offset):
    
    # store the rows in a array
    data_list_storage = []
    info_storage = []
    file_found_storage_2 = []

    # for files found based on given paths in __artifacts_v2__
    for file_found in files_found:
        #  save filepath for use later
        file_found = str(file_found)
        # look for the exact file
        if file_found.endswith('place.db'):
            # open a sqlite db file
            db = open_sqlite_db_readonly(file_found)
            # later passed to ArtifactHtmlReport and displayed in the report
            file_found_storage_1 = file_found
            cursor = db.cursor()
            # write sql statement
            cursor.execute('''
            select
            created, 
            icon, 
            flags, 
            type, 
            name, 
            location, 
            updated
            from com_somyac_watch_libbase_map_direction_placecom_somyac_watch_libbase_map_direction_place_1
            ''')
            # fetchall returns a tuple, to further process the data we have to iterate through the data
            all_rows = cursor.fetchall()
            for row in all_rows:
                converted_row = []
                # enumerate it so we can target specfic columns
                for idx, item in enumerate(row):
                    # further process the values with helper function
                    converted_row.append(parseValues(idx, item))
                # after processing, append to array which is displayed as table rows later
                data_list_storage.append(converted_row)
            db.close()

        # look for the exact file
        if file_found.endswith('com_somyac_watch_libbase_info_inforuntime.dat'):
            # later passed to ArtifactHtmlReport and displayed in the report
            file_found_storage_2.append(file_found)
            with open(file_found) as f:
                # multi-line, grabbing the values from "key_name_1=value_1, key_name_2=value_2, key_name_3=value_3"
                lines = f.readlines()
                temp = [lines[1], lines[2]]
                for col in temp:
                    info_storage.append(col.split("=")[-1])

        # look for the exact file
        if file_found.endswith('com_somyac_watch_gpsnavigation_core_appsettings__hintsettings.dat'):
            # later passed to ArtifactHtmlReport and displayed in the report
            file_found_storage_2.append(file_found)
            with open(file_found) as f:
                # multi-line, grabbing the values from "key_name_1=value_1, key_name_2=value_2, key_name_3=value_3"
                lines = f.readlines()
                temp = [lines[2]]
                for col in temp:
                    info_storage.append(col.split("=")[-1])

        # look for the exact file
        if file_found.endswith('com_somyac_watch_libbase_location_baselocationengine__settings.dat'):
            # later passed to ArtifactHtmlReport and displayed in the report
            file_found_storage_2.append(file_found)
            with open(file_found) as f:
                # multi-line, grabbing the values from "key_name_1=value_1, key_name_2=value_2, key_name_3=value_3"
                lines = f.readlines()
                temp = [lines[1], lines[2], lines[3]]
                for col in temp:
                    info_storage.append(col.split("=")[-1])

    # if there's any rows fetched, creates the html report
    if data_list_storage or info_storage:
        if data_list_storage:
            # Name of the report, will be displayed at the sidebar
            report = ArtifactHtmlReport('GPS Navigation (WearOS)')
            # Header of report, will be displayed at the top of the report
            report.start_artifact_report(report_folder, 'GPS Navigation (WearOS)')
            report.add_script()
            # the headers for the columns
            data_headers = ("created", "icon", "foundIn", "type", "name", "location", "updated")
            report.write_artifact_data_table(data_headers, data_list_storage, file_found_storage_1, html_escape=False)
            report.end_artifact_report()
            # write the tsv file
            tsvname = "GPS Navigation (WearOS)"
            tsv(report_folder, data_headers, data_list_storage, tsvname)
        if info_storage:
            # Name of the report, will be displayed at the sidebar
            report = ArtifactHtmlReport('GPS Navigation (WearOS) - additional information')
            # Header of report, will be displayed at the top of the report
            report.start_artifact_report(report_folder, 'GPS Navigation (WearOS) - additional information')
            report.add_script()
            # the headers for the columns
            data_headers = ("appStartCount", "appStopCount", "notBuyPro", "altitude", "latitude", "longitude")
            report.write_artifact_data_table(data_headers, [info_storage], ','.join(file_found_storage_2), html_escape=False)
            report.end_artifact_report()
    # no rows fetched, logs can be seen in Report Home 
    else:
        logfunc('No GPS Navigation (WearOS) data available')