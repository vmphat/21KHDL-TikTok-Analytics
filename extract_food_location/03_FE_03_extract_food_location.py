# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.16.7
#   kernelspec:
#     display_name: .venv
#     language: python
#     name: python3
# ---

# # Install package
#

# +
# # !pip install -q -U google-genai
# -

# # Import library
#

# +
from typing import List
import os
import pandas as pd
import numpy as np
from tqdm import tqdm
import json
import re
from google import genai
from google.genai import types
import time
from typing import Dict, Any, Optional, List
import random
import asyncio

# Show all columns
pd.set_option('display.max_columns', None)

# +
# Folder to store the name of food and location in the video
FOOD_LOCATION_FOLDER = 'food_location'

# Check if the folder exists
if not os.path.exists(FOOD_LOCATION_FOLDER):
    os.makedirs(FOOD_LOCATION_FOLDER)
# -

# # Đọc dữ liệu vào dataframe
#

# +
# Load data from parquet file
# video_df = pd.read_parquet("top_20_percent_weekly_videos_transcripts.parquet")
video_df = pd.read_parquet("small_weekly_videos_transcripts.parquet")

# # Sort data by "statsV2.playCount" in descending order
# # then reset the index to start from 0
# video_df = video_df.sort_values(
#     by="statsV2.playCount",
#     ascending=False
# ).reset_index(drop=True)

video_df.info()
# -

# # Chuẩn bị xử lý dữ liệu
#

video_id_range = range(video_df.shape[0])[0:20_000]
video_id_range

# # Danh sách các API để chạy luân phiên
#

# +
api_list = [
    # "AIzaSyCgr0Af_ph5vvql_VXpyIwfumJOaehbLDo",  # vmphat.24
    "AIzaSyAAmXLg2yM3Ygz3B_HYC4fcE1iJDNFhxm0",  # pvminh
    "AIzaSyAB9vrQbQPxOp1tbYWN9hjmmmno-9uGwR0",  # ngocquynh
    "AIzaSyCArspeWWKenZy4QSQlpBIrUAnXCWPRr90",  # kiet
    "AIzaSyBMcY_CGvsXGJSOMu3vLfWsd4-qL0bQflg",  # franie
    "AIzaSyAL9WZ2mO88O6DuwivJJWK2oqcy9_UXBNQ",  # daniel
    "AIzaSyDrD1yVeRW85VxX433JKFxKbtFuQ83UhMo",  # tulin
    "AIzaSyA8DDmJgizVgSiE2MdjnVpDZEXqTjEgBRg",  # martin

    # "AIzaSyAcvcAtAlMW4QD1OzCoIsmZl04qjFZ_AZo",  # khdludteam5
    # "AIzaSyCbs_KHkUr-BWL9X6_06kZb3brG7UI1a6w",  # vmphat21

    "AIzaSyBrTgG4YDzJMuK9WknMTbdnnoskSX1nvMY",  # pr

    # "AIzaSyDyjL0w1m1dWCNOP7_9UYXDQnNOqbAdbCw",  # vmphat.24
    "AIzaSyAHiAgc7tIuq4YKtswB-AaHa0W9eqQ5jGw",  # pvminh
    "AIzaSyCnUToo7FRJn8v3BwMOt3FWwrDDFf2b4UI",  # ngocquynh
    "AIzaSyCAnhUoYz6YAYCSfSFF-JmGNbMdxzhDKYU",  # kiet
    "AIzaSyBqu4Xbby4sc0vsCUbxhjqYcqOwKKAwaT4",  # franie
    "AIzaSyDh32FdRtHzuRUaZUXafcmlPHqYQtbRx3A",  # daniel
    "AIzaSyBRhc3Q6rdz3Ok93V5xB76Lfk3mNtdzQEI",  # tulin
    "AIzaSyDPUFWmBABBPAYEa_lOkeony8C2eqKkXTw",  # martin
    "AIzaSyAY8nfoP7DXfL571ovT8V_HlMWCTdHqdgc",  # khdludteam5
    "AIzaSyC4WprE1HsmCUwOoGi4HFfA1Lzg5XSE0Cg",  # vmphat21

    "AIzaSyC-letXWg8hVdOA8H6BlEXb-TXF7W7twQM",
    "AIzaSyCmJQlfuGKf2FNvrUWYd-fPuxYRcmm3p4Q",
    "AIzaSyDlKoywc1dVIaiv4UGVDc0OuaEBFluS2IU",
    "AIzaSyDk5UZkrHP6H3fgAI0FidWJKcVptQdEWBE",
    "AIzaSyBkVUkCK_mMBhJnyi9KoZ9WFf1tfJnlOac",
    "AIzaSyATHBdVQsH-7J8M2v6UcciZyWbzkr13uTA",
    "AIzaSyAvAt0as8Zs0r_iustkbWyimOhdLOzCm8w",
    "AIzaSyDaUPT6NQS8sqs16_hm9_A8ONHsVbh8QiY",


    "AIzaSyAdbNfxlQQQjKSgAcOjQt-XUwil-FMl6V8",  # Luc - Ca nhan
    "AIzaSyCSGNpc1IlacTUwN31TKWms0RzF_we17vk",  # Luc - Truong

    "AIzaSyBE8VObttX0oOGz5Jd82AtOiLTSzavIBL8",
    "AIzaSyAo5sCKOhGgYNgJ0m1QKsT29Ov-GNQHeSo",
    "AIzaSyDLa5CYtBGeXoV1-8y_ojA9eR_xzONABew",
    "AIzaSyCUtzli8ZRql653-0u_RrL7zM2SgEdb5ss",
    "AIzaSyBPi15fdt_YtyqaBIEuvSQ66T6T0ROHEA4",
    "AIzaSyC3DhYcDb8sLzzwywoJe8Foki3kMnVKPwQ",
    "AIzaSyDRE-VA4R9-UBRekhCGCcy3NlhlwQa1fnU",
    "AIzaSyD-WsC4RABxdqebovU-TYMueMHxPT2l6Nw",

    "AIzaSyDBscWgL9o2QtfNvx_xnZP3CWweyknGJKM",  # han-asd
    "AIzaSyAhbb5IEibxRDH8a8XB8Zk7lopPh8jhgwI",  # han-len
]

assert len(api_list) == len(set(api_list)), "Duplicate API keys found"
n_apis = len(api_list)
api_request_threshold = 14
api_idx = random.randint(0, n_apis - 1)
n_consecutive_requests = 0
# -

# # Lấy danh sách các video đã được xử lý
#

# Read text file to get a set of video IDs that have been preprocessed
preprocessed_video_ids = set()
if os.path.exists("preprocessed_video_ids.txt"):
    with open("preprocessed_video_ids.txt", "r") as f:
        preprocessed_video_ids = set(f.read().splitlines())

# Print the number of videos that have been preprocessed
print(f"Number of videos already preprocessed: {len(preprocessed_video_ids)}")

# # Các hàm tiện ích
#

"""
Phân tích nội dung sau (từ transcript video hoặc mô tả) và trích xuất thông tin:
{text}

Phân tích và trích xuất các thông tin theo cấu trúc dưới đây:
Bước 1: Phân loại Video (dựa trên nội dung):
1.1. Phân loại video (có thể dựa trên các từ khóa):
- "Ăn vặt đường phố": từ khóa "xe đẩy", "vỉa hè", "đồ ăn vặt", "chợ đêm", "hàng rong", "đường phố" -> "type": 0
- "Nhà hàng, Quán ăn": từ khóa "nhà hàng", "quán ăn", "đặt bàn", "phục vụ", "buffet", "sang trọng", "bình dân", "quầy bar" -> "type": 1
- "Nấu ăn": từ khóa "nấu ăn", "công thức", "chế biến", "nguyên liệu", "bếp", "tại nhà", "dụng cụ nấu bếp" -> "type": 2
- "Khác": Không thể phân loại -> "type": 3

1.2. Xác định tất cả các món ăn được đề cập (có thể có nhiều món ăn): Lưu tất cả các món ăn vào "food" và trả về theo dạng string data type (str), các món ăn được cách nhau bởi dấu phẩy (",").
1.3. Địa điểm: Xác định thành phố, quận/huyện tại Việt Nam

Bước 2: Trả về kết quả JSON:
{{
    "type": "Phân loại 0, 1, 2, 3",
    "food": "Tất cả các món ăn được đề cập",
    "city": "Thành phố",
    "district": "Quận/Huyện",
    "source": "transcript/desc"
}}

Lưu Ý:
- Ưu tiên thông tin chính xác
- Bám sát nội dung
- Trả về đúng định dạng JSON
- Các thông tin trả về đều phải có đúng định dạng
- Đối với các video không thuộc chủ đề ẩm thực thì hãy trả về None cho tất cả các trường
"""

prompt = """
Bạn là một chuyên gia trong lĩnh vực phân tích dữ liệu thông minh. Bạn có thể phân tích nội dung video và trích xuất thông tin từ đó. Người dùng sẽ cung cấp thông tin về mô tả và transcript của video TikTok về chủ đề ẩm thực. Hãy trích xuất thông tin về các món ăn và địa điểm được đề cập trong video đó. Bạn sẽ trả về một JSON chứa các thông tin sau:
{
    "foods": Danh sách các món ăn được đề cập trong video (danh sách string),
    "city: Tên thành phố (string),
    "district": Tên quận/huyện (string)
}

Đây là một số lưu ý quan trọng:
- Đối với các video không thuộc chủ đề ẩm thực thì hãy trả về None cho tất cả các trường
- Các thông tin trả về đều phải có đúng định dạng
- Trả về kết quả theo đúng định dạng JSON
- Ưu tiên thông tin chính xác
- Câu trả lời phải bám sát theo nội dung được cung cấp

Dưới đây là mô tả và transcript của video TikTok:
- Mô tả: %s
- Transcript: %s
"""


# +
def process_video_content(desc: str, transcript: str,
                          api_key: str) -> str:
    try:
        # Call the API to generate content
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=[
                prompt % (desc, transcript),
            ]
        )

        # Extract JSON content from the markdown-formatted response
        json_text: str = response.text
        # Remove the markdown code block formatting
        json_text: str = re.sub(r'^```json\n|\n```$', '', json_text)

        return json_text

    except Exception as e:
        print(f"[Error] API `{api_key}` failed: {e}")
        return None


def save_response(video_id: str, json_text: str) -> bool:
    # Define the file path for the target JSON file
    output_path: str = FOOD_LOCATION_FOLDER + f"/{video_id}.json"

    # Save the JSON response to a file
    with open(output_path, 'w') as f:
        f.write(json_text)

    if os.path.exists(output_path):
        print(f"Saved response to {output_path}")
        return True
    else:
        print(f"Failed to save response to {output_path}")
        return False


# -

# # Đoạn chương trình chính
#

# View complete prompt from 1 random video
row_idx = random.choice(video_id_range)
video_id, desc, transcript = video_df.loc[
    row_idx, ["video.id", "desc", "transcript"]]
print(prompt % (desc, transcript))

for row_id in tqdm(video_id_range):
    # Extract the videoID, description, and transcript from the DataFrame
    video_id = video_df.loc[row_id, "video.id"]
    desc = video_df.loc[row_id, "desc"]
    transcript = video_df.loc[row_id, "transcript"]

    # Skip if the video ID has already been preprocessed
    if video_id in preprocessed_video_ids:
        # print(f"Row {row_id} => Already preprocessed")
        continue

    # ========================================================
    # ********** MUST STOP IF API QUOTA IS EXCEEDED **********
    # ========================================================
    # Process the audio to generate the transcript
    json_text = process_video_content(
        desc=desc, transcript=transcript, api_key=api_list[api_idx])

    # Increment the number of consecutive requests
    n_consecutive_requests += 1
    # Check if the number of consecutive requests exceeds the threshold
    # and change the API key if necessary
    if n_consecutive_requests >= api_request_threshold:
        n_consecutive_requests = 0
        api_idx = (api_idx + 1) % n_apis
        print(f"Row {row_id} => Change API key")

    # # Sleep for a while to avoid hitting the API rate limit
    # time.sleep(1)

    if not json_text:
        print(f"Error processing content for the row: {row_id}")
        break
        continue

    # Save the transcript to a JSON file
    if not save_response(video_id, json_text):
        print(f"Error saving response for video ID: {video_id}")
        break
        continue

# # Tìm ra các file JSON trong thư mục
#

# +


def list_file_types(directory: str, file_extension: str) -> List[str]:
    """ List all files with a specific extension in a directory.

    Args:
        directory (str): Directory path.
        file_extension (str): File extension.

    Returns:
        List[str]: List of file paths.
    """

    file_list: List[str] = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(file_extension):
                file_list.append(os.path.join(root, file))
    return file_list


# -

json_files = list_file_types("food_location", ".json")
print(f"Number of JSON files found: {len(json_files)}")
# print(json_files[:5])

# +

# Set of filenames
file_names = set()

# Get a list of JSON files
for json_file in tqdm(json_files):
    # Extract base name of the file
    # remove file extension
    file_name = os.path.basename(json_file).replace(".json", "")
    # print(f"Processing file: {file_name}")

    # Append to the set
    file_names.add(file_name)

assert len(file_names) == len(json_files), "Duplicate file names found!"
# -

# Write the set of filenames to a text file
with open("preprocessed_video_ids.txt", "w") as f:
    for file_name in file_names:
        f.write(f"{file_name}\n")
print("==================== [DONE] ====================")
