# Create a Dashboard in Streamlit webapp

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from google import genai
import plotly.express as px
from tqdm import tqdm
import streamlit as st

# Helper functions to load data


@st.cache_data
def load_data():
    data = pd.read_parquet("./preprocessed_videos.parquet")
    return data


# Load data
video_df = load_data()


# Title
st.title("Video Analysis Dashboard")
st.write("This is a dashboard to analyze video data")


@st.cache_data
def extract_insights(video_df):
    # Calculate the distribution of comment counts
    latex_str = video_df["statsV2.commentCount"].describe().to_latex()

    prompt = """
    Tôi muốn phân tích phân phối số lượng bình luận trên các video TikTok. Tôi đã tạo 1 bảng thống kê thể hiện phân phối số lượng bình luận trên các video, kết quả được thể hiện dưới dạng bảng như sau:
    %s

    Hãy giúp tôi rút ra các insights từ bảng thống kê trên. Hãy liệt kê các insights quan trọng từ bảng thống kê trên, bao gồm các thông tin như giá trị trung bình, giá trị trung vị, phân phối dữ liệu, và bất kỳ điểm nào khác bạn thấy quan trọng.
    """

    client = genai.Client(api_key="AIzaSyBYqr4g63GOBTslf5xP0-AbIcSSlAuvMnM")
    response = client.models.generate_content(
        model='gemini-2.5-pro-exp-03-25',
        contents=[
            prompt % latex_str,
        ]
    )

    # Display the markdown response
    st.markdown(response.text)


# Add date range filter in sidebar
st.sidebar.header("Filter Options")
st.sidebar.subheader("Date Range")


@st.cache_data
def filter_date(video_df, start_date, end_date):
    return video_df[(video_df["createTime"].dt.date >= start_date) &
                    (video_df["createTime"].dt.date <= end_date)]


# Get min and max dates
min_date = video_df["createTime"].min().date()
max_date = video_df["createTime"].max().date()

# Create date range slider in sidebar
start_date, end_date = st.sidebar.slider(
    "Select Date Range",
    min_value=min_date,
    max_value=max_date,
    value=(min_date, max_date)  # Default to full date range
)

# Filter the dataframe based on selected date range
filtered_df = filter_date(video_df, start_date, end_date)

# Display filter information
st.write(
    f"Showing {len(filtered_df)} videos from {start_date} to {end_date} (out of {len(video_df)} total)")

# Create histogram for filtered data
st.write("## Comment Count Distribution (Filtered)")
fig = px.histogram(
    filtered_df,
    x="statsV2.commentCount",
    title="Distribution of Comment Counts (Filtered by Date)",
    labels={"statsV2.commentCount": "Comment Count"},
    log_y=True,
    opacity=0.7,
    color_discrete_sequence=['#00b4d8']
)

fig.update_layout(
    xaxis_title="Number of Comments",
    yaxis_title="Count of Videos (log scale)",
    bargap=0.2,
    template="plotly_white"
)

median_value = filtered_df["statsV2.commentCount"].median()
mean_value = filtered_df["statsV2.commentCount"].mean()

fig.add_vline(x=median_value, line_dash="dash", line_color="red",
              annotation_text=f"Median: {median_value}")
fig.add_vline(x=mean_value, line_dash="dash", line_color="green",
              annotation_text=f"Mean: {round(mean_value, 2)}")

st.plotly_chart(fig)
extract_insights(filtered_df)
