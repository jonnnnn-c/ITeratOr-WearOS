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
        "paths": ('*/com.google.android.apps.youtube.music/databases/offline.*.db'), #
        "function": "get_youtubeMusic"
    }
}

from datetime import *
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, is_platform_windows, open_sqlite_db_readonly, convert_ts_int_to_utc

def get_youtubeMusic(files_found, report_folder, seeker, wrap_text, time_offset):

    data_list_storage = {} 
    file_found_storage = []

    for file_found in files_found:
        file_found = str(file_found)
        file_name = file_found.split(".")
        user_id = file_name[-2]
        db = open_sqlite_db_readonly(file_found)
        file_found_storage.append(file_found)
        cursor = db.cursor()

        cursor.execute('''
        select 
        id, channel_id, deleted, saved_timestamp, last_refresh_timestamp, last_playback_timestamp, 
		media_status, preferred_stream_quality, stream_transfer_condition, metadata_timestamp, streams_timestamp,
		offline_source_ve_type, watch_next_proto, video_preview_proto, download_attempts, video_added_timestamp, 
		offline_audio_quality, last_playback_position_timestamp, audio_track_id
        from videosV2
        ''')
        all_rows = cursor.fetchall()
        row_storage = []
        convert =  [3, 4, 5, 9, 10, 15, 17]
        for row in all_rows:
            converted_row = []
            converted_row.append(f"https://www.youtube.com/watch?v={row[0]}&channel={row[1]}")
            for idx, col in enumerate(row):
                if idx in convert and col != None:
                    converted_row.append(convert_ts_int_to_utc(int(col)/1000))
                else:
                    converted_row.append(col)
            row_storage.append(converted_row)
        # multiple users histories
        data_list_storage[user_id] = row_storage
    
    if data_list_storage:
        for idx, user_id in enumerate(data_list_storage.keys()):
            report = ArtifactHtmlReport(f'Youtube Music (Downloads) - {user_id}')
            report.start_artifact_report(report_folder, f'Youtube Music (Downloads) - {user_id}')
            report.add_script()
            data_headers = ("link", "id", "channel_id", "deleted",
                            "saved_timestamp", "last_refresh_timestamp", "last_playback_timestamp", 
                            "media_status", "preferred_stream_quality", "stream_transfer_condition", "metadata_timestamp", 
                            "streams_timestamp", "offline_source_ve_type", "watch_next_proto", "video_preview_proto", "download_attempts", 
                            "video_added_timestamp", "offline_audio_quality", "last_playback_position_timestamp", "audio_track_id")
            report.write_artifact_data_table(data_headers, data_list_storage[user_id], file_found_storage[idx], html_escape=False)
            report.end_artifact_report()

    else:
        logfunc('No Youtube Music (Downloads) available')