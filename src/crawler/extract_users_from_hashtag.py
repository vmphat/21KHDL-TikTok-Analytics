import asyncio
import json
import os
from utils import *
from TikTokApi import TikTokApi

# Define data directories
USER_LISTS_DIR = "data/user_lists/hashtags"

# Define filtering parameters
MIN_LIKES = 10000
MIN_VIDEOS = 2
MIN_FOLLOWERS = 0

# Define evaluation parameters
TIME_WINDOW_DAYS = 90
MIN_VIDEOS_PER_WEEK = 1
MIN_VIEWS = 0
MIN_ENGAGEMENT_RATE = 0
MIN_VALID_VIDEOS = 0


async def run_pipeline(hashtag_file):
    """Main pipeline to process hashtags, fetch videos, filter users, and evaluate performance."""

    # Step 1: Read hashtags from a file
    hashtags = read_usernames_from_file(hashtag_file)
    hashtags = set(hashtags)
    if not hashtags:
        return

    print(f"📌 Loaded {len(hashtags)} hashtags from {hashtag_file}")

    # Step 2: Fetch videos for each hashtag
    print("\n📥 Fetching videos for hashtags...")
    hashtag_videos = await get_videos_for_hashtags(hashtags, count=1000, save=True)

    # Step 3: Filter users from fetched videos
    print("\n🔍 Filtering users based on video criteria...")
    os.makedirs(USER_LISTS_DIR, exist_ok=True)

    filtered_users = {}
    for hashtag, videos in hashtag_videos.items():
        filtered = filter_users_by_video_criteria(
            videos, MIN_LIKES, MIN_VIDEOS, MIN_FOLLOWERS)
        filtered_users[hashtag] = filtered

        # Save filtered users as text file
        user_list_file = os.path.join(USER_LISTS_DIR, f"users_{hashtag}.txt")
        write_list_to_file(user_list_file, filtered)
        print(f"✅ Saved filtered users to {user_list_file}")

    # Step 4: Evaluate user performance
    print("\n📊 Evaluating user performance...")
    all_filtered_users = list(
        set(user for users in filtered_users.values() for user in users))

    final_users, user_video_stats = await evaluate_user_performance(
        all_filtered_users,
        TIME_WINDOW_DAYS,
        MIN_VIDEOS_PER_WEEK,
        MIN_VIEWS,
        MIN_ENGAGEMENT_RATE,
        MIN_VALID_VIDEOS
    )

    # Save final filtered users
    final_users_txt = os.path.join(USER_LISTS_DIR, "final_filtered_users.txt")
    final_users_json = os.path.join(
        USER_LISTS_DIR, "final_filtered_users.json")

    write_list_to_file(final_users_txt, final_users)
    with open(final_users_json, "w") as f:
        json.dump(user_video_stats, f, indent=4)

    print(f"✅ Final filtered users saved: {final_users_txt}")
    print(f"✅ User performance data saved: {final_users_json}")


if __name__ == "__main__":
    # Input file with hashtags
    hashtag_file = os.path.join(USER_LISTS_DIR, "hashtag_amthuc.txt")
    asyncio.run(run_pipeline(hashtag_file))
