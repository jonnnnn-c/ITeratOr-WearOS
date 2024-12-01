__artifacts_v2__ = {
    "ZohoNotebook": {
        "name": "Zoho Notebook",
        "description": "Parse Zoho Notebook db files",
        "author": "@MarkCHC",  
        "version": "0.0.1",  
        "date": "2024-10-31",  
        "requirements": "none",
        "category": "Zoho",
        "notes": "testing",
        "paths": ('*/com.zoho.notebook/databases/app_data.db'),
        "function": "get_zohoNotebook"
    }
}

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, is_platform_windows, open_sqlite_db_readonly, convert_ts_int_to_utc

# Helper function
def parseValues(idx, value):
    # Target specific columns that require further processing
    timestamp_columns = [7,8]
    if idx in timestamp_columns and value != None:
        # convert unix timestamp to readable timestamp
        value = convert_ts_int_to_utc(int(value)/1000)
    return value

# exported function
def get_zohoNotebook(files_found, report_folder, seeker, wrap_text, time_offset):

    # store the rows in a array
    data_list_storage = []

    # for files found based on given paths in __artifacts_v2__
    for file_found in files_found:
        #  save filepath for use later
        file_found = str(file_found)
        # look for the exact file
        if file_found.endswith('app_data.db'):
            # open a sqlite db file
            db = open_sqlite_db_readonly(file_found)
            # later passed to ArtifactHtmlReport and displayed in the report
            file_found_storage = file_found
            # write sql statement
            cursor = db.cursor()
            cursor.execute('''
            select
		    Note.*, 
            ZTodo.zTodoId,
		    ZTodo.title, 
            ZTodo.checked,
            "order", 
            ZTodo.remoteId,
            ZTodo.updatedTime
            from Note left join ZTodo 
            on Note.id=ZTodo.noteId 
            ''')
            all_rows = cursor.fetchall()
            # fetchall returns a tuple, to further process the data we have to iterate through the data
            for row in all_rows:
                converted_row = []
                # enumerate it so we can target specfic columns
                for idx, item in enumerate(row):
                    # further process the values with helper function
                    converted_row.append(parseValues(idx, item))
                # after processing, append to array which is displayed as table rows later
                data_list_storage.append(converted_row)
            db.close()

    # if there's any rows fetched, creates the html report
    if data_list_storage:
        # Name of the report, will be displayed at the sidebar
        report = ArtifactHtmlReport('Zoho Notebook')
        # Header of report, will be displayed at the top of the report
        report.start_artifact_report(report_folder, 'Zoho Notebook')
        report.add_script()
        # the headers for the columns
        data_headers = ("id", "noteId", "name", "title", "type", "contentPath", "color", "createdDate", "modifiedDate", 
                        "shortDescription", "isFavouriteNote", "isLocked", "isTrashed", "syncStatus",
                        "zTodoId", "checklistTitle", "checked", "checklistOrder", "checklistRemoteId", "updatedTime")
        # write the table rows with the header, rows, filepath, delimiter
        report.write_artifact_data_table(data_headers, data_list_storage, file_found_storage, html_escape=False)
        report.end_artifact_report()
        # write the tsv file
        tsvname = "Zoho Notebook"
        tsv(report_folder, data_headers, data_list_storage, tsvname)
    # no rows fetched, logs can be seen in Report Home 
    else:
        logfunc('No Zoho Notebook data available')