import argparse
import asyncio
import json
import os
import time

from yt_dlp import YoutubeDL

from TikTokApi import TikTokApi

ms_token = os.environ.get("ms_token", None)  # set your own ms_token
VIDEO_DIR = "videos"


def get_current_timestamp():
    return int(time.time())


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


async def get_hashtag_videos(hashtag, count):
    path = os.path.join(VIDEO_DIR, hashtag)
    os.makedirs(path, exist_ok=True)

    async with TikTokApi() as api:
        await api.create_sessions(headless=False, ms_tokens=[ms_token], num_sessions=1, sleep_after=3, browser=os.getenv("TIKTOK_BROWSER", "chromium"))
        tag = api.hashtag(name=hashtag)
        videos = []
        downloaded = 0
        async for video in tag.videos(count=200):
            if downloaded >= count:
                break

            try:
                video_url = f"https://www.tiktok.com/@{video.author.username}/video/{video.id}"
                filename = f"{video.author.username}_{video.id}.mp4"
                filepath = os.path.join(path, filename)
                if os.path.exists(filepath):
                    continue
                else:
                    ydl_opts = {
                        'outtmpl': f'{path}/%(uploader)s_%(id)s.%(ext)s'}

                    with YoutubeDL(ydl_opts) as ydl:
                        ydl.download([video_url])

                    video_info = video.as_dict
                    new_data = {"collectedTime": get_current_timestamp()}
                    video_info.update(new_data)
                    videos.append(video_info)
                    downloaded += 1

            except Exception as e:
                print(
                    f"Error downloading @{video.author.username}/video/{video.id}: {e}")

        if len(videos) > 0:
            filename = "videos_info.json"
            filepath = os.path.join(path, filename)
            update_json_file(filepath, videos)


def main():
    parser = argparse.ArgumentParser(description="TikTok Hashtag Crawler")
    parser.add_argument("hashtag", type=str, help="Hashtag to search for")
    parser.add_argument("num_videos", type=int,
                        help="Number of videos to fetch")

    args = parser.parse_args()
    print(f"🔍 Crawling {args.num_videos} videos for hashtag: #{args.hashtag}")
    asyncio.run(get_hashtag_videos(args.hashtag, args.num_videos))


if __name__ == "__main__":
    main()
