import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from video_analysis.utils.visualization import (
    analyze_hashtag_engagement,
    plot_improved_top_hashtags,
    plot_hashtag_trends,
    analyze_hashtag_count_effect,
    get_top_hashtags_by_group,
    plot_interactive_hashtag_analysis,
    plot_video_duration_vs_views,
    plot_posting_day_vs_engagement,
    plot_posting_time_vs_views,
    plot_video_duration_vs_engagement,
    plot_hashtag_count_vs_engagement,
    plot_hashtag_count_boxplot,
    show_hashtag_wordcloud
)


@st.cache_data
def load_data():
    # Load the cleaned video data
    return pd.read_parquet("data/processed/video_data.parquet")


# 🎨 Streamlit Page Config
st.set_page_config(
    page_title="TikTok Insights Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 🎯 Sidebar Navigation
st.sidebar.title("📊 TikTok Dashboard")
selected_section = st.sidebar.radio("🔍 Select Analysis", [
                                    "📈 Hashtag Engagement", "🎬 Video Performance", "📈 Hashtag Insights"])

df = load_data()  # Load the data into a DataFrame

# 👉 General Filters
with st.sidebar.expander("⚙️ Filters", expanded=True):
    selected_metric = st.selectbox(
        "📊 Select Metric", ["Views", "Likes", "Comments", "Shares"], index=0)
    metric_map = {
        "Views": "statsV2.playCount",
        "Likes": "statsV2.diggCount",
        "Comments": "statsV2.commentCount",
        "Shares": "statsV2.shareCount",
    }
    metric_col = metric_map[selected_metric]

if selected_section == "📈 Hashtag Engagement":
    show_hashtag_wordcloud(df, metric_col)

# 🎮 Video Performance Insights
elif selected_section == "🎬 Video Performance":
    st.title("🎬 Video Performance Insights")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader(f"📌 Video Duration vs. {selected_metric}")
        st.plotly_chart(plot_video_duration_vs_views(
            df, metric_col), use_container_width=True)
    with col2:
        st.subheader(f"📌 Engagement vs. {selected_metric}")
        st.plotly_chart(plot_video_duration_vs_engagement(
            df, metric_col), use_container_width=True)

    st.markdown("---")

    # 🕖 Posting Time Analysis
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("⏰ Posting Time vs. Views")
        st.plotly_chart(plot_posting_time_vs_views(
            df, metric_col), use_container_width=True)
    with col2:
        st.subheader("📅 Posting Day vs. Engagement")
        st.plotly_chart(plot_posting_day_vs_engagement(
            df, metric_col), use_container_width=True)

# 📊 Hashtag Insights
elif selected_section == "📈 Hashtag Insights":
    st.title("🔍 Hashtag Analysis Dashboard")

    with st.sidebar.expander("📌 Hashtag Filters", expanded=True):
        top_n = st.slider("Select Top N Hashtags",
                          min_value=3, max_value=10, value=5)
        time_agg = st.radio("Choose Time Grouping:", [
                            "Daily", "Weekly", "Monthly"])

    col1, col2 = st.columns(2)
    with col1:
        st.subheader(f"📊 Hashtag Engagement Insights ({selected_metric})")
        st.plotly_chart(plot_improved_top_hashtags(analyze_hashtag_engagement(
            df, top_n, metric_col)), use_container_width=True)
    with col2:
        # Hashtag Count Analysis
        st.subheader(f"📌 Hashtag Count Effect on {selected_metric}")
        st.plotly_chart(plot_interactive_hashtag_analysis(analyze_hashtag_count_effect(
            df, metric_col), get_top_hashtags_by_group(df, metric_col), metric_col), use_container_width=True)

    st.markdown("---")

    st.subheader(f"📊 Hashtag Trends Over Time ({selected_metric})")
    st.plotly_chart(plot_hashtag_trends(df, time_agg, top_n,
                    metric_col), use_container_width=True)

    # Hashtag Count vs. Engagement Scatter
    st.subheader(f"📌 Hashtag Count vs. {selected_metric}")
    st.plotly_chart(plot_hashtag_count_vs_engagement(
        df, metric_col), use_container_width=True)
