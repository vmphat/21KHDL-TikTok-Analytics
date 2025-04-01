import streamlit as st
import plotly.express as px
import pandas as pd


# Configuring Streamlit
st.set_page_config(
    page_title="Phân tích người dùng TikTok",
    page_icon=":bar_chart:",
    layout="wide",
    initial_sidebar_state="expanded",
)


def correlation_analysis(cleaned_user_info_df):
    tab1, tab2, tab3 = st.tabs(
        ["📊 Correlation Analysis", "🏆 Top Users", "🔥 Engagement Insights"])

    # Tab 1: Correlation Analysis
    with tab1:
        st.header("📊 Correlation Analysis")
        st.write("Analyze relationships between followers, likes, and videos.")
        colors_rgba = ["rgba(99, 110, 250, 0.9)",
                       "rgba(239, 85, 59, 0.8)", "rgba(0, 204, 150, 0.7)"]
        st.markdown(
            '<div class="main-title">📊 TikTok User Analysis Dashboard</div>', unsafe_allow_html=True)
        st.markdown("### ⚙️ Customize Your Analysis")
        col_input1, col_input2, col_input3 = st.columns([2, 1, 1])
        with col_input1:
            chart_option = st.selectbox("Select a Visualization", [
                                        "Distribution of Followers", "Distribution of Likes", "Distribution of Video Count", "All in One", "Scatter Matrix"])
        with col_input2:
            num_bins = st.slider("Number of Bins", 10, 100, 50, 5)
        with col_input3:
            log_scale = st.checkbox("Logarithmic Scale", value=True)

        col1, col2 = st.columns([3, 2])
        with col1:
            with st.spinner(f"Rendering {chart_option.lower()}..."):
                if chart_option == "Distribution of Followers":
                    st.markdown(
                        '<div class="subheader">📈 Followers Distribution</div>', unsafe_allow_html=True)
                    fig = px.histogram(cleaned_user_info_df, x='stats.followerCount', nbins=num_bins,
                                       log_y=log_scale, color_discrete_sequence=[colors_rgba[0]], height=500, marginal="box")
                    fig.update_layout(template="plotly_dark",
                                      bargap=0.1, showlegend=False)
                    st.plotly_chart(fig, use_container_width=True)
                elif chart_option == "Distribution of Likes":
                    st.markdown(
                        '<div class="subheader">❤️ Likes Distribution</div>', unsafe_allow_html=True)
                    fig = px.histogram(cleaned_user_info_df, x='stats.heart', nbins=num_bins, log_y=log_scale, color_discrete_sequence=[
                                       colors_rgba[1]], height=500, marginal="box")
                    fig.update_layout(template="plotly_dark",
                                      bargap=0.1, showlegend=False)
                    st.plotly_chart(fig, use_container_width=True)
                elif chart_option == "Distribution of Video Count":
                    st.markdown(
                        '<div class="subheader">🎬 Video Count Distribution</div>', unsafe_allow_html=True)
                    fig = px.histogram(cleaned_user_info_df, x='stats.videoCount', nbins=num_bins,
                                       log_y=log_scale, color_discrete_sequence=[colors_rgba[2]], height=500, marginal="box")
                    fig.update_layout(template="plotly_dark",
                                      bargap=0.1, showlegend=False)
                    st.plotly_chart(fig, use_container_width=True)
                elif chart_option == "All in One":
                    st.markdown(
                        '<div class="subheader">📊 Combined Distribution</div>', unsafe_allow_html=True)
                    melted_df = cleaned_user_info_df.melt(value_vars=[
                                                          'stats.followerCount', 'stats.heart', 'stats.videoCount'], var_name="Metric", value_name="Count")
                    metric_names = {"stats.followerCount": "Followers",
                                    "stats.heart": "Likes", "stats.videoCount": "Videos"}
                    melted_df["Metric"] = melted_df["Metric"].map(metric_names)
                    fig = px.histogram(melted_df, x="Count", color="Metric", log_y=log_scale, nbins=num_bins, color_discrete_map={
                                       "Followers": colors_rgba[0], "Likes": colors_rgba[1], "Videos": colors_rgba[2]}, height=500, opacity=0.7, barmode="overlay")
                    fig.update_layout(template="plotly_dark",
                                      bargap=0.1, legend_title_text="Metrics")
                    st.plotly_chart(fig, use_container_width=True)
                elif chart_option == "Scatter Matrix":
                    st.markdown(
                        '<div class="subheader">🔍 Scatter Matrix</div>', unsafe_allow_html=True)
                    fig = px.scatter_matrix(cleaned_user_info_df, dimensions=[
                                            'stats.followerCount', 'stats.heart', 'stats.videoCount'], color_discrete_sequence=colors_rgba, height=600, opacity=0.6)
                    fig.update_traces(diagonal_visible=False)
                    fig.update_layout(template="plotly_dark")
                    st.plotly_chart(fig, use_container_width=True)
            data_to_download = cleaned_user_info_df[[
                'stats.followerCount', 'stats.heart', 'stats.videoCount']]
            st.download_button(label="📥 Download Chart Data", data=data_to_download.to_csv(
                index=False), file_name=f"{chart_option.lower().replace(' ', '_')}.csv", mime="text/csv")
        with col2:
            with st.expander("📋 Quick Stats", expanded=True):
                st.markdown("#### Summary")
                st.write(f"**Total Users:** {len(cleaned_user_info_df):,}")
                st.write(
                    f"**Avg. Followers:** {cleaned_user_info_df['stats.followerCount'].mean():,.0f}")
                st.write(
                    f"**Avg. Likes:** {cleaned_user_info_df['stats.heart'].mean():,.0f}")
                st.write(
                    f"**Avg. Videos:** {cleaned_user_info_df['stats.videoCount'].mean():,.0f}")
            st.markdown(
                '<div class="subheader">📊 Correlation Heatmap</div>', unsafe_allow_html=True)
            correlation_matrix = cleaned_user_info_df[[
                'stats.followerCount', 'stats.heart', 'stats.videoCount']].corr()
            fig = px.imshow(correlation_matrix, text_auto=".2f", aspect="equal", color_continuous_scale="Blues", labels=dict(
                x="Metrics", y="Metrics", color="Correlation"), height=400)
            fig.update_layout(xaxis=dict(tickvals=[0, 1, 2], ticktext=["Followers", "Likes", "Videos"]), yaxis=dict(
                tickvals=[0, 1, 2], ticktext=["Followers", "Likes", "Videos"]))
            st.plotly_chart(fig, use_container_width=True)

    # Tab 2: Top Users
    with tab2:
        st.header("🏆 Top Users")
        st.write("View the most influential TikTok users.")
        st.markdown('<div class="main-title" style="font-size: 28px; font-weight: bold; color: #1E90FF;">🏆 Top Users Analysis</div>', unsafe_allow_html=True)
        st.markdown('<p style="color: #666;">Explore the top-performing users based on engagement metrics like likes and video counts.</p>', unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            top_n = st.slider("Select Top N Users", 1, 50, 10, 1)
        with col2:
            chart_option = st.selectbox("Select Chart Type", [
                                        "Most Likes", "Most Videos", "Most Followers", "Engagement Rate"])
        with col3:
            sort_order = st.radio(
                "Sort Order", ["Descending", "Ascending"], index=0)
        tab_bar, tab_pie = st.tabs(["Bar Chart", "Pie Chart"])
        with st.spinner(f"Generating visuals for Top {top_n} Users..."):
            if chart_option == "Most Likes":
                metric, title, color_scale, y_label = 'stats.heart', f"Top {top_n} Users with Most Likes", 'reds', "Total Likes (Hearts)"
            elif chart_option == "Most Videos":
                metric, title, color_scale, y_label = 'stats.videoCount', f"Top {top_n} Users with Most Videos", 'greens', "Total Videos"
            elif chart_option == "Most Followers":
                metric, title, color_scale, y_label = 'stats.followerCount', f"Top {top_n} Users with Most Followers", 'blues', "Total Followers"
            else:
                cleaned_user_info_df['engagement_rate'] = cleaned_user_info_df['stats.heart'] / \
                    cleaned_user_info_df['stats.videoCount'].replace(0, 1)
                metric, title, color_scale, y_label = 'engagement_rate', f"Top {top_n} Users by Engagement Rate (Likes/Video)", 'purples', "Engagement Rate"
            top_data = (cleaned_user_info_df.nlargest(top_n, metric) if sort_order ==
                        "Descending" else cleaned_user_info_df.nsmallest(top_n, metric))[['user.uniqueId', metric]]
            with tab_bar:
                st.markdown(
                    f'<div class="subheader" style="color: #333; font-weight: bold;">{title}</div>', unsafe_allow_html=True)
                fig = px.bar(top_data, x='user.uniqueId', y=metric, color=metric, color_continuous_scale=color_scale, text=top_data[metric].apply(
                    lambda x: f'{x:,.1f}' if metric == 'engagement_rate' else f'{x:,}'), height=500)
                fig.update_traces(textposition='outside', textfont_size=12)
                fig.update_layout(xaxis_title="User ID", yaxis_title=y_label, template="plotly_white", xaxis_tickangle=-45,
                                  showlegend=False, margin=dict(t=50, b=50), plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig, use_container_width=True)
            with tab_pie:
                st.markdown(
                    f'<div class="subheader" style="color: #333; font-weight: bold;">Distribution of {chart_option}</div>', unsafe_allow_html=True)
                fig = px.pie(top_data, names='user.uniqueId', values=metric,
                             color_discrete_sequence=px.colors.sequential.RdBu, height=500)
                fig.update_traces(textinfo='percent+label',
                                  pull=[0.1] + [0]*(top_n-1))
                fig.update_layout(template="plotly_white", margin=dict(
                    t=50, b=50), plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig, use_container_width=True)
        with st.expander("View Detailed Data", expanded=False):
            st.dataframe(top_data.style.format(
                {metric: "{:,.2f}" if metric == 'engagement_rate' else "{:,}"}), use_container_width=True)
        csv = top_data.to_csv(index=False)
        st.download_button(label="📥 Download Data as CSV", data=csv,
                           file_name=f"top_{top_n}_{chart_option.lower().replace(' ', '_')}_{sort_order.lower()}.csv", mime="text/csv")

    # Tab 3: Engagement Insights
    with tab3:
        st.header("🔥 Engagement Insights")
        st.write(
            "Understand how engagement levels vary across different user segments.")
        st.markdown(
            '<h2 style="text-align:center;">🏆 Engagement Analysis</h2>', unsafe_allow_html=True)
        st.write(
            "Analyze the relationship between **followers** and **engagement (likes/hearts)**.")
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            follower_level = st.selectbox("📌 Select Follower Level:", [
                                          "Low", "Average", "High"])
        with col2:
            engagement_level = st.selectbox("🔥 Select Engagement Level:", [
                                            "Low", "Average", "High"])
        with col3:
            plotly_theme = st.selectbox(
                "🎨 Choose Theme:", ["plotly_dark", "seaborn", "ggplot2", "plotly_white"])
        cleaned_user_info_df['engagement_ratio'] = cleaned_user_info_df['stats.heart'] / \
            cleaned_user_info_df['stats.followerCount'].replace(0, 1)
        percentiles = [0, 0.33, 0.66, 1]
        low_followers, high_followers = cleaned_user_info_df['stats.followerCount'].quantile(
            percentiles[1]), cleaned_user_info_df['stats.followerCount'].quantile(percentiles[2])
        low_engagement, high_engagement = cleaned_user_info_df['engagement_ratio'].quantile(
            percentiles[1]), cleaned_user_info_df['engagement_ratio'].quantile(percentiles[2])
        if follower_level == "Low":
            filtered_df = cleaned_user_info_df[cleaned_user_info_df['stats.followerCount'] <= low_followers]
        elif follower_level == "Average":
            filtered_df = cleaned_user_info_df[(cleaned_user_info_df['stats.followerCount'] > low_followers) & (
                cleaned_user_info_df['stats.followerCount'] <= high_followers)]
        else:
            filtered_df = cleaned_user_info_df[cleaned_user_info_df['stats.followerCount'] > high_followers]
        if engagement_level == "Low":
            filtered_df = filtered_df[filtered_df['engagement_ratio']
                                      <= low_engagement]
        elif engagement_level == "Average":
            filtered_df = filtered_df[(filtered_df['engagement_ratio'] > low_engagement) & (
                filtered_df['engagement_ratio'] <= high_engagement)]
        else:
            filtered_df = filtered_df[filtered_df['engagement_ratio']
                                      > high_engagement]
        with st.spinner("📊 Rendering engagement analysis..."):
            fig = px.scatter(filtered_df, x='stats.followerCount', y='stats.heart', size='stats.followerCount',
                             color='engagement_ratio', color_continuous_scale='viridis', hover_data=['user.uniqueId'], height=600, opacity=0.75)
            fig.update_layout(xaxis_title="👥 Follower Count", yaxis_title="❤️ Total Likes", template=plotly_theme,
                              xaxis_type="log", yaxis_type="log", showlegend=True, coloraxis_colorbar_title="Engagement Ratio 🔥")
            st.markdown(
                f'<h3>📊 Engagement Insights: {follower_level} Followers & {engagement_level} Engagement</h3>', unsafe_allow_html=True)
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("📌 Number of Users", f"{len(filtered_df):,}")
            with col2:
                st.metric("❤️ Avg. Likes",
                          f"{filtered_df['stats.heart'].mean():,.0f}")
            with col3:
                st.metric("👥 Avg. Followers",
                          f"{filtered_df['stats.followerCount'].mean():,.0f}")
            st.plotly_chart(fig, use_container_width=True)
        st.markdown("""
        **🔍 Key Takeaways:**
        - Higher engagement doesn't always come from high followers!
        - Some small creators can outperform big ones in engagement.
        - Use trending hashtags and sounds to boost visibility!
        """)


@st.cache_data
def load_data():
    cleaned_user_csv_file = "data/processed/cleaned_user_info.csv"
    cleaned_video_csv_file = "data/processed/cleaned_video_info.csv"
    cleaned_user_info_df = pd.read_csv(cleaned_user_csv_file)
    cleaned_video_info_df = pd.read_csv(cleaned_video_csv_file,
                                        parse_dates=["createTime"])
    # cleaned_video_info_df['createTime'] = pd.to_datetime(
    #     cleaned_video_info_df['createTime'], unit='s')
    return cleaned_user_info_df, cleaned_video_info_df


cleaned_user_info_df, cleaned_video_info_df = load_data()
correlation_analysis(cleaned_user_info_df)
