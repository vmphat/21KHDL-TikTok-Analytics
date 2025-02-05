import subprocess
import sys
import time
import os


def run_crawler(keyword, limit):
    """
    Run the crawler script with given keyword and limit
    Returns True if successful, False otherwise
    """
    try:
        print(f"\nStarting crawler for keyword: {keyword}")

        # Set environment variable for UTF-8 encoding
        my_env = os.environ.copy()
        my_env["PYTHONIOENCODING"] = "utf-8"

        # On Windows, force the console to use UTF-8
        if sys.platform == "win32":
            my_env["PYTHONUTF8"] = "1"

        process = subprocess.run(
            # * Change path to the crawler script
            ['python', 'src/crawler/crawler.py', keyword, str(limit)],
            check=True,
            text=True,
            capture_output=True,
            env=my_env,
            encoding='utf-8'
        )
        print(f"Successfully completed crawler for {keyword}")
        print(process.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running crawler for {keyword}: {e}")
        if e.stderr:
            print(f"Error output: {e.stderr}")
        return False
    except Exception as e:
        print(f"Unexpected error for {keyword}: {e}")
        return False


def main():
    # List of tasks to run sequentially
    tasks = [
        # ********** Thể thao và hoạt động ngoài trời **********
        ("bongda", 50),
        ("vietnamvodich", 50),
        ("ronaldo", 50),
        ("nguyenxuanson", 50),
        ("photography", 50),
        ("thaydoibanthan", 50),
        ("barcelona", 50),
        ("quanghai", 50),
        ("lifestyle", 50),
        ("tienlinh", 50),
        ("fptplay", 50),
        ("championsleague", 50),
        ("kungfu", 50),
        ("footballedit", 50),
        ("basketball", 50),
        ("lamineyamal", 50),

        # ********** Công nghệ và đồ điện tử **********
        ("tainghe", 50),
        ("tainghebluetooth", 50),
        ("sacduphong", 50),
        ("flycam", 50),
        ("tainghekhongday", 50),
        ("sacnhanh", 50),
        ("donghothongminh", 50),
        ("dji", 50),
        ("oppo", 50),
        ("drone", 50),
        ("loamini", 50),
        ("dientu", 50),
        ("goojodoq", 50),
        ("sacdienthoai", 50),
        ("iphonetricks", 50),
        ("smartwatch", 50),
        ("banphimco", 50),
    ]
    # Set console to UTF-8 mode on Windows
    if sys.platform == "win32":
        os.system("chcp 65001")

    total_tasks = len(tasks)
    completed_tasks = 0

    for keyword, limit in tasks:
        completed_tasks += 1
        print(f"\n[{completed_tasks}/{total_tasks}] Running task for: {keyword}")

        if run_crawler(keyword, limit):
            print(f"Completed {completed_tasks} of {total_tasks} tasks")
        else:
            print(f"Task failed for {keyword}. Continuing with next task...")

        # Add a small delay between tasks to prevent any potential issues
        if completed_tasks < total_tasks:
            time.sleep(2)


if __name__ == "__main__":
    print("Starting sequential crawler execution...")
    main()
    print("\nAll tasks completed!")
