__artifacts_v2__ = {
    "Habitify": {
        "name": "Habitify",
        "description": "Parse Habitify db files",
        "author": "@MarkCHC",  
        "version": "0.0.1",  
        "date": "2024-10-13",  
        "requirements": "none",
        "category": "Habitify",
        "paths": ('*/co.unstatic.habitify/databases/habitify.firebaseio.com_default'),
        "function": "get_habitify"
    }
}

from ast import literal_eval
from datetime import *
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, is_platform_windows, open_sqlite_db_readonly, convert_ts_int_to_utc

def parseValues(field, value):
    value = value.decode('utf-8')
    if value != "null":
        if field == "accentColor":
            value = value[2:-1]
        if field == "logInfo":
            value = literal_eval(value)["type"]
        if (field == "name" or field == "regularly" or field == "templateIdentifier" 
            or field == "createdAt"):
            value = value[1:-1]
        if (field == "startDate"):
            value = convert_ts_int_to_utc(int(value))
        # if field == "remind":
        #     value = value["timeTriggers"]
        if field == "shareLink":
            value = value[1:-1].replace("\\","")
    return value

def get_habitify(files_found, report_folder, seeker, wrap_text, time_offset):
    
    data_list_storage = []
    # tables: serverCache, trackedQueries

    for file_found in files_found:
        file_found = str(file_found)
        if file_found.endswith('habitify.firebaseio.com_default'):
            db = open_sqlite_db_readonly(file_found)
            file_found_storage = file_found
            dict = {}
            cursor = db.cursor()
            cursor.execute('''
            select 
            path,
	        value
            from serverCache 
            ''')
            all_rows = cursor.fetchall()
            for row in all_rows:
                path = row[0]
                value = row[1]
                if "/habits/" in path:
                    field = path.split("/")[-2]
                    if field in ["accentColor", "habitType", "iconNamed", "isArchived", "logInfo", 
                                 "name", "priority", "priorityByArea", "regularly", "remind", 
                                 "startDate", "targetActivityType", "targetFolderId", "templateIdentifier", 
                                 "timeOfDay", "shareLink", "createdAt"]:
                        id = path.split("/")[-3]
                        if id not in dict.keys():
                            dict[id] = {field: parseValues(field, value)}
                        else:
                            dict[id][field] = parseValues(field, value)
            for id in dict.keys():
                data_list_storage.append((id, dict[id]["name"], dict[id]["logInfo"], dict[id]["shareLink"],
                                          dict[id]["regularly"], dict[id]["remind"], dict[id]["templateIdentifier"],
                                          dict[id]["accentColor"], dict[id]["habitType"], dict[id]["iconNamed"], 
                                          dict[id]["isArchived"], dict[id]["priority"], dict[id]["priorityByArea"],
                                          dict[id]["startDate"], dict[id]["targetActivityType"],
                                          dict[id]["targetFolderId"], dict[id]["timeOfDay"],
                                          dict[id]["createdAt"]))
            db.close()

    if data_list_storage:
        report = ArtifactHtmlReport('Habitify')
        report.start_artifact_report(report_folder, 'Habitify')
        report.add_script()
        data_headers = ("id", "name", "logInfo", "shareLink", 
                        "regularly", "remind", "templateIdentifier", 
                        "accentColor", "habitType", "iconNamed", 
                        "isArchived", "priority", "priorityByArea", 
                        "startDate", "targetActivityType", 
                        "targetFolderId", "timeOfDay", "createdAt")
        report.write_artifact_data_table(data_headers, data_list_storage, file_found_storage, html_escape=False)
        report.end_artifact_report()

    else:
        logfunc('No Habitify data available')
