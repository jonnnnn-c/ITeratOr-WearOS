__artifacts_v2__ = {
    "YoutubeMusic": {
        "name": "Youtube Music (Downloads)",
        "description": "Parse downloaded Youtube Music files from db",
        "author": "@MarkCHC",  
        "version": "0.0.1",  
        "date": "2024-10-27",  
        "requirements": "none",
        "category": "Youtube",
        "notes": "testing",
        "paths": ('*/com.google.android.apps.youtube.music/databases/offline.*.db'),
        "function": "get_youtubeMusic"
    }
}

from datetime import *
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, is_platform_windows, open_sqlite_db_readonly, convert_ts_int_to_utc

# exported function
def get_youtubeMusic(files_found, report_folder, seeker, wrap_text, time_offset):

    # use dictionary to map multiple accounts information
    data_list_storage = {} 
    #  store account filepath
    file_found_storage = []

    # for files found based on given paths in __artifacts_v2__
    for file_found in files_found:
        #  save filepath for use later
        file_found = str(file_found)
        file_name = file_found.split(".")
        user_id = file_name[-2]
        db = open_sqlite_db_readonly(file_found)
        # append account-specific filepath
        file_found_storage.append(file_found)
        cursor = db.cursor()
        # write sql statement
        cursor.execute('''
        select 
        id, channel_id, deleted, saved_timestamp, last_refresh_timestamp, last_playback_timestamp, 
		media_status, preferred_stream_quality, stream_transfer_condition, metadata_timestamp, streams_timestamp,
		offline_source_ve_type, watch_next_proto, video_preview_proto, download_attempts, video_added_timestamp, 
		offline_audio_quality, last_playback_position_timestamp, audio_track_id
        from videosV2
        ''')
        # fetchall returns a tuple, to further process the data we have to iterate through the data
        all_rows = cursor.fetchall()
        # store the rows in a array
        row_storage = []
        convert =  [3, 4, 5, 9, 10, 15, 17]
        for row in all_rows:
            converted_row = []
            converted_row.append(f"https://www.youtube.com/watch?v={row[0]}&channel={row[1]}")
            for idx, col in enumerate(row):
                if idx in convert and col != None:
                    # convert unix timestamp to readable timestamp
                    converted_row.append(convert_ts_int_to_utc(int(col)/1000))
                else:
                    converted_row.append(col)
            # after processing, append to array which is displayed as table rows later
            row_storage.append(converted_row)
        # multiple users histories
        data_list_storage[user_id] = row_storage
        db.close()

    # if there's any rows fetched, creates the html report
    if data_list_storage:
        for idx, user_id in enumerate(data_list_storage.keys()):
            # Name of the report, will be displayed at the sidebar
            report = ArtifactHtmlReport(f'Youtube Music (Downloads) - {user_id}')
            # Header of report, will be displayed at the top of the report
            report.start_artifact_report(report_folder, f'Youtube Music (Downloads) - {user_id}')
            report.add_script()
            # the headers for the columns
            data_headers = ("link", "id", "channel_id", "deleted",
                            "saved_timestamp", "last_refresh_timestamp", "last_playback_timestamp", 
                            "media_status", "preferred_stream_quality", "stream_transfer_condition", "metadata_timestamp", 
                            "streams_timestamp", "offline_source_ve_type", "watch_next_proto", "video_preview_proto", "download_attempts", 
                            "video_added_timestamp", "offline_audio_quality", "last_playback_position_timestamp", "audio_track_id")
            # write the table rows with the header, rows, filepath, delimiter
            report.write_artifact_data_table(data_headers, data_list_storage[user_id], file_found_storage[idx], html_escape=False)
            report.end_artifact_report()
            # write the tsv file
            tsvname = f'Youtube Music (Downloads) - {user_id}'
            tsv(report_folder, data_headers, data_list_storage[user_id], tsvname)
    # no rows fetched, logs can be seen in Report Home 
    else:
        logfunc('No Youtube Music (Downloads) available')