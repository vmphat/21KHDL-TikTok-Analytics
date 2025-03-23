import pandas as pd


def load_data():
    cleaned_user_csv_file = "data/processed/cleaned_user_info.csv"
    cleaned_video_csv_file = "data/processed/cleaned_video_info.csv"
    cleaned_user_info_df = pd.read_csv(cleaned_user_csv_file)
    cleaned_video_info_df = pd.read_csv(cleaned_video_csv_file,
                                        parse_dates=["createTime"])
    # cleaned_video_info_df['createTime'] = pd.to_datetime(
    #     cleaned_video_info_df['createTime'], unit='s')
    return cleaned_user_info_df, cleaned_video_info_df
