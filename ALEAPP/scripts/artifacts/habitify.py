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
from scripts.ilapfuncs import logfunc, tsv, is_platform_windows, open_sqlite_db_readonly, convert_ts_int_to_utc

# Helper function
def parseValues(field, value):
    # Target specific columns that require further processing
    value = value.decode('utf-8')
    # check the column name in the given object response
    if value != "null":
        # remove quotes
        if field == "accentColor":
            value = value[2:-1]
        if field == "logInfo":
            # parse object
            value = literal_eval(value)["type"]
        if (field == "name" or field == "regularly" or field == "templateIdentifier" 
            or field == "createdAt"):
            # remove quotes
            value = value[1:-1]
        if (field == "startDate"):
            # convert unix timestamp to readable timestamp
            value = convert_ts_int_to_utc(int(value))
        if field == "shareLink":
            # remove blackslash escape char in filepath to enable url
            value = value[1:-1].replace("\\","")
    return value

# exported function
def get_habitify(files_found, report_folder, seeker, wrap_text, time_offset):
    
    # store the rows in a array
    data_list_storage = []
    # tables with info: serverCache, trackedQueries

    # for files found based on given paths in __artifacts_v2__
    for file_found in files_found:
        #  save filepath for use later
        file_found = str(file_found)
        # look for the exact file
        if file_found.endswith('habitify.firebaseio.com_default'):
            # open a sqlite db file
            db = open_sqlite_db_readonly(file_found)
            # later passed to ArtifactHtmlReport and displayed in the report
            file_found_storage = file_found
            # needed a dictionary to map
            # each task has a unique id and the entries has the id tagged to its path
            # /habits/EooHQ9HT12Y2tgUlYEcZz6pUEB42/-OAIW_k0a3ejNt__qM-w/accentColor/
            dict = {}
            cursor = db.cursor()
            # write sql statement
            cursor.execute('''
            select 
            path,
	        value
            from serverCache 
            ''')
            # fetchall returns a tuple, to further process the data we have to iterate through the data
            all_rows = cursor.fetchall()
            for row in all_rows:
                path = row[0]
                value = row[1]
                if "/habits/" in path:
                    field = path.split("/")[-2]
                    # the files are stored like /habits/EooHQ9HT12Y2tgUlYEcZz6pUEB42/-OAIW_k0a3ejNt__qM-w/accentColor/
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
                # after processing, append to array which is displayed as table rows later
                data_list_storage.append((id, dict[id]["name"], dict[id]["logInfo"], dict[id]["shareLink"],
                                          dict[id]["regularly"], dict[id]["remind"], dict[id]["templateIdentifier"],
                                          dict[id]["accentColor"], dict[id]["habitType"], dict[id]["iconNamed"], 
                                          dict[id]["isArchived"], dict[id]["priority"], dict[id]["priorityByArea"],
                                          dict[id]["startDate"], dict[id]["targetActivityType"],
                                          dict[id]["targetFolderId"], dict[id]["timeOfDay"],
                                          dict[id]["createdAt"]))
            db.close()

    # if there's any rows fetched, creates the html report
    if data_list_storage:
        # Name of the report, will be displayed at the sidebar
        report = ArtifactHtmlReport('Habitify')
        # Header of report, will be displayed at the top of the report
        report.start_artifact_report(report_folder, 'Habitify')
        report.add_script()
        # the headers for the columns
        data_headers = ("id", "name", "logInfo", "shareLink", 
                        "regularly", "remind", "templateIdentifier", 
                        "accentColor", "habitType", "iconNamed", 
                        "isArchived", "priority", "priorityByArea", 
                        "startDate", "targetActivityType", 
                        "targetFolderId", "timeOfDay", "createdAt")
        # write the table rows with the header, rows, filepath, delimiter
        report.write_artifact_data_table(data_headers, data_list_storage, file_found_storage, html_escape=False)
        report.end_artifact_report()
        # write the tsv file
        tsvname = "Habitify"
        tsv(report_folder, data_headers, data_list_storage, tsvname)
    # no rows fetched, logs can be seen in Report Home 
    else:
        logfunc('No Habitify data available')
