# data_loader.py
import streamlit as st
import pandas as pd
# from data_preprocessing import video_info_df  # assuming you have this function

@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_data():
    """Load and cache the preprocessed data"""
    video_info_df = pd.read_parquet("data/preprocessed_videos.parquet")
    video_info_df['createTime'] = pd.to_datetime(video_info_df['createTime'], unit='s')
    return  video_info_df # This should return your video_info_df

# print(load_data().head)