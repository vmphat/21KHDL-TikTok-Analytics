import asyncio
import json
import os
import time

from TikTokApi import TikTokApi
from yt_dlp import YoutubeDL

# Configuration
MS_TOKEN = os.environ.get("ms_token", None)
DATA_DIR = "data/raw/user_amthuc"
USER_LISTS_DIR = "data/user_lists"


def get_current_timestamp():
    return int(time.time())


def is_within_range(timestamp, days=0, weeks=0, months=0):
    now = time.time()
    seconds_range = (days * 86400) + (weeks * 604800) + (months * 2592000)
    return timestamp >= int(now - seconds_range)


def read_usernames_from_file(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return [line.strip() for line in file.readlines() if line.strip()]
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return []
    except Exception as e:
        print(f"Error reading file: {e}")
        return []


def write_list_to_file(file_path, data_list):
    try:
        with open(file_path, "w", encoding="utf-8") as file:
            for item in data_list:
                file.write(str(item) + "\n")
        print(f"Successfully wrote {len(data_list)} items to {file_path}")
    except Exception as e:
        print(f"Error writing to file: {e}")

# def update_json_file(file_path, new_data):
#     try:
#         with open(file_path, "r", encoding="utf-8") as file:
#             existing_data = json.load(file)
#         if not isinstance(existing_data, list):
#             raise ValueError("JSON file does not contain a list.")
#     except (FileNotFoundError, json.JSONDecodeError):
#         existing_data = []

#     print(
#         f"Existing videos: {len(existing_data)}, New videos: {len(new_data)}")
#     existing_data.extend(new_data)

#     with open(file_path, "w", encoding="utf-8") as file:
#         json.dump(existing_data, file, indent=3)


def update_json_file(json_file, new_data):
    """Updates a JSON file with new dictionary entries if they are not already present based on 'author.username' and 'id'."""
    try:
        # Load existing data from JSON file
        if os.path.exists(json_file):
            with open(json_file, "r", encoding="utf-8") as file:
                try:
                    existing_data = json.load(file)
                    if not isinstance(existing_data, list):
                        raise ValueError("JSON file does not contain a list.")
                except json.JSONDecodeError:
                    existing_data = []
        else:
            existing_data = []

        # Ensure new_data is a list of dictionaries
        if not isinstance(new_data, list) or not all(isinstance(item, dict) for item in new_data):
            raise ValueError("New data should be a list of dictionaries.")

        # Create a set of unique keys from existing data based on ("author.username", "id")
        existing_keys = {(entry.get("author", {}).get(
            "username"), entry.get("id")) for entry in existing_data}

        # Filter only unique dictionaries not in existing data
        unique_new_data = [item for item in new_data if (
            item.get("author", {}).get("username"), item.get("id")) not in existing_keys]

        if unique_new_data:
            existing_data.extend(unique_new_data)
            # Save updated data back to JSON file
            with open(json_file, "w", encoding="utf-8") as file:
                json.dump(existing_data, file, indent=3, ensure_ascii=False)
            print(
                f"Added {len(unique_new_data)} new unique records to {json_file}.")
        else:
            print("No new unique records to add.")

    except Exception as e:
        print(f"Error updating JSON file: {e}")


def download_video(username, video_id, download_folder):
    video_path = os.path.join(download_folder, f"{username}_{video_id}.mp4")
    if os.path.exists(video_path):
        return

    try:
        ydl_opts = {
            'outtmpl': f"{download_folder}/%(uploader)s_%(id)s.%(ext)s"}
        video_url = f"https://www.tiktok.com/@{username}/video/{video_id}"
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
    except Exception as e:
        print(f"Error downloading @{username}/video/{video_id}: {e}")


def extract_video_contents(username, video_id, download_folder):
    pass  # Placeholder for future implementation


async def process_user_videos(user, user_path, days=0, weeks=0, months=0):
    user_data = await user.info()

    with open(f"{user_path}/user_info.json", "w", encoding="utf-8") as f:
        json.dump(user_data, f, indent=3)

    videos, missing_videos = [], []
    video_count = user_data["userInfo"]["stats"]["videoCount"]

    async for video in user.videos(count=video_count):
        video_data = video.as_dict
        if is_within_range(video_data["createTime"], days, weeks, months):
            try:
                # download_video(video.author.username,
                #                video.id, f"{user_path}/videos")
                video_data.update({"collectTime": get_current_timestamp()})
                videos.append(video_data)
            except Exception as e:
                print(
                    f"Error accessing @{video.author.username}/video/{video.id}: {e}")
                missing_videos.append(
                    {"username": video.author.username, "id": video.id, "createTime": video.create_time})
        elif video_data.get("isPinnedItem"):
            continue
        else:
            break

    if videos:
        update_json_file(os.path.join(user_path, "videos_info.json"), videos)
    if missing_videos:
        update_json_file(os.path.join(
            user_path, "missing_videos.json"), missing_videos)


async def get_info_users(usernames, days=0, weeks=0, months=0, max_retries=5):
    """Fetches user information from TikTok and retries up to max_retries times for missing users."""

    attempt = 0
    missing_users = usernames  # Start with the full list

    while attempt < max_retries and missing_users:
        print(f"\n--- Attempt {attempt + 1}/{max_retries} ---")
        attempt += 1
        current_missing_users = []

        async with TikTokApi() as api:
            await api.create_sessions(headless=False, ms_tokens=[MS_TOKEN], num_sessions=1, sleep_after=3, browser=os.getenv("TIKTOK_BROWSER", "chromium"))

            for username in missing_users:
                user_path = os.path.join(DATA_DIR, username)
                os.makedirs(user_path, exist_ok=True)
                try:
                    await process_user_videos(api.user(username), user_path, days, weeks, months)
                except Exception as e:
                    print(f"Error processing user @{username}: {e}")
                    current_missing_users.append(username)

            await api.close_sessions()

        # Update the missing users list
        missing_users = current_missing_users

    # If still missing after max attempts, save them
    missing_users_path = os.path.join(USER_LISTS_DIR, "missing_users.txt")
    write_list_to_file(missing_users_path, missing_users)

    if missing_users:
        print(
            f"\nUsers still missing after {max_retries} attempts. Saved to {missing_users_path}.")
    else:
        print("\nAll users processed successfully!")


if __name__ == "__main__":
    file_path = os.path.join(USER_LISTS_DIR, "user_list_amthuc.txt")
    usernames = read_usernames_from_file(file_path)

    start_time = time.time()
    asyncio.run(get_info_users(usernames, months=12+4, max_retries=5))
    end_time = time.time()

    elapsed_time = end_time - start_time
    hours, remainder = divmod(elapsed_time, 3600)
    minutes, seconds = divmod(remainder, 60)

    print(f"Execution time: {int(hours)}h {int(minutes)}m {seconds:.2f}s")
