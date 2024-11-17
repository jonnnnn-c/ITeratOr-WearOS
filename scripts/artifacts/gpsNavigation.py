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
from scripts.ilapfuncs import logfunc, is_platform_windows, open_sqlite_db_readonly, convert_ts_int_to_utc

def parseValues(idx, value):
    base64_columns = [4]
    timestamp_columns = [0, 6]
    flags_columns = [2]
    flags = {
        1: 'Favourite',
        2: 'History'
    }
    if idx in timestamp_columns and value != None:
        value = convert_ts_int_to_utc(int(value)/1000)
    elif idx in flags_columns and value != None:
        value = flags[value]
    elif idx in base64_columns and value != None:
        value = base64.b64decode(value).decode('utf-8')
    return value

def get_gpsNavigation(files_found, report_folder, seeker, wrap_text, time_offset):
    
    data_list_storage = []
    info_storage = []
    file_found_storage_2 = []

    for file_found in files_found:
        file_found = str(file_found)
        if file_found.endswith('place.db'):
            db = open_sqlite_db_readonly(file_found)
            file_found_storage_1 = file_found
            cursor = db.cursor()
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
            all_rows = cursor.fetchall()
            for row in all_rows:
                converted_row = []
                for idx, item in enumerate(row):
                    converted_row.append(parseValues(idx, item))
                data_list_storage.append(converted_row)
            db.close()

        if file_found.endswith('com_somyac_watch_libbase_info_inforuntime.dat'):
            file_found_storage_2.append(file_found)
            with open(file_found) as f:
                lines = f.readlines()
                temp = [lines[1], lines[2]]
                for col in temp:
                    info_storage.append(col.split("=")[-1])

        if file_found.endswith('com_somyac_watch_gpsnavigation_core_appsettings__hintsettings.dat'):
            file_found_storage_2.append(file_found)
            with open(file_found) as f:
                lines = f.readlines()
                temp = [lines[2]]
                for col in temp:
                    info_storage.append(col.split("=")[-1])

        if file_found.endswith('com_somyac_watch_libbase_location_baselocationengine__settings.dat'):
            file_found_storage_2.append(file_found)
            with open(file_found) as f:
                lines = f.readlines()
                temp = [lines[1], lines[2], lines[3]]
                for col in temp:
                    info_storage.append(col.split("=")[-1])

    if data_list_storage or info_storage:
        if data_list_storage:
            report = ArtifactHtmlReport('GPS Navigation (WearOS)')
            report.start_artifact_report(report_folder, 'GPS Navigation (WearOS)')
            report.add_script()
            data_headers = ("created", "icon", "foundIn", "type", "name", "location", "updated")
            report.write_artifact_data_table(data_headers, data_list_storage, file_found_storage_1, html_escape=False)
            report.end_artifact_report()
        if info_storage:
            report = ArtifactHtmlReport('GPS Navigation (WearOS) - additional information')
            report.start_artifact_report(report_folder, 'GPS Navigation (WearOS) - additional information')
            report.add_script()
            data_headers = ("appStartCount", "appStopCount", "notBuyPro", "altitude", "latitude", "longitude")
            report.write_artifact_data_table(data_headers, [info_storage], ','.join(file_found_storage_2), html_escape=False)
            report.end_artifact_report()

    else:
        logfunc('No GPS Navigation (WearOS) data available')