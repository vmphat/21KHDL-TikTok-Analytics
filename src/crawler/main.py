import asyncio
import os
import time

import utils

USER_LISTS_DIR = "data/user_lists"

if __name__ == "__main__":
    file_path = os.path.join(USER_LISTS_DIR, "user_list_amthuc.txt")
    usernames = utils.read_usernames_from_file(file_path)

    start_time = time.time()
    asyncio.run(utils.get_info_users(
        usernames, months=12+4, max_retries=5, batch_size=30,  save=True))
    end_time = time.time()

    elapsed_time = end_time - start_time
    hours, remainder = divmod(elapsed_time, 3600)
    minutes, seconds = divmod(remainder, 60)

    print(f"Execution time: {int(hours)}h {int(minutes)}m {seconds:.2f}s")
