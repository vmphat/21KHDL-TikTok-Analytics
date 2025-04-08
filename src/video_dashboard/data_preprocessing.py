#!/usr/bin/env python
# coding: utf-8

# # Import các thư viện cần thiết

# In[ ]:


import os
from tqdm import tqdm
from typing import List
import pandas as pd

# Display all columns
pd.set_option('display.max_columns', None)


# # 2. Tiền xử lý dữ liệu thống kê từ video

# Đọc dữ liệu thống kê video thành DataFrame.

# In[18]:


video_info_df = pd.read_csv("data/interim/video_info.csv", low_memory=False)
video_info_df.info()


# Loại bỏ các cột có tỷ lệ thiếu dữ liệu lớn hơn 50%

# In[19]:


# Calculate the missing ratio
missing_ratio = video_info_df.isna().sum() / len(video_info_df)

# Sort the missing ratio in descending order
missing_ratio = missing_ratio.sort_values(ascending=False)

# Display first 5 rows
missing_ratio.head()


# In[20]:


# Remove columns with missing ratios greater than 0.50
video_info_df = video_info_df.dropna(
    axis='columns', thresh=0.50 * len(video_info_df)
)


# In[23]:


# Calculate the missing ratio
missing_ratio = video_info_df.isna().sum() / len(video_info_df)

# Sort the missing ratio in descending order
missing_ratio = missing_ratio.sort_values(ascending=False)

# Display the missing ratio
for column, ratio in missing_ratio[:5].items():
    print(f"{column:50}:{ratio:8.2%}")


# In[24]:


# video_info_df.info()


# Vì các cột có tên bắt đầu với `stats.*` chứa cùng thông tin với các cột có tên bắt đầu với `statsV2.*`, nhưng không có thông tin về `repostCount` như `statsV2.*`. Nên ta sẽ loại bỏ các cột có tên bắt đầu với `stats.*`.
# 

# In[25]:


# Remove columns starting with "stats."
video_info_df = video_info_df[
    [column for column in video_info_df.columns
            if not column.startswith("stats.")]
]

# video_info_df.info()


# Xóa các cột bắt đầu với `video.claInfo.originalLanguageInfo.*` vì chúng chứa thông tin không cần thiết.
# 

# In[26]:


# Remove columns starting with "video.claInfo.originalLanguageInfo."
video_info_df = video_info_df[
    [column for column in video_info_df.columns
            if not column.startswith("video.claInfo.originalLanguageInfo.")]
]

# video_info_df.info()


# Tạo một cột chứa danh sách các `hashtag` được trích xuất từ mô tả video. Và tính số lượng hashtag trong mỗi video.

# In[27]:


# Replace missing values in "desc" column with an empty string
video_info_df["desc"] = video_info_df["desc"].fillna("")
video_info_df["desc"] = video_info_df["desc"].astype(str)
video_info_df["desc"] = video_info_df["desc"].str.strip()

# Create a new column for the hashtags
# and the number of hashtags in each video
video_info_df["hashtags"] = [""] * len(video_info_df)
video_info_df["num_hashtags"] = [0] * len(video_info_df)

# Extract hashtags from the "desc" column
# and Get the number of hashtags in each video
for index in tqdm(range(len(video_info_df))):
    # Get the description of the video
    description = video_info_df.loc[index, "desc"].strip().lower()

    if description:
        # Remove emojis
        description = description.encode('ascii', 'ignore').decode('ascii')

        # Add a space before all "#" characters
        description = description.replace("#", " #")

        # Find all strings starting with "#" and followed by a word
        hashtags = [word[1:] for word in description.split()
                    if word.startswith("#")]

        # Extract hashtags from the description
        video_info_df.loc[index, "hashtags"] = ",".join(hashtags).strip()

        # Get the number of hashtags
        video_info_df.loc[index, "num_hashtags"] = len(hashtags)
    else:
        video_info_df.loc[index, "hashtags"] = ""
        video_info_df.loc[index, "num_hashtags"] = 0


# In[35]:


video_info_df[["hashtags", "num_hashtags"]].sample(n=5)


# In[ ]:


video_info_df['hashtags'] = video_info_df['hashtags'].apply(lambda x: x.split(',') if isinstance(x, str) and x.strip() else [])
video_info_df["hashtags"] = video_info_df["hashtags"].apply(lambda x: x if isinstance(x, list) else [])


# In[ ]:


video_info_df['createTime'] = pd.to_datetime(video_info_df['createTime'], unit='s')


# Lưu DataFrame đã xử lý vào file `merged_data.csv`.

# In[ ]:


video_info_df.to_csv("data/processed/video_data.csv", index=False)
# small_vide_df = video_info_df.head()
# small_vide_df.to_csv("data/processed/sub_video_data.csv", index=False)


# In[54]:

video_info_df["hashtag_count"] = video_info_df["hashtags"].apply(lambda x: len(x))
video_info_df = video_info_df[video_info_df["hashtag_count"] <= 40]

# merged_df.to_parquet("data/processed/merged_data.parquet", index=False)


# # ========================================