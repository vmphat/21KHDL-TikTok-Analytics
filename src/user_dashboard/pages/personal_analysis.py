import streamlit as st
import plotly.express as px
import pandas as pd
from styles import personal_styles
from footer import display_footer
from data_loader import load_data

# Tải dữ liệu với vòng quay chờ
with st.spinner("Đang tải dữ liệu TikTok..."):
    # Tải dữ liệu
    cleaned_user_info_df, cleaned_video_info_df, cleaned_script_df = load_data()
    # Lưu trữ dữ liệu trong trạng thái phiên để các trang truy cập
    st.session_state['cleaned_user_info_df'] = cleaned_user_info_df
    st.session_state['cleaned_video_info_df'] = cleaned_video_info_df
    st.session_state['cleaned_script_df'] = cleaned_script_df

def analyze_scripts(data_df, title="🍳 Phân tích kịch bản", user_context="người dùng được chọn"):
    """
    Phân tích các thuộc tính kịch bản và hiển thị thông tin chi tiết cho một DataFrame đã cho.
    
    Tham số:
    - data_df: DataFrame chứa dữ liệu video với các cột kịch bản
    - title: Tiêu đề cho phần phân tích
    - user_context: Bối cảnh cho (các) người dùng đang được phân tích (ví dụ: "người dùng" hoặc "người dùng được chọn")
    """
    # CSS tùy chỉnh để định kiểu (nhất quán với bản gốc)
    st.markdown("""
        <style>
        .main {background-color: #f5f5f5; padding: 20px;}
        .stSubheader {font-size: 20px; font-weight: bold; color: #2c3e50;}
        .stButton>button {background-color: #3498db; color: white; border-radius: 5px;}
        .stMarkdown {font-size: 14px; color: #34495e;}
        </style>
    """, unsafe_allow_html=True)

    # Tiêu đề và Giới thiệu
    st.title(title)
    st.markdown(f"_Lọc và khám phá video với thông tin chi tiết cho {user_context}._")

    # Bộ lọc
    st.subheader("🔍 Lọc video")
    col1, col2, col3 = st.columns(3)
    with col1:
        selected_main_focus = st.multiselect("Chủ đề chính", data_df["main_content_focus"].explode().unique(), 
                                             help="Trọng tâm chính của video.")
        selected_structure_style = st.multiselect("Phong cách nội dung", data_df["structure_style"].explode().unique(), 
                                                  help="Cấu trúc của kịch bản.")
    with col2:
        selected_hook_type = st.multiselect("Loại móc câu", data_df["hook_type"].explode().unique(), 
                                            help="Loại yếu tố thu hút sự chú ý.")
        selected_tone = st.multiselect("Giọng điệu", data_df["tone_of_voice"].explode().unique(), 
                                       help="Tông cảm xúc của video.")
    with col3:
        selected_pacing = st.multiselect("Tốc độ", data_df["pacing"].explode().unique(), 
                                         help="Tốc độ trình bày.")
        reset_filters = st.button("Đặt lại bộ lọc")

    # Logic đặt lại bộ lọc
    if reset_filters:
        selected_main_focus = []
        selected_structure_style = []
        selected_hook_type = []
        selected_tone = []
        selected_pacing = []

    # Áp dụng bộ lọc
    filtered_df = data_df.copy()
    if selected_main_focus:
        filtered_df = filtered_df[filtered_df["main_content_focus"].apply(lambda x: any(i in selected_main_focus for i in x))]
    if selected_structure_style:
        filtered_df = filtered_df[filtered_df["structure_style"].apply(lambda x: any(i in selected_structure_style for i in x))]
    if selected_hook_type:
        filtered_df = filtered_df[filtered_df["hook_type"].apply(lambda x: any(i in selected_hook_type for i in x))]
    if selected_tone:
        filtered_df = filtered_df[filtered_df["tone_of_voice"].apply(lambda x: any(i in selected_tone for i in x))]
    if selected_pacing:
        filtered_df = filtered_df[filtered_df["pacing"].apply(lambda x: any(i in selected_pacing for i in x))]

    # Hiển thị kết quả đã lọc
    st.subheader("📊 Thông tin chi tiết về video")
    if filtered_df.empty:
        st.warning(f"Không có video nào khớp với bộ lọc đã chọn cho {user_context}.")
    else:
        st.info(f"Hiển thị thông tin chi tiết cho {len(filtered_df)} video phù hợp.")

        # Biểu đồ cột số liệu tương tác
        st.markdown("### Tổng quan tương tác")
        engagement_agg = filtered_df[["statsV2.playCount", "statsV2.diggCount", "statsV2.commentCount",
                                      "statsV2.shareCount", "statsV2.collectCount"]].mean().reset_index()
        engagement_agg.columns = ["Chỉ số", "Số lượng trung bình"]
        engagement_agg["Chỉ số"] = ["Lượt xem", "Lượt thích", "Bình luận", "Chia sẻ", "Lưu"]
        fig_eng = px.bar(
            engagement_agg, x="Chỉ số", y="Số lượng trung bình",
            text=engagement_agg["Số lượng trung bình"].apply(lambda x: f"{int(x):,}"),
            template="plotly_white", color="Chỉ số", color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig_eng.update_traces(textposition="auto")
        fig_eng.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig_eng, use_container_width=True)

        # Phân phối thời lượng video
        st.markdown("### Phân phối thời lượng video")
        fig_duration = px.histogram(
            filtered_df, x="video.duration", nbins=20, title="",
            template="plotly_white", color_discrete_sequence=["#3498db"]
        )
        fig_duration.update_layout(height=400, xaxis_title="Thời lượng (giây)", yaxis_title="Số lượng")
        st.plotly_chart(fig_duration, use_container_width=True)

        # Biểu đồ tròn sử dụng hashtag
        st.markdown("### Hashtag hàng đầu")
        hashtag_counts = filtered_df["hashtags"].explode().value_counts().head(10).reset_index()
        hashtag_counts.columns = ["Hashtag", "Số lượng"]
        fig_hashtag = px.pie(
            hashtag_counts, names="Hashtag", values="Số lượng",
            template="plotly_white", color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig_hashtag.update_layout(height=400)
        st.plotly_chart(fig_hashtag, use_container_width=True)

        # Tất cả video trong bảng phân trang
        st.markdown("### Chi tiết tất cả video")
        if 'page' not in st.session_state:
            st.session_state.page = 0

        rows_per_page = 10
        total_pages = (len(filtered_df) - 1) // rows_per_page + 1

        display_df = filtered_df[[
            'author.uniqueId', 'video.id', 'desc', 'video.duration', 'createTime',
            'statsV2.playCount', 'statsV2.diggCount', 'statsV2.commentCount',
            'statsV2.shareCount', 'statsV2.collectCount', 'gemini_analysis'
        ]].copy()
        display_df['createTime'] = display_df['createTime'].dt.strftime('%Y-%m-%d')
        display_df.columns = [
            'Tác giả', 'ID Video', 'Mô tả', 'Thời lượng (giây)', 'Ngày tạo',
            'Lượt xem', 'Lượt thích', 'Bình luận', 'Chia sẻ', 'Lưu', 'Phân tích Gemini'
        ]

        start_idx = st.session_state.page * rows_per_page
        end_idx = start_idx + rows_per_page
        page_df = display_df.iloc[start_idx:end_idx]

        st.dataframe(page_df, use_container_width=True, height=400)

        col_prev, col_page, col_next = st.columns([1, 2, 1])
        with col_prev:
            if st.button("Trước") and st.session_state.page > 0:
                st.session_state.page -= 1
        with col_page:
            st.write(f"Trang {st.session_state.page + 1} / {total_pages}")
        with col_next:
            if st.button("Tiếp") and st.session_state.page < total_pages - 1:
                st.session_state.page += 1

def personal_analysis(cleaned_video_info_df):
    personal_styles()

    # Kiểm tra nếu DataFrame trống hoặc thiếu cột cần thiết
    required_columns = ['author.uniqueId', 'createTime', 'hashtags', 'music.authorName']
    if cleaned_video_info_df.empty or not all(col in cleaned_video_info_df.columns for col in required_columns):
        st.error("Dữ liệu video được cung cấp trống hoặc thiếu các cột cần thiết.")
        return

    tiktoker_options = cleaned_video_info_df['author.uniqueId'].unique()
    min_date = cleaned_video_info_df['createTime'].min().date()
    max_date = cleaned_video_info_df['createTime'].max().date()

    # Khởi tạo trạng thái phiên cho phạm vi ngày dưới dạng đối tượng ngày
    if 'start_date' not in st.session_state:
        st.session_state['start_date'] = min_date
    if 'end_date' not in st.session_state:
        st.session_state['end_date'] = max_date

    with st.sidebar:
        st.title("📊 Phân tích TikTok")
        st.markdown("Phân tích xu hướng TikTok")
        selected_tiktoker = st.selectbox("👤 Chọn TikToker", tiktoker_options)
        # Đảm bảo giá trị là một tuple của các đối tượng ngày
        date_range = st.slider("📅 Phạm vi ngày", min_value=min_date, max_value=max_date,
                               value=(st.session_state['start_date'], st.session_state['end_date']),
                               format="MM/DD/YYYY")
        # Cập nhật trạng thái phiên với các đối tượng ngày
        st.session_state['start_date'], st.session_state['end_date'] = date_range[0], date_range[1]
        if st.button("🔄 Đặt lại"):
            st.session_state['start_date'] = min_date
            st.session_state['end_date'] = max_date
            st.rerun()  # Chạy lại để cập nhật thanh trượt

    st.header(f"Phân tích của @{selected_tiktoker}")
    tiktoker_data = cleaned_video_info_df[cleaned_video_info_df['author.uniqueId'] == selected_tiktoker]
    tiktoker_script = cleaned_script_df[cleaned_script_df['author.uniqueId'] == selected_tiktoker]

    if not tiktoker_data.empty:
        user_info = tiktoker_data.iloc[0]
        with st.container():
            st.subheader("Tổng quan hồ sơ")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Tên người dùng", user_info['author.uniqueId'])
                st.metric("Người theo dõi", f"{user_info.get('authorStats.followerCount', 0):,}")
            with col2:
                st.metric("Thương mại", user_info.get('user.commerceUserInfo.category', 'Không có thông tin'))
                st.metric("Tổng lượt thích", f"{user_info.get('authorStats.heartCount', 0):,}")
            with col3:
                st.metric("Đã xác minh", "Có ✅" if user_info.get('author.verified', False) else "Không ❌")
                st.metric("Tổng số video", f"{user_info.get('authorStats.videoCount', 0):,}")

        with st.spinner("Đang tải dữ liệu..."):
            filtered_data = tiktoker_data[(tiktoker_data['createTime'] >= pd.to_datetime(st.session_state['start_date'])) &
                                         (tiktoker_data['createTime'] <= pd.to_datetime(st.session_state['end_date']))]

        if not filtered_data.empty:
            st.markdown("📈 Xu hướng video", unsafe_allow_html=True)
            video_counts = filtered_data.groupby(filtered_data['createTime'].dt.date).size().reset_index(name='Số lượng video')
            fig = px.area(video_counts, x='createTime', y='Số lượng video', title="Tạo video theo thời gian", template="plotly_white")
            fig.update_traces(line=dict(color="#00b4d8", width=2), fill='tozeroy')
            fig.add_scatter(x=video_counts['createTime'], y=video_counts['Số lượng video'], mode='markers', marker=dict(size=8, color="#00b4d8"))
            max_day = video_counts.loc[video_counts['Số lượng video'].idxmax()]
            fig.add_annotation(x=max_day['createTime'], y=max_day['Số lượng video'], text=f"Đỉnh: {max_day['Số lượng video']}", showarrow=True, arrowhead=1)
            fig.update_layout(xaxis_title="Ngày", yaxis_title="Video đã đăng", showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

            st.markdown("🎵 Sử dụng âm nhạc", unsafe_allow_html=True)
            music_counts = filtered_data['music.authorName'].value_counts().head(10).reset_index()
            music_counts.columns = ['Tác giả âm nhạc', 'Số lượng']
            fig = px.bar(music_counts, x='Số lượng', y='Tác giả âm nhạc', orientation='h', title="Top 10 lựa chọn âm nhạc", color='Số lượng', color_continuous_scale='magma')
            fig.update_layout(xaxis_title="Số lần sử dụng", yaxis_title="", showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

            st.markdown("🏷️ Sử dụng hashtag", unsafe_allow_html=True)
            all_hashtags = filtered_data['hashtags'].dropna().str.split().explode()
            if not all_hashtags.empty:
                hashtag_counts = all_hashtags.value_counts().head(10).reset_index()
                hashtag_counts.columns = ['Hashtag', 'Số lượng']
                fig = px.treemap(hashtag_counts, path=['Hashtag'], values='Số lượng', title="Top 10 hashtag", color='Số lượng', color_continuous_scale='viridis')
                fig.update_layout(margin=dict(t=50, l=0, r=0, b=0))
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.markdown('<p style="color:#3498db;">ℹ️ Không có hashtag nào.</p>', unsafe_allow_html=True)
            analyze_scripts(tiktoker_script)
        else:
            st.markdown(f'<p style="color:#e67e22;">⚠️ Không có dữ liệu video cho {selected_tiktoker} trong phạm vi này.</p>', unsafe_allow_html=True)
    else:
        st.markdown(f'<p style="color:#c0392b;">❌ Không có dữ liệu cho {selected_tiktoker}.</p>', unsafe_allow_html=True)

# Chỉ chạy phân tích nếu dữ liệu có sẵn trong trạng thái phiên
if 'cleaned_video_info_df' in st.session_state:
    personal_analysis(st.session_state['cleaned_video_info_df'])
    display_footer()
else:
    st.warning("Vui lòng tải lên hoặc cung cấp dữ liệu video để phân tích.")