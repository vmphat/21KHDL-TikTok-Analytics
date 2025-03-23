import streamlit as st
import plotly.express as px
from styles import hashtag_song_styles
import pandas as pd

def hashtag_song_analysis(cleaned_video_info_df):
    hashtag_song_styles()
    min_date = cleaned_video_info_df['createTime'].min().date()
    max_date = cleaned_video_info_df['createTime'].max().date()

    with st.sidebar:
        st.title("🔍 Filters")
        date_range = st.slider("📅 Date Range", min_value=min_date, max_value=max_date, value=(min_date, max_date), format="YYYY-MM-DD")
        start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
        top_k = st.number_input("🔢 Top K", min_value=1, max_value=50, value=10, step=1)

    st.title("🔍 Hashtag & Song Analysis")
    with st.spinner("Analyzing data..."):
        filtered_data = cleaned_video_info_df[(cleaned_video_info_df['createTime'] >= start_date) & (cleaned_video_info_df['createTime'] <= end_date)]

    if not filtered_data.empty:
        with st.expander("🔥 Most Used Hashtags", expanded=True):
            all_hashtags = filtered_data['hashtags'].dropna().str.split().explode()
            if not all_hashtags.empty:
                hashtag_counts = all_hashtags.value_counts().reset_index()
                hashtag_counts.columns = ['Hashtag', 'Count']
                top_hashtags = hashtag_counts.head(top_k)
                fig = px.bar(top_hashtags, x='Count', y='Hashtag', orientation='h', title="📌 Most Used Hashtags", color='Count', color_continuous_scale='viridis')
                fig.update_layout(xaxis_title="Usage Count", yaxis_title="Hashtag", template="plotly_white")
                st.plotly_chart(fig, use_container_width=True)
                if st.checkbox("Show Hashtag Table"):
                    st.dataframe(top_hashtags)
            else:
                st.markdown('<p style="color:#e74c3c;">⚠️ No hashtags found.</p>', unsafe_allow_html=True)

        with st.expander("🎵 Most Used Songs", expanded=True):
            music_counts = filtered_data['music.authorName'].value_counts().reset_index()
            music_counts.columns = ['Music Author', 'Count']
            top_music = music_counts.head(top_k)
            if not top_music.empty:
                fig = px.bar(top_music, x='Count', y='Music Author', orientation='h', title="🎶 Most Used Songs", color='Count', color_continuous_scale='viridis')
                fig.update_layout(xaxis_title="Usage Count", yaxis_title="Music Author", template="plotly_white")
                st.plotly_chart(fig, use_container_width=True)
                if st.checkbox("Show Song Table"):
                    st.dataframe(top_music)
            else:
                st.markdown('<p style="color:#e74c3c;">⚠️ No songs found.</p>', unsafe_allow_html=True)
    else:
        st.markdown('<p style="color:#e74c3c;">⚠️ No data available for this range.</p>', unsafe_allow_html=True)
