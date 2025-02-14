import asyncio
import csv
import json
import os
import time

from TikTokApi import TikTokApi
from yt_dlp import YoutubeDL

ms_token = os.environ.get("ms_token", None)  # set your own ms_token
DATA_DIR = "data"
USER_LIST_DIR = "data/UserList"


def get_current_timestamp():
    return int(time.time())


def is_within_range(timestamp, days=0, weeks=0, months=0):
    now = time.time()  # Current Unix timestamp
    seconds_range = (days * 24 * 60 * 60) + (weeks * 7 * 24 *
                                             60 * 60) + (months * 30 * 24 * 60 * 60)
    past_limit = now - seconds_range  # Calculate the timestamp limit

    return timestamp >= int(past_limit)


def update_json_file(file_path, new_data):
    try:
        # Read existing data
        with open(file_path, "r", encoding="utf-8") as file:
            existing_data = json.load(file)

        # Ensure it's a list
        if not isinstance(existing_data, list):
            raise ValueError("JSON file does not contain a list.")

    except (FileNotFoundError, json.JSONDecodeError):
        # If file doesn't exist or is empty, start with an empty list
        existing_data = []

    print("Number of existing videos: ", len(existing_data))
    print("Number of new videos: ", len(new_data))
    # Append new data (should be a list of dictionaries)
    existing_data.extend(new_data)

    # Write back the updated data
    with open(file_path, "w") as file:
        json.dump(existing_data, file, indent=3)


def extract_video_contents(username, video_id, download_folder=None):
    video_path = os.path.join(download_folder, f'{username}_{video_id}.mp4')
    if not os.path.exists(video_path):
        try:
            file_path = f'{download_folder}/%(uploader)s_%(id)s.%(ext)s' if download_folder else '%(uploader)s_%(id)s.%(ext)s'
            ydl_opts = {'outtmpl': file_path}
            video_url = f"https://www.tiktok.com/@{username}/video/{video_id}"
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([video_url])
        except Exception as e:
            print(f"Error accessing @{username}/video/{video_id}: {e}")
            return

    # TODO: EXTRACT VIDEO CONTENTS

    # image_captions = []
    # audio_text = ""

    # # Remove video after extracting
    # if os.path.exists(video_path):
    #     os.remove(video_path)
    #     print(f"{video_path} has been deleted.")
    # else:
    #     print("File not found.")

    # return {"image_captions": image_captions, "audio_transcribe": audio_text}


async def get_info_users(usernames, days=0, weeks=0, months=0, download_video=False):
    async with TikTokApi() as api:
        await api.create_sessions(headless=False, ms_tokens=[ms_token], num_sessions=1, sleep_after=3, browser=os.getenv("TIKTOK_BROWSER", "chromium"))
        for username in usernames:
            user = api.user(username)
            user_data = await user.info()
            user_path = os.path.join(DATA_DIR, username)
            os.makedirs(user_path, exist_ok=True)
            with open(f"{user_path}/user_info.json", "w") as f:
                json.dump(user_data, f, indent=3)

            videos = []
            missing_videos = []
            downloaded = 0
            video_count = user_data["userInfo"]["stats"]["videoCount"]
            async for video in user.videos(count=video_count):
                video_data = video.as_dict
                if is_within_range(video_data["createTime"], days=days, weeks=weeks, months=months):
                    try:

                        # # TODO: EXTRACT VIDEO CONTENTS
                        # video_contents = extract_video_contents(video.author.username, video.id)
                        # video_data.update(video_contents)

                        collect_time = {"collectTime": get_current_timestamp()}
                        video_data.update(collect_time)
                        videos.append(video_data)
                        downloaded += 1
                    except Exception as e:
                        print(
                            f"Error accessing @{video.author.username}/video/{video.id}: {e}")
                        missing_videos.append(
                            {"username": video.author.username, "id": video.id, "createTime": video.create_time})
                elif (video_data.get("isPinnedItem") and video_data["isPinnedItem"]):
                    continue
                else:
                    break

            if len(videos) > 0:
                filename = "videos_info.json"
                filepath = os.path.join(user_path, filename)
                update_json_file(filepath, videos)
            if len(missing_videos) > 0:
                filename = "missing_videos_info.json"
                filepath = os.path.join(user_path, filename)
                update_json_file(filepath, missing_videos)

        await api.close_sessions()


if __name__ == "__main__":
    try:
        with open(f"{USER_LIST_DIR}/top_100_noxscore_usernames.csv", "r", encoding="utf-8") as file:
            reader = csv.reader(file)
            usernames = [row[0] for row in reader]  # Convert to a list
    except Exception:
        usernames = []

    start_time = time.time()
    asyncio.run(get_info_users(usernames, months=1))
    end_time = time.time()

    # Calculate the execution time
    execution_time = end_time - start_time
    hours, remainder = divmod(execution_time, 3600)
    minutes, seconds = divmod(remainder, 60)

    # Print the execution time in hours, minutes, and seconds
    print(f"Execution time: {int(hours)}h {int(minutes)}m {seconds:.2f}s")
