import pandas as pd
import streamlit as st

@st.cache_data
def load_data():
    cleaned_user_csv_file = "data/interim/cleaned_user_info.csv"
    cleaned_video_csv_file = "data/interim/cleaned_video_info.csv"
    cleaned_script_parquet_file = "data/interim/content_features_6_users.parquet"

    cleaned_user_info_df = pd.read_csv(cleaned_user_csv_file)

    cleaned_video_info_df = pd.read_csv(cleaned_video_csv_file)
    cleaned_video_info_df['createTime'] = pd.to_datetime(cleaned_video_info_df['createTime'], unit='s')

    cleaned_script_df = pd.read_parquet(cleaned_script_parquet_file)
    cleaned_script_df['createTime'] = pd.to_datetime(cleaned_script_df['createTime'], errors='coerce')
    return cleaned_user_info_df, cleaned_video_info_df, cleaned_script_df
