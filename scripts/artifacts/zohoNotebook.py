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
from scripts.ilapfuncs import logfunc, is_platform_windows, open_sqlite_db_readonly, convert_ts_int_to_utc

def parseValues(idx, value):
    timestamp_columns = [7,8]
    if idx in timestamp_columns and value != None:
        value = convert_ts_int_to_utc(int(value)/1000)
    return value

def get_zohoNotebook(files_found, report_folder, seeker, wrap_text, time_offset):

    data_list_storage = []

    for file_found in files_found:
        file_found = str(file_found)
        if file_found.endswith('app_data.db'):
            db = open_sqlite_db_readonly(file_found)
            file_found_storage = file_found
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
            on Note.noteId=ZTodo.noteId 
            ''')
            all_rows = cursor.fetchall()
            for row in all_rows:
                converted_row = []
                for idx, item in enumerate(row):
                    converted_row.append(parseValues(idx, item))
                data_list_storage.append(converted_row)

    if data_list_storage:
        report = ArtifactHtmlReport('Zoho Notebook')
        report.start_artifact_report(report_folder, 'Zoho Notebook')
        report.add_script()
        data_headers = ("id", "noteId", "name", "title", "type", "contentPath", "color", "createdDate", "modifiedDate", 
                        "shortDescription", "isFavouriteNote", "isLocked", "isTrashed", "syncStatus",
                        "zTodoId", "checklistTitle", "checked", "checklistOrder", "checklistRemoteId", "updatedTime")
        # report.write_artifact_data_table(data_headers, data_list_storage, file_found_storage, html_escape=False)
        report.write_artifact_data_table(data_headers, data_list_storage, file_found_storage, html_escape=False)
        report.end_artifact_report()
    
    else:
        logfunc('No Zoho Notebook data available')