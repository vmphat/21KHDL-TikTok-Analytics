import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from user_analysis.utils.styles import personal_styles
from user_analysis.utils.footer import display_footer
from user_analysis.utils.data_loader import load_data


# Tải dữ liệu với vòng quay chờ
with st.spinner("Đang tải dữ liệu TikTok..."):
    # Tải dữ liệu
    cleaned_user_info_df, cleaned_video_info_df, cleaned_script_df = load_data()
    # Lưu trữ dữ liệu trong trạng thái phiên để các trang truy cập
    st.session_state['cleaned_user_info_df'] = cleaned_user_info_df
    st.session_state['cleaned_video_info_df'] = cleaned_video_info_df
    st.session_state['cleaned_script_df'] = cleaned_script_df


@st.cache_data
def calculate_metrics(video_df):
    """
    Tính toán các chỉ số từ dữ liệu video.
    """
    # Kiểm tra dữ liệu đầu vào
    required_cols = ['statsV2.playCount', 'statsV2.diggCount',
                     'statsV2.commentCount', 'statsV2.shareCount', 'authorStats.followerCount']
    if video_df.empty or not all(col in video_df.columns for col in required_cols):
        return None

    # Tính trung bình các chỉ số
    total_views = video_df['statsV2.playCount'].sum()
    total_likes = video_df['statsV2.diggCount'].sum()
    total_comments = video_df['statsV2.commentCount'].sum()
    total_shares = video_df['statsV2.shareCount'].sum()
    # Giả định follower count không thay đổi
    total_followers = video_df['authorStats.followerCount'].iloc[0]
    number_video = len(video_df)

    # Tính các tỷ lệ (%):
    views_per_follower = (total_views / total_followers /
                          number_video * 100) if total_followers > 0 else 0
    likes_per_view = (total_likes / total_views *
                      100) if total_views > 0 else 0
    comments_per_view = (total_comments / total_views *
                         100) if total_views > 0 else 0
    shares_per_view = (total_shares / total_views *
                       100) if total_views > 0 else 0
    engagement_rate = ((likes_per_view + comments_per_view +
                       shares_per_view + views_per_follower) / 4)

    return {
        "views_per_follower": views_per_follower,
        "likes_per_view": likes_per_view,
        "comments_per_view": comments_per_view,
        "shares_per_view": shares_per_view,
        "engagement_rate": engagement_rate
    }


def determine_level(value, ref_range):
    if value < ref_range[0]:
        return "Thấp"
    elif ref_range[0] <= value <= ref_range[1]:
        return "Trung bình"
    else:
        return "Cao"


def display_dynamic_metrics_dashboard(video_df):
    metrics_calculated = calculate_metrics(video_df)
    if metrics_calculated is None:
        st.error(
            "Không thể tính toán chỉ số do dữ liệu trống hoặc thiếu cột cần thiết.")
        return

    # Thông tin các chỉ số
    metric_definitions = [
        {"name": "Tỷ lệ tương tác", "key": "engagement_rate",
            "reference_range": [6, 11.23]},
        {"name": "Lượt xem / Lượt theo dõi",
            "key": "views_per_follower", "reference_range": [0.8, 7.56]},
        {"name": "Lượt likes / Lượt xem", "key": "likes_per_view",
            "reference_range": [6.6, 10.37]},
        {"name": "Lượt bình luận / Lượt xem",
            "key": "comments_per_view", "reference_range": [0.03, 0.05]},
        {"name": "Lượt chia sẻ / Lượt xem", "key": "shares_per_view",
            "reference_range": [0.03, 0.08]},
    ]

    color_map = {
        "Cao": "#387F39",
        "Trung bình": "#A2CA71",
        "Thấp": "#BEDC74"
    }

    st.markdown(
        """
        <div style='display: flex; align-items: center;'>
            <h3 style='margin-right: 10px;'>🟠 Số liệu chung</h3>
        </div>
        """,
        unsafe_allow_html=True
    )

    cols = st.columns(5)
    for idx, metric_def in enumerate(metric_definitions):
        key = metric_def["key"]
        # Giá trị đã là phần trăm từ calculate_metrics
        value = round(metrics_calculated[key], 2)
        ref_range = metric_def["reference_range"]
        level = determine_level(value, ref_range)

        with cols[idx]:
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=value,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': metric_def["name"], 'font': {'size': 14}},
                # Hiển thị số với định dạng phần trăm
                number={'valueformat': '.2f', 'suffix': '%'},
                gauge={
                    # Trục hiển thị phần trăm
                    'axis': {'range': [0, ref_range[1] * 1.5], 'tickformat': '.2f%'},
                    'bar': {'color': color_map[level]},

                    'steps': [
                        {'range': [0, ref_range[0]], 'color': '#FBFFE4'},
                        {'range': ref_range, 'color': '#B3D8A8'},
                        {'range': [ref_range[1], ref_range[1]
                                   * 1.5], 'color': '#FBFFE4'}
                    ],
                }
            ))

            fig.update_layout(
                height=250,
                margin=dict(l=20, r=20, t=50, b=20),
                paper_bgcolor="rgba(0,0,0,0)",
                font={'color': "#34495e"}
            )

            st.plotly_chart(fig, use_container_width=True)

            st.markdown(
                f"""
                <div style='text-align: center;'>
                    <p style='font-size: 20px; color: #41644A; font-weight: bold;'>{level}</p>
                    <p style='font-size: 14px; color: #7f8c8d;'>Khoảng trung bình của giá trị này là: {ref_range[0]}% - {ref_range[1]}%</p>
                </div>
                """,
                unsafe_allow_html=True
            )


def analyze_scripts(data_df, title="🔍 Phân tích kịch bản", user_context="người dùng được chọn"):
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
    st.subheader(title)

    # Phân tích và visualize các trường bằng bar chart
    fields_to_visualize = {
        "main_content_focus": "Chủ đề chính",
        "structure_style": "Phong cách nội dung",
        "hook_type": "Loại móc câu",
        "tone_of_voice": "Giọng điệu",
        "pacing": "Tốc độ"
    }
    if not data_df.empty:
        # ông sửa ở đây nè :
        st.markdown("### Phân tích tổng quát")
        for field, field_name in fields_to_visualize.items():
            # Đếm tần suất các giá trị trong trường (explode vì dữ liệu có thể là danh sách)
            value_counts = data_df[field].explode(
            ).value_counts().reset_index()
            value_counts.columns = [field_name, "Số lượng"]

            # Tạo bar chart
            fig = px.bar(
                value_counts,
                x=field_name,
                y="Số lượng",
                text=value_counts["Số lượng"].apply(lambda x: f"{int(x):,}"),
                template="plotly_white",
                color=field_name,
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            fig.update_traces(textposition="auto")
            fig.update_layout(
                showlegend=False,
                height=400,
                title=f"Phân phối {field_name}",
                xaxis_title=field_name,
                yaxis_title="Số lượng"
            )
            st.plotly_chart(fig, use_container_width=True)

    # Dòng giới thiệu
    st.markdown(
        f"_Lọc và khám phá video với thông tin chi tiết cho {user_context}._")
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
        st.write(" ")
        st.write(" ")
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
        filtered_df = filtered_df[filtered_df["main_content_focus"].apply(
            lambda x: any(i in selected_main_focus for i in x))]
    if selected_structure_style:
        filtered_df = filtered_df[filtered_df["structure_style"].apply(
            lambda x: any(i in selected_structure_style for i in x))]
    if selected_hook_type:
        filtered_df = filtered_df[filtered_df["hook_type"].apply(
            lambda x: any(i in selected_hook_type for i in x))]
    if selected_tone:
        filtered_df = filtered_df[filtered_df["tone_of_voice"].apply(
            lambda x: any(i in selected_tone for i in x))]
    if selected_pacing:
        filtered_df = filtered_df[filtered_df["pacing"].apply(
            lambda x: any(i in selected_pacing for i in x))]

    # Hiển thị kết quả đã lọc
    st.subheader("📊 Thông tin chi tiết về video")
    if filtered_df.empty:
        st.warning(
            f"Không có video nào khớp với bộ lọc đã chọn cho {user_context}.")
    else:
        st.info(
            f"Hiển thị thông tin chi tiết cho {len(filtered_df)} video phù hợp.")

        display_dynamic_metrics_dashboard(filtered_df)

        col1, col2 = st.columns(2)
        with col1:
            # Biểu đồ cột số liệu tương tác
            st.markdown("### Tổng quan tương tác")
            engagement_agg = filtered_df[["statsV2.playCount", "statsV2.diggCount", "statsV2.commentCount",
                                          "statsV2.shareCount", "statsV2.collectCount"]].mean().reset_index()
            engagement_agg.columns = ["Chỉ số", "Số lượng trung bình"]
            engagement_agg["Chỉ số"] = ["Lượt xem",
                                        "Lượt thích", "Bình luận", "Chia sẻ", "Lưu"]
            fig_eng = px.bar(
                engagement_agg, x="Chỉ số", y="Số lượng trung bình",
                text=engagement_agg["Số lượng trung bình"].apply(
                    lambda x: f"{int(x):,}"),
                template="plotly_white", color="Chỉ số", color_discrete_sequence=px.colors.qualitative.Pastel
            )
            fig_eng.update_traces(textposition="auto")
            fig_eng.update_layout(showlegend=False, height=400)
            st.plotly_chart(fig_eng, use_container_width=True)
        with col2:
            # Biểu đồ tròn sử dụng hashtag
            st.markdown("### Hashtag hàng đầu")
            hashtag_counts = filtered_df["hashtags"].explode(
            ).value_counts().head(10).reset_index()
            hashtag_counts.columns = ["Hashtag", "Số lượng"]
            fig_hashtag = px.pie(
                hashtag_counts, names="Hashtag", values="Số lượng",
                template="plotly_white", color_discrete_sequence=px.colors.qualitative.Pastel
            )
            fig_hashtag.update_layout(height=400)
            st.plotly_chart(fig_hashtag, use_container_width=True)

        # Phân phối thời lượng video
        st.markdown("### Phân phối thời lượng video")
        fig_duration = px.histogram(
            filtered_df, x="video.duration", nbins=20, title="",
            template="plotly_white", color_discrete_sequence=["#3498db"]
        )
        fig_duration.update_layout(
            height=400, xaxis_title="Thời lượng (giây)", yaxis_title="Số lượng")
        st.plotly_chart(fig_duration, use_container_width=True)

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
        display_df['createTime'] = display_df['createTime'].dt.strftime(
            '%Y-%m-%d')
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
    required_columns = ['author.uniqueId',
                        'createTime', 'hashtags', 'music.authorName']
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
                               value=(
                                   st.session_state['start_date'], st.session_state['end_date']),
                               format="MM/DD/YYYY")
        # Cập nhật trạng thái phiên với các đối tượng ngày
        st.session_state['start_date'], st.session_state['end_date'] = date_range[0], date_range[1]
        if st.button("🔄 Đặt lại"):
            st.session_state['start_date'] = min_date
            st.session_state['end_date'] = max_date
            st.rerun()  # Chạy lại để cập nhật thanh trượt

    st.header(f"Phân tích của @{selected_tiktoker}")
    tiktoker_data = cleaned_video_info_df[cleaned_video_info_df['author.uniqueId']
                                          == selected_tiktoker]
    tiktoker_script = cleaned_script_df[cleaned_script_df['author.uniqueId']
                                        == selected_tiktoker]

    if not tiktoker_data.empty:
        user_info = tiktoker_data.iloc[0]
        with st.container():
            st.subheader("Tổng quan hồ sơ")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Tên người dùng", user_info['author.uniqueId'])
                st.metric("Người theo dõi",
                          f"{user_info.get('authorStats.followerCount', 0):,}")
            with col2:
                st.metric("Thương mại", user_info.get(
                    'user.commerceUserInfo.category', 'Không có thông tin'))
                st.metric("Tổng lượt thích",
                          f"{user_info.get('authorStats.heartCount', 0):,}")
            with col3:
                st.metric("Đã xác minh", "Có ✅" if user_info.get(
                    'author.verified', False) else "Không ❌")
                st.metric("Tổng số video",
                          f"{user_info.get('authorStats.videoCount', 0):,}")

        with st.spinner("Đang tải dữ liệu..."):
            filtered_data = tiktoker_data[(tiktoker_data['createTime'] >= pd.to_datetime(st.session_state['start_date'])) &
                                          (tiktoker_data['createTime'] <= pd.to_datetime(st.session_state['end_date']))]

    if not filtered_data.empty:
        st.subheader("Phân tích đăng tải")
        st.markdown("📅 Lịch sử đăng bài", unsafe_allow_html=True)
        video_counts = filtered_data.groupby(
            filtered_data['createTime'].dt.date).size().reset_index(name='Số lượng video')
        fig = px.area(video_counts, x='createTime', y='Số lượng video',
                      template="plotly_white")
        fig.update_traces(
            line=dict(color="#FF9149", width=2), fill='tozeroy')
        fig.add_scatter(x=video_counts['createTime'], y=video_counts['Số lượng video'],
                        mode='markers', marker=dict(size=8, color="#EA7300"))
        max_day = video_counts.loc[video_counts['Số lượng video'].idxmax()]
        fig.add_annotation(x=max_day['createTime'], y=max_day['Số lượng video'],
                           text=f"Đỉnh: {max_day['Số lượng video']}", showarrow=True, arrowhead=1)
        fig.update_layout(xaxis_title="Ngày",
                          yaxis_title="Video đã đăng", showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

        # Phần "Phân tích lịch đăng bài theo tháng"
        st.markdown("📅 Phân tích lịch đăng bài theo tháng",
                    unsafe_allow_html=True)
        # Chọn tháng để phân tích
        col1, col2 = st.columns([1, 2])
        with col1:
            filtered_data['createTime'] = pd.to_datetime(
                filtered_data['createTime'])
            available_months = filtered_data['createTime'].dt.to_period(
                'M').unique()
            selected_month = st.selectbox(
                "Chọn tháng để phân tích", available_months, format_func=lambda x: x.strftime('%m/%Y'))

            # Lọc dữ liệu theo tháng được chọn
            month_data = filtered_data[filtered_data['createTime'].dt.to_period(
                'M') == selected_month]

        if not month_data.empty:
            with col1:
                # 1. Calendar Heatmap
                month_data['day'] = month_data['createTime'].dt.day

                # Lấy số ngày tối đa trong tháng
                max_days = pd.Period(selected_month).days_in_month

                # Đếm số lượng bài đăng theo ngày và reindex đến max_days
                daily_counts = month_data.groupby('day').size().reindex(
                    range(1, max_days + 1), fill_value=0).reset_index(name='Số lượng')

                # Tạo cột ngày hợp lệ
                daily_counts['date'] = pd.to_datetime(
                    f"{selected_month.year}-{selected_month.month}-" +
                    daily_counts['day'].astype(str),
                    # Bỏ qua lỗi nếu có (không cần thiết với max_days, nhưng để an toàn)
                    errors='coerce'
                )
                # 0 = Thứ 2, 6 = Chủ nhật
                daily_counts['weekday'] = daily_counts['date'].dt.weekday

                # Tạo calendar heatmap
                fig_cal = go.Figure(data=go.Heatmap(
                    z=daily_counts['Số lượng'],
                    x=daily_counts['weekday'],
                    y=daily_counts['day'],
                    colorscale='Oranges',
                    text=daily_counts['Số lượng'].astype(str),
                    hoverinfo='text',
                    showscale=True
                ))
                fig_cal.update_layout(
                    title=f"Lịch đăng bài - {selected_month.strftime('%m/%Y')}",
                    xaxis=dict(
                        tickmode='array',
                        tickvals=[0, 1, 2, 3, 4, 5, 6],
                        ticktext=['Thứ 2', 'Thứ 3', 'Thứ 4',
                                  'Thứ 5', 'Thứ 6', 'Thứ 7', 'Chủ nhật']
                    ),
                    yaxis=dict(title='Ngày trong tháng', autorange='reversed'),
                    height=500
                )
                st.plotly_chart(fig_cal, use_container_width=True)
            with col2:
                # 2. Chỉ số thống kê
                st.subheader("Chỉ số thống kê")
                total_posts = len(month_data)
                weeks_in_month = (
                    month_data['createTime'].dt.days_in_month.max() / 7)
                avg_posts_per_week = total_posts / weeks_in_month
                latest_post_date = month_data['createTime'].max().strftime(
                    '%Y-%m-%d')

                # Xác định cấp độ tần suất
                if total_posts < 6:
                    frequency_level = "Ít"
                elif 6 <= total_posts <= 10:
                    frequency_level = "Trung bình"
                else:
                    frequency_level = "Nhiều"

                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Tổng số bài đăng", total_posts)
                with col2:
                    st.metric("Trung bình mỗi tuần",
                              f"{avg_posts_per_week:.1f}")
                with col3:
                    st.metric("Ngày đăng gần nhất", latest_post_date)
                with col4:
                    st.metric("Cấp độ tần suất", frequency_level)

                # 3. Biểu đồ tần suất đăng theo thứ trong tuần
                st.subheader("Tần suất đăng theo thứ trong tuần")
                weekday_counts = month_data['createTime'].dt.weekday.value_counts().reindex(
                    range(7), fill_value=0)
                weekday_percentages = (
                    weekday_counts / total_posts * 100).reset_index()
                weekday_percentages.columns = ['Thứ', 'Tỷ lệ (%)']
                weekday_percentages['Thứ'] = [
                    'Thứ 2', 'Thứ 3', 'Thứ 4', 'Thứ 5', 'Thứ 6', 'Thứ 7', 'Chủ nhật']

                fig_weekday = px.bar(
                    weekday_percentages,
                    x='Thứ',
                    y='Tỷ lệ (%)',
                    text=weekday_percentages['Tỷ lệ (%)'].apply(
                        lambda x: f"{x:.1f}%"),
                    color_discrete_sequence=['#FF6200'],  # Màu cam
                    template="plotly_white"
                )
                fig_weekday.update_traces(textposition='auto')
                fig_weekday.update_layout(
                    yaxis_title="Tỷ lệ phần trăm (%)",
                    showlegend=False,
                    height=400
                )
                st.plotly_chart(fig_weekday, use_container_width=True)

        else:
            st.warning(
                f"Không có dữ liệu cho tháng {selected_month.strftime('%m/%Y')}.")
        st.subheader("Sở thích cá nhân")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("🏷️ Sử dụng hashtag", unsafe_allow_html=True)
            all_hashtags = filtered_data['hashtags'].dropna(
            ).str.split().explode()
            if not all_hashtags.empty:
                hashtag_counts = all_hashtags.value_counts().head(10).reset_index()
                hashtag_counts.columns = ['Hashtag', 'Số lượng']
                fig = px.treemap(hashtag_counts, path=['Hashtag'], values='Số lượng',
                                 title="Top 10 hashtag", color='Số lượng', color_continuous_scale='aggrnyl')
                fig.update_layout(margin=dict(t=50, l=0, r=0, b=0))
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.markdown(
                    '<p style="color:#3498db;">ℹ️ Không có hashtag nào.</p>', unsafe_allow_html=True)
        with col2:
            st.markdown("🎵 Sử dụng âm nhạc")
            if 'music.authorName' not in filtered_data.columns:
                st.warning("Dữ liệu không chứa cột 'music.authorName'.")
                return

            # Đếm số lần xuất hiện của mỗi tác giả âm nhạc
            music_counts = filtered_data['music.authorName'].value_counts().head(
                10)

            # Tính phần trăm so với tổng số video
            total_videos = len(filtered_data)
            music_percentages = (music_counts / total_videos * 100).round(1)

            # Chuẩn bị dữ liệu hiển thị
            music_bars = [
                (author, percent, color)
                for author, percent, color in zip(
                    music_counts.index,
                    music_percentages,
                    px.colors.qualitative.Safe[:len(
                        music_counts)]  # Màu từ Plotly
                )
            ]

            # Hiển thị bằng HTML progress bars
            for author, percent, color in music_bars:
                st.markdown(
                    f"""
                    <div style="margin-bottom: 10px;">
                        <div style="display: flex; justify-content: space-between; font-weight: bold;">
                            <span>{author}</span>
                            <span>{percent:.1f}%</span>
                        </div>
                        <div style="height: 8px; background-color: #eee; border-radius: 6px;">
                            <div style="width: {percent}%; background-color: {color}; height: 100%; border-radius: 6px;"></div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        analyze_scripts(tiktoker_script)
    else:
        st.markdown(
            f'<p style="color:#e67e22;">⚠️ Không có dữ liệu video cho {selected_tiktoker} trong phạm vi này.</p>', unsafe_allow_html=True)


# Chỉ chạy phân tích nếu dữ liệu có sẵn trong trạng thái phiên
if 'cleaned_video_info_df' in st.session_state:
    personal_analysis(st.session_state['cleaned_video_info_df'])
    display_footer()
else:
    st.warning("Vui lòng tải lên hoặc cung cấp dữ liệu video để phân tích.")
