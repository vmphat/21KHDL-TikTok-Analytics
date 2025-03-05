import json
import os
import time
from collections import Counter, defaultdict
import asyncio


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
        if not isinstance(new_data, list) or not all(
            isinstance(item, dict) for item in new_data
        ):
            raise ValueError("New data should be a list of dictionaries.")

        # Create a set of unique keys from existing data based on ("author.username", "id")
        existing_keys = {
            (entry.get("author", {}).get("username"), entry.get("id"))
            for entry in existing_data
        }

        # Filter only unique dictionaries not in existing data
        unique_new_data = [
            item
            for item in new_data
            if (item.get("author", {}).get("username"), item.get("id"))
            not in existing_keys
        ]

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
            "outtmpl": f"{download_folder}/%(uploader)s_%(id)s.%(ext)s"}
        video_url = f"https://www.tiktok.com/@{username}/video/{video_id}"
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
    except Exception as e:
        print(f"Error downloading @{username}/video/{video_id}: {e}")


def extract_video_contents(username, video_id, download_folder):
    pass  # Placeholder for future implementation

# --------GET USER INFO AND VIDEOS--------#


async def process_user_videos(user, video_count, user_path, days=0, weeks=0, months=0, save=False):
    """Crawl and return video data for a user. Optionally save to disk if `save=True`."""

    videos, missing_videos = [], []

    try:
        async for video in user.videos(count=video_count):
            video_data = video.as_dict
            if is_within_range(video_data["createTime"], days, weeks, months):
                try:
                    video_data.update({"collectTime": get_current_timestamp()})
                    videos.append(video_data)
                except Exception as e:
                    print(
                        f"Error accessing @{video.author.username}/video/{video.id}: {e}")
                    missing_videos.append(
                        {"username": video.author.username, "id": video.id})

            elif video_data.get("isPinnedItem"):
                continue
            else:
                break
    except Exception as e:
        print(f"Error processing user videos: {e}")
        return videos, missing_videos

    # Save files only if `user_path` is provided
    if user_path and save:
        if videos:
            update_json_file(os.path.join(
                user_path, "videos_info.json"), videos)
        if missing_videos:
            update_json_file(os.path.join(user_path, "missing_videos.json"),
                             missing_videos)

    return videos, missing_videos


async def get_info_user(api, username, days=0, weeks=0, months=0, save=False):
    """Crawl user info and videos. Optionally save data if `save=True`."""
    user_path = os.path.join(
        DATA_DIR, username) if save else None  # Set user path ONCE
    user_info, videos, missing_videos = {}, [], []

    try:
        print(f"\n📥 Processing @{username}...")

        if user_path:
            # Create directory only when `save=True`
            os.makedirs(user_path, exist_ok=True)

        user = api.user(username)
        user_data = await user.info()

        # Get user info safely
        user_info = user_data.get("userInfo", {})

        # Save user info only if `save=True`
        if save and user_path:
            with open(os.path.join(user_path, "user_info.json"), "w", encoding="utf-8") as f:
                json.dump(user_info, f, indent=3)

        video_count = user_info.get(
            "stats", {}).get("videoCount", 0)

        # Fetch user videos (returns full dictionary)
        videos, missing_videos = await process_user_videos(user, video_count, user_path, days, weeks, months, save)

        print(
            f"✅ Done processing @{username} - {len(videos)} videos found.")

    except Exception as e:
        print(f"⚠️ Error processing @{username}: {e}")

    return {"userInfo": user_info, "videos": videos, "missing_videos": missing_videos}


async def get_info_users(usernames, days=0, weeks=0, months=0, max_retries=5, batch_size=30, save=False):
    """Crawl multiple users in batches, retry if needed, and optionally save data."""

    attempt = 0
    missing_users = usernames[:]  # Copy the username list for processing
    user_data = {}  # Dictionary to store user results

    while attempt < max_retries and missing_users:
        print(
            f"\n--- Attempt {attempt + 1}/{max_retries}: {len(missing_users)} users remaining ---")
        attempt += 1
        current_missing_users = []

        # Process users in batches
        for i in range(0, len(missing_users), batch_size):
            # Get a batch of users
            user_batch = missing_users[i:i + batch_size]

            print(
                f"\n📥 Processing batch {i // batch_size + 1} ({len(user_batch)} users)...")

            async with TikTokApi() as api:
                await api.create_sessions(
                    headless=False,
                    ms_tokens=[MS_TOKEN],
                    num_sessions=1,
                    sleep_after=3,
                    browser=os.getenv("TIKTOK_BROWSER", "chromium"),
                )

                # Run batch requests in parallel
                tasks = [get_info_user(
                    api, user, days, weeks, months, save) for user in user_batch]
                results = await asyncio.gather(*tasks)

                await api.close_sessions()

            # Process results and retry failed users
            for username, result in zip(user_batch, results):
                if result["userInfo"] and not result["missing_videos"]:
                    user_data[username] = result
                else:
                    current_missing_users.append(username)

        missing_users = current_missing_users  # Update the retry list

    # Save missing users if retries are exhausted
    if save and missing_users:
        missing_users_path = os.path.join(USER_LISTS_DIR, "missing_users.txt")
        write_list_to_file(missing_users_path, missing_users)
        print(
            f"\n⚠️ Users still missing after retries. Saved to {missing_users_path}.")
    else:
        print("\n✅ All users processed successfully!")

    return user_data  # Return the collected data


# --------GET HASHTAG--------#


async def get_videos_for_hashtag(api, hashtag, count=1000):
    """Fetch videos for a single hashtag using an existing API session."""

    tag = api.hashtag(name=hashtag)
    videos = []

    async for video in tag.videos(count=count):
        videos.append(video.as_dict)

    print(f"✅ Total videos for #{hashtag}: {len(videos)}")
    return videos


async def get_videos_for_hashtags(hashtags, count=1000, save=False):
    """Fetch videos for multiple hashtags concurrently with a single API session."""

    async with TikTokApi() as api:
        await api.create_sessions(
            headless=False,
            ms_tokens=[MS_TOKEN],
            num_sessions=1,
            sleep_after=3,
            browser=os.getenv("TIKTOK_BROWSER", "chromium"),
        )

        # Run all hashtag fetches in parallel using the same `api` session
        tasks = [get_videos_for_hashtag(api, hashtag, count)
                 for hashtag in hashtags]
        results = await asyncio.gather(*tasks)

        await api.close_sessions()  # Close session after fetching

    # Save to file if `save=True`
    if save:
        hashtags_dir = os.path.join(DATA_DIR, "hashtags")
        os.makedirs(hashtags_dir, exist_ok=True)  # Ensure directory exists
        for hashtag, videos in zip(hashtags, results):
            update_json_file(f"{hashtags_dir}/{hashtag}.json", videos)

    # Return a dictionary of hashtag results
    return {hashtag: videos for hashtag, videos in zip(hashtags, results)}

# --------FILTER USERS BY CRITERIA--------#


def get_user_info_from_video(video):
    """Trích xuất thông tin user từ video."""
    username = video.get("author", {}).get("uniqueId")
    user_stats = video.get("authorStats", {})
    return {"username": username, "stats": user_stats}


def filter_users_by_video_criteria(videos, min_likes=0, min_videos=0, min_followers=0):
    """Lọc danh sách user dựa trên số lượng like, số video, và số follower tối thiểu."""

    usernames = []
    users_info = {}

    # **Bước 1: Lọc video có lượt like >= min_likes**
    for video in videos:
        likes = int(video.get("stats", video.get(
            "statsV2", {})).get("diggCount", 0))

        if likes >= min_likes:
            user_data = get_user_info_from_video(video)
            username = user_data["username"]
            user_stats = user_data["stats"]

            if username:
                usernames.append(username)
                if username not in users_info:
                    # Chỉ lưu thông tin user một lần
                    users_info[username] = user_stats

    # **Bước 2: Đếm số video mỗi user**
    usernames_count = Counter(usernames)

    # **Bước 3: Lọc user theo tiêu chí số lượng video và số follower**
    filtered_users = [
        (user, users_info.get(user, {}).get("followerCount", 0))
        for user, count in usernames_count.items()
        if count >= min_videos and users_info.get(user, {}).get("followerCount", 0) >= min_followers
    ]

    # **Bước 4: Sắp xếp danh sách theo số follower giảm dần**
    sorted_users = sorted(filtered_users, key=lambda x: x[1], reverse=True)

    # **Bước 5: Ghi danh sách username vào file nếu cần**
    sorted_usernames = [user[0] for user in sorted_users]

    return sorted_usernames


async def evaluate_user_performance(users, time_window_days=0, min_videos_per_week=0, min_views=0,
                                    min_engagement_rate=0, min_valid_videos=0):
    """Đánh giá hiệu suất của các user dựa trên video của họ."""

    # Fetch all user data concurrently
    user_data = await get_info_users(users, days=time_window_days)

    filtered_users = []
    user_video_stats = defaultdict(list)

    for user, user_dict in user_data.items():
        videos = user_dict["videos"]
        valid_videos = []  # Danh sách video đạt yêu cầu

        for video in videos:
            stats = video.get("stats", video.get("statsV2", {}))
            views = int(stats.get("playCount", 0))
            likes = int(stats.get("diggCount", 0))
            comments = int(stats.get("commentCount", 0))
            shares = int(stats.get("shareCount", 0))

            # Tính tỷ lệ tương tác
            engagement_rate = (likes + comments + shares) / \
                views if views > 0 else 0

            # Kiểm tra điều kiện lọc
            if views >= min_views and engagement_rate >= min_engagement_rate:
                valid_videos.append({
                    "username": user,
                    "id": video["id"],
                    "views": views,
                    "likes": likes,
                    "comments": comments,
                    "shares": shares,
                    "engagement_rate": engagement_rate
                })

        # Tính số lượng video hợp lệ trung bình mỗi tuần
        posting_frequency = len(
            videos) / (time_window_days / 7) if videos else 0
        valid_video_count = len(valid_videos)

        # Lọc user dựa trên tiêu chí hiệu suất
        if posting_frequency >= min_videos_per_week and valid_video_count >= min_valid_videos:
            filtered_users.append(user)
            user_video_stats[user] = {
                "valid_video_count": valid_video_count,
                "videos_per_week": posting_frequency,
                "valid_videos": valid_videos
            }

    return filtered_users, user_video_stats
