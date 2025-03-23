import streamlit as st
import plotly.express as px
import pandas as pd
from styles import personal_styles

def personal_analysis(cleaned_video_info_df):
    personal_styles()
    tiktoker_options = cleaned_video_info_df['author.uniqueId'].unique()
    min_date = cleaned_video_info_df['createTime'].min().date()
    max_date = cleaned_video_info_df['createTime'].max().date()

    with st.sidebar:
        st.title("📊 TikTok Analytics")
        st.markdown("Analyze TikTok trends")
        selected_tiktoker = st.selectbox("👤 Select TikToker", tiktoker_options)
        date_range = st.slider("📅 Date Range", min_value=min_date, max_value=max_date, value=(min_date, max_date), format="MM/DD/YYYY")
        start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
        if st.button("🔄 Reset"):
            start_date, end_date = pd.to_datetime(min_date), pd.to_datetime(max_date)

    st.header(f"@{selected_tiktoker}'s Analytics")
    tiktoker_data = cleaned_video_info_df[cleaned_video_info_df['author.uniqueId'] == selected_tiktoker]

    if not tiktoker_data.empty:
        user_info = tiktoker_data.iloc[0]
        with st.container():
            st.subheader("Profile Overview")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Username", user_info['author.uniqueId'])
                st.metric("Followers", f"{user_info['authorStats.followerCount']:,}")
            with col2:
                st.metric("Commerce", user_info.get('user.commerceUserInfo.category', 'No info'))
                st.metric("Total Likes", f"{user_info['authorStats.heartCount']:,}")
            with col3:
                st.metric("Verified", "Yes ✅" if user_info['author.verified'] else "No ❌")
                st.metric("Total Videos", f"{user_info['authorStats.videoCount']:,}")

        with st.spinner("Loading data..."):
            filtered_data = tiktoker_data[(tiktoker_data['createTime'] >= start_date) & (tiktoker_data['createTime'] <= end_date)]

        if not filtered_data.empty:
            with st.expander("📈 Video Trends", expanded=True):
                video_counts = filtered_data.groupby(filtered_data['createTime'].dt.date).size().reset_index(name='Video Count')
                fig = px.area(video_counts, x='createTime', y='Video Count', title="Video Creation Over Time", template="plotly_white")
                fig.update_traces(line=dict(color="#00b4d8", width=2), fill='tozeroy')
                fig.add_scatter(x=video_counts['createTime'], y=video_counts['Video Count'], mode='markers', marker=dict(size=8, color="#00b4d8"))
                max_day = video_counts.loc[video_counts['Video Count'].idxmax()]
                fig.add_annotation(x=max_day['createTime'], y=max_day['Video Count'], text=f"Peak: {max_day['Video Count']}", showarrow=True, arrowhead=1)
                fig.update_layout(xaxis_title="Date", yaxis_title="Videos Posted", showlegend=False)
                st.plotly_chart(fig, use_container_width=True)

            with st.expander("🎵 Music Usage"):
                music_counts = filtered_data['music.authorName'].value_counts().head(10).reset_index()
                music_counts.columns = ['Music Author', 'Count']
                fig = px.bar(music_counts, x='Count', y='Music Author', orientation='h', title="Top 10 Music Choices", color='Count', color_continuous_scale='magma')
                fig.update_layout(xaxis_title="Times Used", yaxis_title="", showlegend=False)
                st.plotly_chart(fig, use_container_width=True)

            with st.expander("🏷️ Hashtag Usage"):
                all_hashtags = filtered_data['hashtags'].dropna().str.split().explode()
                if not all_hashtags.empty:
                    hashtag_counts = all_hashtags.value_counts().head(10).reset_index()
                    hashtag_counts.columns = ['Hashtag', 'Count']
                    fig = px.treemap(hashtag_counts, path=['Hashtag'], values='Count', title="Top 10 Hashtags", color='Count', color_continuous_scale='viridis')
                    fig.update_layout(margin=dict(t=50, l=0, r=0, b=0))
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.markdown('<p style="color:#3498db;">ℹ️ No hashtags available.</p>', unsafe_allow_html=True)
        else:
            st.markdown(f'<p style="color:#e67e22;">⚠️ No video data for {selected_tiktoker} in this range.</p>', unsafe_allow_html=True)
    else:
        st.markdown(f'<p style="color:#c0392b;">❌ No data for {selected_tiktoker}.</p>', unsafe_allow_html=True)
