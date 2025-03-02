import asyncio
import csv
import json
import os

from TikTokApi import TikTokApi


async def main():
    # username_list = get_top_100()
    # # Save to CSV file
    # csv_filename = "top_100_most_followers.csv"
    # with open(csv_filename, "w", newline="", encoding="utf-8") as csv_file:
    #     writer = csv.writer(csv_file)
    #     # writer.writerow(["Username"])
    #     for username in username_list:
    #         writer.writerow([username])
    # print(
    #     f"Extracted {len(username_list)} usernames and saved to {csv_filename}")

    # assert (len(username_list) > 0)

    # username_list = []
    # csv_filename = "top_100_most_followers.csv"
    # with open(csv_filename, "r", encoding="utf-8") as csv_file:
    #     reader = csv.reader(csv_file)
    #     # next(reader)  # Skip the header row
    #     username_list = [row[0]for row in reader]

    # set your own ms_token, think it might need to have visited a profile
    ms_token = os.environ.get("ms_token", None)

    async with TikTokApi() as api:
        await api.create_sessions(headless=False, ms_tokens=[ms_token], num_sessions=1, sleep_after=3, browser=os.getenv("TIKTOK_BROWSER", "chromium"))
        user_info_list = []
        missing_users = []
        videos = []
        for username in ["huonggiangofficial"]:
            try:
                print("Processing: ", username)
                user = api.user(username)
                user_data = await user.info()
                user_info_list.append(user_data)

                count = user_data["userInfo"]["stats"]["videoCount"]
                print("Max videos count: ", count)
                count = 300
                video_len_b4 = len(videos)
                async for video in user.videos(count=count):
                    try:
                        videos.append(video.as_dict)
                    except Exception as e:
                        print(f"{video}-{e}")

                print(
                    f"Videos wanted vs actual: {count} - {len(videos)-video_len_b4}")

            except Exception as e:
                print(f"Not found: {username} - Error: {e}")
                missing_users.append(username)

        with open("user_info.json", "w") as f:
            json.dump(user_info_list, f, indent=4)
        with open("missing_user.csv", "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(missing_users)  # Writes the list as a single row
        with open("lebong_videos.json", "w") as f:
            json.dump(videos, f, indent=4)

        print("No. users found: ", len(user_info_list))
        print("No. users not found: ", len(missing_users))

        await api.close_sessions()


if __name__ == "__main__":
    asyncio.run(main())
