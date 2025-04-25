import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from google import genai
from typing import List, Tuple, Dict
import scipy.stats as stats


# ================================================================
# *_____________________ [Define constants] _____________________*
# ================================================================
DARK_GRAY: str = "#444444"
CLEANED_USER_DATA_FILE: str = "data/processed/cleaned_user_info.parquet"
COLUMN_TO_AXIS_TITLE: Dict[str, str] = {
    "stats.videoCount": "Số video",
    "stats.followerCount": "Số người theo dõi",
    "stats.heartCount": "Số lượt thích",
    "avg_comments_per_video": "Số bình luận trên mỗi video",
    "avg_diggs_per_video": "Số lượt thích trên mỗi video",
    "avg_plays_per_video": "Số lượt xem trên mỗi video",
    "avg_shares_per_video": "Số lượt chia sẻ trên mỗi video",
    "avg_collects_per_video": "Số lượt lưu trên mỗi video",
    "avg_videos_per_week": "Số video mỗi tuần",
    "avg_hashtags_per_video": "Số hashtag mỗi video",
    "avg_video_duration": "Thời gian video (giây)",
}


# ================================================================
# *____________________ [Utility functions] _____________________*
# ================================================================
# Hàm giúp tạo nhận xét và rút ra insights từ kết quả phân tích và trực quan hóa dữ liệu
@st.cache_data(show_spinner=False)
def generate_insights(prompt: str, api_key: str) -> str:
    # return "[TEMPORARY] Chức năng này hiện đang tạm dừng hoạt động."
    """ Tạo nhận xét từ Gemini API """
    # Generate content
    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model="gemini-2.0-flash-lite",
            contents=[prompt]
        )
        return response.text
    except Exception as e:
        print(f"Lỗi khi tạo nội dung: {e}")
        return ""


# Tạo 1 module dành riêng cho việc rút trích insights từ biểu đồ
# và thể hiện lên trang web
def display_AI_generated_insights(prompt: str, api_key: str,
                                  print_to_console: bool = False,
                                  expanded: bool = True
                                  ) -> None:
    """ End-to-end module để rút trích insights từ biểu đồ và hiện thị lên trang web """

    with st.expander(
            label=":blue-background[:blue[**:material/auto_awesome: Nhận xét từ AI**]]",
            expanded=expanded):
        # Tạo nhận xét từ Gemini API
        with st.spinner(text="Đang tạo nhận xét từ AI...", show_time=True):
            insights = generate_insights(prompt=prompt, api_key=api_key)
            if not insights:
                st.error("Hiện tại hệ thống đang quá tải, vui lòng thử lại sau.")
            else:
                st.markdown(insights)
                if print_to_console:
                    print(f"Nhận xét từ AI:\n{insights}")


# Tải dữ liệu
# @st.cache_data
def load_user_data() -> pd.DataFrame:
    """ Tải và lưu trữ dữ liệu người dùng đã được làm sạch từ tệp """
    if CLEANED_USER_DATA_FILE.endswith(".csv"):
        return pd.read_csv(CLEANED_USER_DATA_FILE)
    elif CLEANED_USER_DATA_FILE.endswith(".parquet"):
        return pd.read_parquet(CLEANED_USER_DATA_FILE)

    return None


# Hàm tính tỷ lệ tương tác
@st.cache_data
def calculate_engagement_ratio(df: pd.DataFrame) -> pd.DataFrame:
    """ Tính toán tỷ lệ tương tác cho từng người dùng """
    df['engagement_ratio'] = (
        df['stats.heartCount'] /
        df['stats.followerCount'].replace(0, 1)
    )
    return df


# Hàm tính số lượt like trung bình trên mỗi video của mỗi user
@st.cache_data
def calculate_avg_likes_per_video(df: pd.DataFrame) -> pd.DataFrame:
    """ Tính toán số lượt thích trung bình trên mỗi video """
    df['avg_likes_per_video'] = df['stats.heartCount'] / \
        df['stats.videoCount'].replace(0, 1)
    return df


# Hàm tính các giá trị phân vị để lọc dữ liệu
@st.cache_data
def calculate_percentiles(df: pd.DataFrame,
                          percentiles: List[float]) -> Tuple[float, float, float, float]:
    """ Tính toán các giá trị phân vị cho người theo dõi và tương tác """

    low_followers = df['stats.followerCount'].quantile(percentiles[1])
    high_followers = df['stats.followerCount'].quantile(percentiles[2])
    low_engagement = df['engagement_ratio'].quantile(percentiles[1])
    high_engagement = df['engagement_ratio'].quantile(percentiles[2])

    return low_followers, high_followers, low_engagement, high_engagement


# Hàm lọc dữ liệu theo mức độ tương tác và người theo dõi
@st.cache_data
def filter_data(df: pd.DataFrame, follower_level: str, engagement_level: str,
                low_followers: float, high_followers: float,
                low_engagement: float, high_engagement: float
                ) -> pd.DataFrame:
    """ Lọc dữ liệu theo mức độ tương tác và người theo dõi """

    # Lọc theo mức người theo dõi
    if follower_level == "Thấp":
        filtered_df = df[df['stats.followerCount'] <= low_followers]
    elif follower_level == "Trung bình":
        filtered_df = df[
            (df['stats.followerCount'] > low_followers) &
            (df['stats.followerCount'] <= high_followers)
        ]
    else:
        filtered_df = df[df['stats.followerCount'] > high_followers]

    # # Lọc theo mức tương tác
    # if engagement_level == "Thấp":
    #     filtered_df = filtered_df[
    #         filtered_df['engagement_ratio'] <= low_engagement]
    # elif engagement_level == "Trung bình":
    #     filtered_df = filtered_df[
    #         (filtered_df['engagement_ratio'] > low_engagement) &
    #         (filtered_df['engagement_ratio'] <= high_engagement)
    #     ]
    # else:
    #     filtered_df = filtered_df[
    #         filtered_df['engagement_ratio'] > high_engagement]

    return filtered_df


# Hàm để vẽ biểu đồ scatter plot thể hiện mối quan hệ giữa người theo dõi và mức độ tương tác
@st.cache_data(show_spinner=False)
def plot_engagement_scatter(df: pd.DataFrame, x_col: str, y_col: str,
                            color: str = None) -> Tuple[go.Figure, float]:
    """ Vẽ biểu đồ phân tán thể hiện mối quan hệ giữa người theo dõi và mức độ tương tác """

    # Tạo biểu đồ phân tán
    fig = px.scatter(
        df, x=x_col, y=y_col,

        # color='lightblue',
        # color_continuous_scale='Teal',
        hover_data=['user.uniqueId'],
        height=400,
        opacity=0.8,

        # Vẽ regression line trên biểu đồ phân tán
        trendline="ols",
        trendline_color_override="#f56b69",
        trendline_options=dict(
            log_x=True,
            log_y=True,
            add_constant=True,
        ),

    )

    # Cập nhật marker và màu sắc
    fig.update_traces(
        marker=dict(
            line=dict(width=1, color=DARK_GRAY),
            size=10,
            color=color,
            opacity=0.8,
        ),
    )

    # Hiển thị hệ số tương quan giữa 2 biến x và y
    corr = df[x_col].corr(df[y_col])
    fig.add_annotation(
        text=f" ρ = {corr:.2f} ",
        xref="paper",
        yref="paper",
        x=0.95,
        y=0.95,
        showarrow=False,
        font=dict(size=18, color=DARK_GRAY),
        bgcolor='#e7f4ea',
        bordercolor='#39a342',
        borderwidth=1,
    )

    # Cập nhật bố cục biểu đồ
    fig.update_layout(
        xaxis_title=COLUMN_TO_AXIS_TITLE[x_col],
        yaxis_title=COLUMN_TO_AXIS_TITLE[y_col],
        xaxis_type="log",
        yaxis_type="log",
        # showlegend=True,
        # coloraxis_colorbar_title="Tỷ lệ tương tác 🔥",

        # Thay đổi màu nền và kích thước tiêu đề
        plot_bgcolor="#fafafa",
        # title_x=0.5,
        title_y=0.95,
        # title_xanchor="right",
        title_yanchor="top",
        title_font_size=20,
        title_font_color=DARK_GRAY,
        title_text=f"Mối tương quan giữa {COLUMN_TO_AXIS_TITLE[x_col]}<br />và {COLUMN_TO_AXIS_TITLE[y_col]}",
        title_font_family="Arial",

        # Thay đổi kích thước x, y-axis label
        xaxis_title_font=dict(size=16),
        yaxis_title_font=dict(size=16),

        # Thay đổi kích thước x, y-axis tick labels
        xaxis_tickfont=dict(size=14),
        yaxis_tickfont=dict(size=14),
    )

    return fig, corr


# ================================================================
# *_______________________ [Basic setup] ________________________*
# ================================================================
# Cấu hình Streamlit
st.set_page_config(
    page_title="Engagement Insights",
    page_icon="📊",
    layout="wide",
)
# Tiêu đề trang
st.title("📊 Phân tích đặc điểm và hiệu suất giữa các nhóm TikToker khác nhau")
st.write(
    "So sánh các chỉ số tương tác, tần suất đăng tải, và đặc điểm nội dung giữa các nhóm người dùng có mức độ người theo dõi khác nhau.")

# Custom CSS for better styling
st.markdown("""
<style>
    .card {background-color: #F3F4F6; border-radius: 8px; padding: 1.2rem; margin-bottom: 1rem; border-left: 4px solid #2563EB;}
    .card-title {font-size: 1.2rem; font-weight: 600; color: #1E40AF;}
</style>
""", unsafe_allow_html=True)


# ================================================================
# *_______________ [Read data and set up styles] ________________*
# ================================================================
# Tải dữ liệu đã lưu trữ
cleaned_user_info_df: pd.DataFrame = load_user_data()
print(cleaned_user_info_df.columns)


# ================================================================
# *___________________ [Data transformation] ____________________*
# ================================================================
# Tính tỷ lệ tương tác
cleaned_user_info_df = calculate_engagement_ratio(
    cleaned_user_info_df)

# Tính số lượng like trung bình trên mỗi video
cleaned_user_info_df = calculate_avg_likes_per_video(
    cleaned_user_info_df)

# Xác định các phân vị để lọc
percentiles = [0, 0.33, 0.66, 1]
low_followers, high_followers, low_engagement, high_engagement = \
    calculate_percentiles(cleaned_user_info_df, percentiles)


# ================================================================
# *_________________ [Display follower levels] __________________*
# ================================================================
# Feature cards in 3 columns
follower_col1, follower_col2, follower_col3 = st.columns(3)

# Xác định những người dùng thuộc nhóm người theo dõi thấp, trung bình và cao
with follower_col1:
    st.markdown(f"""
    <div class="card">
        <div class="card-title">🥉 Nhóm người theo dõi thấp</div>
        <p>Những người dùng có số người theo dõi thấp hơn <b>{low_followers:,.0f}</b>.</p>
        <p>Những người dùng này có thể là những người mới bắt đầu hoặc chưa có nhiều nội dung nổi bật.</p>
    </div>
    """, unsafe_allow_html=True)
with follower_col2:
    st.markdown(f"""
    <div class="card">
        <div class="card-title">🥈 Nhóm người theo dõi trung bình</div>
        <p>Những người dùng có số người theo dõi nằm trong khoảng <b>{low_followers:,.0f} - {high_followers:,.0f}</b>.</p>
        <p>Những người dùng này có thể là những người mới nổi hoặc có ảnh hưởng vừa phải trên TikTok.</p>
    </div>
    """, unsafe_allow_html=True)
with follower_col3:
    st.markdown(f"""
    <div class="card">
        <div class="card-title">🥇 Nhóm người theo dõi cao</div>
        <p>Những người dùng có số người theo dõi cao hơn <b>{high_followers:,.0f}</b>.</p>
        <p>Những người dùng này có thể là những người nổi tiếng hoặc có ảnh hưởng lớn trên TikTok.</p>
    </div>
    """, unsafe_allow_html=True)


# ================================================================
# *_________________ [UI for selecting filters] _________________*
# ================================================================
# Cho người dùng chọn các bộ lọc
st.subheader(
    body="🔍 Chọn bộ lọc để phân tích",
    help="Chọn các bộ lọc để phân tích mức độ tương tác của người dùng TikTok.",
)
follower_level = st.selectbox(
    label=":blue[**Chọn mức người theo dõi:**]",
    options=["Thấp", "Trung bình", "Cao"]
)
# engagement_level = st.selectbox(
#     label="🔥 :orange[**Chọn mức tương tác:**]",
#     options=["Thấp", "Trung bình", "Cao"]
# )
engagement_level = None

# Lọc dữ liệu theo mức độ tương tác và người theo dõi
filtered_df = filter_data(
    df=cleaned_user_info_df,
    follower_level=follower_level,
    engagement_level=engagement_level,
    low_followers=low_followers,
    high_followers=high_followers,
    low_engagement=low_engagement,
    high_engagement=high_engagement
)

# Số lượng người dùng
st.info(
    body=f"📌 Số người dùng trong nhóm có mức độ người theo dõi **{follower_level}** là: **{len(filtered_df):,}**",
)


# ================================================================
# *___________________ [Display basic stats] ____________________*
# ================================================================
# Hiển thị tiêu đề cho biểu đồ
st.header(
    # body=f"Thông tin chi tiết về tương tác: Số người theo dõi {follower_level} & Mức độ tương tác {engagement_level}",
    body=f"Thông tin chi tiết về mức độ tương tác của các TikToker có số người theo dõi {follower_level}",
)

# Hiển thị số liệu thống kê
# Số người dùng
# stats.followerCount    | avg_likes_per_video    | avg_videos_per_week
# avg_plays_per_video    | avg_shares_per_video   | avg_hashtags_per_video
# avg_comments_per_video | avg_collects_per_video | avg_video_duration

# 22  avg_videos_per_week                 264 non-null    float64
# 23  avg_collects_per_video              264 non-null    float64
# 24  avg_comments_per_video              264 non-null    float64
# 25  avg_diggs_per_video                 264 non-null    float64
# 26  avg_plays_per_video                 264 non-null    float64
# 27  avg_shares_per_video                264 non-null    float64
# 28  avg_video_duration                  264 non-null    float64
# 29  avg_hashtags_per_video              264 non-null    float64
col1, col2, col3 = st.columns(spec=3, gap="small", border=False)
with col1:
    # Số lượng người theo dõi trung bình
    st.metric(label="👀 Số người theo dõi",
              value=f"{filtered_df['stats.followerCount'].mean():,.0f}",
              border=True,
              )
    # Số lượt xem trên mỗi video
    st.metric(label="👁️ Số lượt xem trên mỗi video",
              value=f"{filtered_df['avg_plays_per_video'].mean():,.0f}",
              border=True,
              )
    # Số lượt bình luận trên mỗi video
    st.metric(label="💬 Số bình luận trên mỗi video",
              value=f"{filtered_df['avg_comments_per_video'].mean():,.0f}",
              border=True,
              )
with col2:
    # Số lượng thích trung bình trên mỗi video
    st.metric(label="💖 Số lượt thích trên mỗi video",
              value=f"{filtered_df['avg_likes_per_video'].mean():,.0f}",
              border=True,
              )
    # Số lượt chia sẻ trên mỗi video
    st.metric(label="🔗 Số lượt chia sẻ trên mỗi video",
              value=f"{filtered_df['avg_shares_per_video'].mean():,.0f}",
              border=True,
              )
    # Số lượt lưu trên mỗi video
    st.metric(label="💾 Số lượt lưu trên mỗi video",
              value=f"{filtered_df['avg_collects_per_video'].mean():,.0f}",
              border=True,
              )
with col3:
    # Số lượng video trung bình trong mỗi tuần (calendar emoji)
    st.metric(label="📅 Số video mỗi tuần",
              value=f"{filtered_df['avg_videos_per_week'].mean():,.1f} ± {filtered_df['avg_videos_per_week'].std():,.1f}",
              border=True,
              )
    # Số lượng hashtag trên mỗi video
    st.metric(label="🏷️ Số hashtag trên mỗi video",
              value=f"{filtered_df['avg_hashtags_per_video'].mean():,.1f} ± {filtered_df['avg_hashtags_per_video'].std():,.1f}",
              border=True,
              )
    # Thời lượng video trung bình
    st.metric(label="⏱️ Thời lượng video (giây)",
              value=f"{filtered_df['avg_video_duration'].mean():,.1f} ± {filtered_df['avg_video_duration'].std():,.1f}",
              border=True,
              )


# ================================================================
# *___________________ [Engagement Analysis] ____________________*
# ================================================================
st.divider()
# Research question
st.header(":blue-background[:blue[Câu hỏi:]] Với cùng một ngưỡng số người theo dõi nhất định, liệu việc tăng số lượng video có thực sự đem lại nhiều lượt xem và lượt tương tác hơn trên mỗi video, hay chỉ đơn thuần tạo ra nhiều lượt xem và tương tác tổng?")
# Answer
with st.expander(label=":green[**:material/check_box: Trả lời**]", expanded=False):
    st.markdown(f"""
    **Kết quả phân tích chính và Nhận xét tổng quát:**

    Qua phân tích mối tương quan giữa **Tổng số video đăng tải** và các chỉ số **Lượt xem/Lượt thích/Lượt bình luận/Lượt chia sẻ trung bình trên mỗi video**, một xu hướng nhất quán đã được quan sát và có thể tổng quát hóa cho cả ba nhóm người dùng (Thấp, Trung bình, Cao về số người theo dõi):

    1.  **Mối tương quan nghịch giữa Số lượng video và Tương tác trên mỗi video:**

        - Đối với tất cả các chỉ số tương tác được phân tích (Lượt xem, Lượt thích, Lượt bình luận, Lượt chia sẻ), đều tồn tại mối tương quan **nghịch** với tổng số lượng video đăng tải. Điều này có nghĩa là, nhìn chung, khi một TikToker đăng tải **càng nhiều video**, thì lượng tương tác trung bình (lượt xem, lượt thích, bình luận, chia sẻ) mà **mỗi video riêng lẻ** nhận được có xu hướng **giảm xuống**.
        - Mối tương quan nghịch này thể hiện rõ nhất ở **Lượt xem** và **Lượt thích**, và yếu dần ở **Lượt bình luận** và **Lượt chia sẻ**. Điều này cho thấy việc tăng số lượng video tác động mạnh hơn đến lượt xem và lượt thích trên từng video so với lượt bình luận và chia sẻ.
        - Đường xu hướng trên các biểu đồ phân tán đều minh họa xu hướng giảm của tương tác trên mỗi video khi số lượng video tăng lên.

    2.  **Sự đánh đổi giữa Số lượng và Chất lượng (trên mỗi video):**
        - Kết quả này nhấn mạnh sự đánh đổi tiềm ẩn giữa số lượng và hiệu quả tương tác trên từng video. Mặc dù việc đăng nhiều video hơn có thể làm tăng tổng số lượt xem/tương tác kênh nhận được (do số lượng nội dung nhiều hơn), nó dường như lại làm "loãng" mức độ tương tác trung bình mà mỗi video đơn lẻ có thể thu hút.
        - Quan sát về các TikToker có **ít video nhưng đạt lượt tương tác trung bình trên mỗi video rất cao** (nằm ở góc trên bên trái của các biểu đồ phân tán) củng cố nhận định này. Những nhà sáng tạo này có thể đang tập trung vào việc sản xuất nội dung chất lượng cao, độc đáo, hoặc tìm được thị trường ngách hiệu quả, giúp tối đa hóa hiệu quả tương tác của từng video mà không cần đăng bài ồ ạt.

    **Hàm ý cho Nhà sáng tạo nội dung (Tổng quát cho mọi nhóm):**

    Dựa trên mối tương quan nghịch được quan sát, chiến lược "chất lượng hơn số lượng" (trên mỗi video) dường như là một yếu tố quan trọng để tối đa hóa mức độ tương tác trung bình cho từng nội dung.

    - **Ưu tiên Chất lượng Nội dung:** Thay vì chỉ tập trung vào việc tăng tần suất đăng bài để có nhiều nội dung hơn, các nhà sáng tạo ở mọi nhóm (Thấp, Trung bình, Cao) nên ưu tiên đầu tư thời gian, công sức vào việc sản xuất các video có chất lượng cao, hấp dẫn, độc đáo và phù hợp với đối tượng mục tiêu.
    - **Tối ưu hóa Tương tác trên từng Video:** Chú trọng vào các yếu tố giúp tăng tương tác trên mỗi video như nội dung giá trị, hình ảnh/âm thanh thu hút, kêu gọi hành động (call-to-action) rõ ràng, tương tác với bình luận của người xem, v.v..
    - **Cân bằng giữa Số lượng và Chất lượng:** Nhà sáng tạo cần tìm ra sự cân bằng phù hợp giữa tần suất đăng bài đều đặn và việc duy trì chất lượng cho từng video để tối ưu hóa cả tổng tương tác kênh và hiệu quả của từng nội dung.

    **Kết luận:**

    Phân tích này cho thấy một xu hướng rõ ràng: việc tăng tổng số lượng video đăng tải có mối liên hệ tiêu cực với hiệu quả tương tác trung bình trên mỗi video. Điều này nhấn mạnh tầm quan trọng của chất lượng nội dung và chiến lược tối ưu hóa từng video đối với các nhà sáng tạo TikTok, bất kể họ đang ở mức độ người theo dõi nào.
    """)

# Hiển thị trực quan với vòng quay chờ
with st.spinner(text="Đang tải biểu đồ...", show_time=True):
    row1_col1, row1_col2 = st.columns(2, gap="small", border=True)
    with row1_col1:
        # Vẽ biểu đồ phân tán thể hiện mối quan hệ giữa
        # số video và số lượt xem trên mỗi video
        scatter_fig1, corr1 = plot_engagement_scatter(
            df=filtered_df, x_col="stats.videoCount",
            y_col="avg_plays_per_video", color="#FFD2A0"
        )
        # Hiển thị biểu đồ
        st.plotly_chart(scatter_fig1, use_container_width=True)
    with row1_col2:
        # Vẽ biểu đồ phân tán thể hiện mối quan hệ giữa
        # số video và số lượt thích trên mỗi video
        scatter_fig2, corr2 = plot_engagement_scatter(
            df=filtered_df, x_col="stats.videoCount",
            y_col="avg_diggs_per_video", color="#B7B1F2"
        )
        # Hiển thị biểu đồ
        st.plotly_chart(scatter_fig2, use_container_width=True)

    row2_col1, row2_col2 = st.columns(2, gap="small", border=True)
    with row2_col1:
        # Vẽ biểu đồ phân tán thể hiện mối quan hệ giữa
        # số video và số lượt bình luận trên mỗi video
        scatter_fig3, corr3 = plot_engagement_scatter(
            df=filtered_df, x_col="stats.videoCount",
            y_col="avg_comments_per_video", color="#91e3fa"
        )
        # Hiển thị biểu đồ
        st.plotly_chart(scatter_fig3, use_container_width=True)
    with row2_col2:
        # Vẽ biểu đồ phân tán thể hiện mối quan hệ giữa
        # số video và số lượt chia sẻ trên mỗi video
        scatter_fig4, corr4 = plot_engagement_scatter(
            df=filtered_df, x_col="stats.videoCount",
            y_col="avg_shares_per_video", color="#ffa9d0"
        )
        # Hiển thị biểu đồ
        st.plotly_chart(scatter_fig4, use_container_width=True)

# Function to create a specific prompt for a single chart


def create_single_chart_prompt(chart_type: str, metric_name: str, corr: float, df: pd.DataFrame) -> str:
    return f"""
    Hãy phân tích mối quan hệ giữa 'Số lượng video' của TikToker với '{metric_name}' dựa trên biểu đồ phân tán này.
    Hệ số tương quan (ρ = {corr:.2f}) cho biết điều gì về mối quan hệ này?

    Thông tin bổ sung về dữ liệu:
    - Tập dữ liệu đang phân tích gồm {len(df):,} TikToker có mức độ người theo dõi '{follower_level}'
    - Số người theo dõi trung bình của nhóm này: {df['stats.followerCount'].mean():,.0f} người

    Hãy phân tích các điểm sau:
    1. Hệ số tương quan này thể hiện mối quan hệ như thế nào giữa số lượng video và {metric_name.lower()}?
    2. Đường xu hướng (trend line) màu đỏ trên biểu đồ thể hiện xu hướng gì?
    3. Những TikToker có ít video nhưng {metric_name.lower()} cao (góc trên bên trái của biểu đồ) có đặc điểm gì đáng chú ý?
    4. Chiến lược nào phù hợp với nhóm người dùng này dựa trên phân tích?

    Vui lòng cung cấp phân tích ngắn gọn, súc tích, khoảng 100-150 từ.
    """


# Generate and display AI insights for each chart
with row1_col1:
    view_prompt = create_single_chart_prompt(
        chart_type="lượt xem",
        metric_name="Số lượt xem trên mỗi video",
        corr=corr1,
        df=filtered_df
    )
    display_AI_generated_insights(
        prompt=view_prompt,
        api_key="AIzaSyAdbNfxlQQQjKSgAcOjQt-XUwil-FMl6V8",
        print_to_console=False, expanded=False
    )

with row1_col2:
    like_prompt = create_single_chart_prompt(
        chart_type="lượt thích",
        metric_name="Số lượt thích trên mỗi video",
        corr=corr2,
        df=filtered_df
    )
    display_AI_generated_insights(
        prompt=like_prompt,
        api_key="AIzaSyCSGNpc1IlacTUwN31TKWms0RzF_we17vk",
        print_to_console=False, expanded=False
    )

with row2_col1:
    comment_prompt = create_single_chart_prompt(
        chart_type="lượt bình luận",
        metric_name="Số lượt bình luận trên mỗi video",
        corr=corr3,
        df=filtered_df
    )
    display_AI_generated_insights(
        prompt=comment_prompt,
        api_key="AIzaSyAHiAgc7tIuq4YKtswB-AaHa0W9eqQ5jGw",
        print_to_console=False, expanded=False
    )

with row2_col2:
    share_prompt = create_single_chart_prompt(
        chart_type="lượt chia sẻ",
        metric_name="Số lượt chia sẻ trên mỗi video",
        corr=corr4,
        df=filtered_df
    )
    display_AI_generated_insights(
        prompt=share_prompt,
        api_key="AIzaSyCnUToo7FRJn8v3BwMOt3FWwrDDFf2b4UI",
        print_to_console=False, expanded=False
    )


# ================================================================
# *__________ [Comparative Analysis by Follower Level] __________*
# ================================================================
st.divider()
# Research question
st.header(":blue-background[:blue[Câu hỏi:]] Có sự khác biệt có ý nghĩa thống kê về :blue[tần suất đăng tải video mỗi tuần], :blue[số lượng hashtag trung bình trên mỗi video] và :blue[thời lượng video trung bình] giữa các nhóm người dùng có số người theo dõi thấp, trung bình và cao không?")
# Answer
with st.expander(label=":green[**:material/check_box: Trả lời**]", expanded=False):
    st.markdown(f"""
    **Kết quả phân tích chính:**

    1.  **Về Số video đăng tải mỗi tuần:**

        - **Kết quả chính:** Phân tích cho thấy **không có sự khác biệt có ý nghĩa thống kê** về số lượng video đăng tải mỗi tuần giữa ba nhóm người dùng dựa trên số lượng người theo dõi (p-value = 0.0856 > 0.05).
        - **Nhận xét xu hướng:** Mặc dù giá trị trung bình có tăng nhẹ từ nhóm Thấp (4.41 video/tuần) lên nhóm Cao (4.66 video/tuần), sự khác biệt này không đủ lớn và đáng tin cậy để kết luận rằng số người theo dõi hiện tại là yếu tố quyết định chính đến tần suất đăng video.
        - **Ý nghĩa:** Kết quả này gợi ý rằng các nhà sáng tạo nội dung không nhất thiết phải tập trung vào việc tăng số lượng người theo dõi hiện tại để cải thiện tần suất đăng bài. Các yếu tố khác có thể đóng vai trò quan trọng hơn trong việc định hình thói quen đăng tải.

    2.  **Về Số lượng hashtag trên mỗi video:**

        - **Kết quả chính:** Phân tích chỉ ra **có sự khác biệt có ý nghĩa thống kê** về số lượng hashtag trung bình trên mỗi video giữa các nhóm người dùng (p-value = 0.0000 < 0.05).
        - **Nhận xét xu hướng:** Nhóm người dùng có số lượng người theo dõi **Thấp** sử dụng trung bình số hashtag **cao nhất** (7.46 hashtag/video), trong khi nhóm **Cao** sử dụng số hashtag **thấp nhất** (5.73 hashtag/video).
        - **Ý nghĩa:** Xu hướng này có thể phản ánh chiến lược của người dùng. Những người có ít người theo dõi có xu hướng sử dụng nhiều hashtag hơn nhằm tăng khả năng khám phá video của họ bởi đối tượng khán giả mới. Ngược lại, những người đã có lượng người theo dõi lớn có thể ít phụ thuộc vào hashtag hơn.

    3.  **Về Thời lượng video:**
        - **Kết quả chính:** Phân tích xác nhận **có sự khác biệt có ý nghĩa thống kê** về thời lượng video trung bình giữa ba nhóm người dùng theo số lượng người theo dõi (p-value = 0.0000 < 0.05).
        - **Nhận xét xu hướng:** Thời lượng video trung bình có xu hướng **tăng lên đáng kể** khi số lượng người theo dõi tăng. Nhóm Thấp có thời lượng trung bình ngắn nhất (59.01 giây), nhóm Trung bình dài hơn (74.48 giây), và nhóm Cao có thời lượng trung bình dài nhất (103.56 giây).
        - **Ý nghĩa:** Kết quả này ủng hộ quan sát rằng những người sáng tạo có lượng người theo dõi lớn hơn có xu hướng tạo ra các video có thời lượng dài hơn. Điều này có thể liên quan đến việc đầu tư nhiều hơn vào nội dung, khả năng giữ chân khán giả lâu hơn, hoặc xây dựng uy tín thông qua nội dung chuyên sâu hơn.

    **Tóm tắt và Hàm ý:**

    Kết quả phân tích cho thấy trong ba đặc điểm được khảo sát, **số lượng hashtag sử dụng** và **thời lượng video** có mối liên hệ có ý nghĩa thống kê với số lượng người theo dõi. Cụ thể, người dùng có ít người theo dõi có xu hướng dùng nhiều hashtag hơn và tạo video ngắn hơn, trong khi người dùng có nhiều người theo dõi lại dùng ít hashtag hơn và tạo video dài hơn. Ngược lại, **tần suất đăng tải video mỗi tuần** lại không cho thấy sự khác biệt đáng kể giữa các nhóm.

    Đối với các nhà sáng tạo nội dung, những phát hiện này gợi ý rằng:

    - Việc tăng tần suất đăng video có thể không trực tiếp phụ thuộc vào việc tăng số người theo dõi hiện có.
    - Hashtag có thể là công cụ quan trọng hơn cho những người dùng mới hoặc có ít người theo dõi để tăng khả năng hiển thị.
    - Thời lượng video có thể là một đặc điểm phát triển theo quá trình xây dựng lượng khán giả, khi người sáng tạo có thể đủ khả năng và lý do để tạo ra nội dung dài hơn và giữ chân người xem hiệu quả hơn.
                """)

st.header("Phân tích chỉ số theo mức độ người theo dõi")


def categorize_by_followers(df: pd.DataFrame) -> pd.DataFrame:
    """ Define follower levels based on follower count """

    # Calculate follower percentiles
    low_threshold = df['stats.followerCount'].quantile(0.33)
    high_threshold = df['stats.followerCount'].quantile(0.66)

    # Create a new column for follower level
    df_with_levels = df.copy()
    df_with_levels['follower_level'] = 'Trung bình'
    df_with_levels.loc[df_with_levels['stats.followerCount']
                       <= low_threshold, 'follower_level'] = 'Thấp'
    df_with_levels.loc[df_with_levels['stats.followerCount']
                       > high_threshold, 'follower_level'] = 'Cao'

    return df_with_levels


# Add follower levels to the dataframe
user_df_with_levels = categorize_by_followers(cleaned_user_info_df)

# Create filter for metric selection
metric_options = {
    "Số video mỗi tuần": "avg_videos_per_week",
    "Số hashtag trên mỗi video": "avg_hashtags_per_video",
    "Thời lượng video (giây)": "avg_video_duration"
}

selected_metric_name = st.selectbox(
    "Chọn chỉ số để phân tích:",
    options=list(metric_options.keys())
)

selected_metric_col = metric_options[selected_metric_name]

# Create groups for the analysis
low_followers = user_df_with_levels[user_df_with_levels['follower_level'] == 'Thấp']
medium_followers = user_df_with_levels[user_df_with_levels['follower_level'] == 'Trung bình']
high_followers = user_df_with_levels[user_df_with_levels['follower_level'] == 'Cao']

# Create a boxplot to visualize the distribution of the selected metric by follower level
fig_box = go.Figure()

for level, color in zip(['Thấp', 'Trung bình', 'Cao'], ['#FF9999', '#66B2FF', '#99CC99']):
    group_data = user_df_with_levels[user_df_with_levels['follower_level']
                                     == level][selected_metric_col]
    fig_box.add_trace(go.Box(
        y=group_data,
        name=f'{level}',
        boxpoints='all',
        jitter=0.3,
        pointpos=-1.8,
        marker_color=color,
        marker=dict(size=3),
        boxmean=True,
    ))

fig_box.update_layout(
    title=f'Phân phối {selected_metric_name}<br />theo mức độ người theo dõi',
    xaxis_title='Mức độ người theo dõi',
    yaxis_title=selected_metric_name,
    plot_bgcolor='#fafafa',
    boxmode="overlay",
    showlegend=False,

    height=450,
    title_y=0.95,
    title_yanchor="top",
    title_font_size=20,
    title_font_color=DARK_GRAY,
    title_font_family="Arial",
)

# Create a bar chart to compare means
metric_means = user_df_with_levels.groupby(
    'follower_level')[selected_metric_col].mean().reset_index()
metric_std = user_df_with_levels.groupby(
    'follower_level')[selected_metric_col].std().reset_index()

fig_bar = px.bar(
    metric_means,
    x='follower_level',
    y=selected_metric_col,
    color='follower_level',
    color_discrete_map={'Thấp': '#FF9999',
                        'Trung bình': '#66B2FF', 'Cao': '#99CC99'},
    labels={'follower_level': 'Mức độ người theo dõi',
            selected_metric_col: selected_metric_name},
    title=f'{selected_metric_name} trung bình<br />theo mức độ người theo dõi',
    # Sort x-axis of barchart by "Thấp", "Trung bình", "Cao"
    category_orders={
        'follower_level': ['Thấp', 'Trung bình', 'Cao']
    },
)

# Annotation for the mean value of each bar
for i, row in metric_means.iterrows():
    fig_bar.add_annotation(
        x=row['follower_level'],
        y=row[selected_metric_col],
        text=f" {row[selected_metric_col]:.2f} ",
        showarrow=False,
        font=dict(size=12, color=DARK_GRAY),
        bgcolor='white',
        bordercolor=DARK_GRAY,
        borderwidth=1,
    )

# Add error bars
fig_bar.update_traces(
    error_y=dict(
        type='data',
        array=metric_std[selected_metric_col],
        visible=True
    ),
    textposition='none',
)

fig_bar.update_layout(
    xaxis_title='Mức độ người theo dõi',
    yaxis_title=selected_metric_name,
    plot_bgcolor='#fafafa',
    showlegend=False,

    height=450,
    title_y=0.95,
    title_yanchor="top",
    title_font_size=20,
    title_font_color=DARK_GRAY,
    title_font_family="Arial",
)

# Display visualizations
col1, col2 = st.columns(spec=2, gap="small", border=True)
with col1:
    st.plotly_chart(fig_box, use_container_width=True)
with col2:
    st.plotly_chart(fig_bar, use_container_width=True)

# Display statistical test results
st.subheader("Kết quả kiểm định thống kê")

# Count samples in each group
group_counts = user_df_with_levels.groupby(
    'follower_level')[selected_metric_col].count().reset_index()
group_counts.columns = ['Mức độ người theo dõi', 'Số lượng mẫu']

# Create table of descriptive statistics
desc_stats = user_df_with_levels.groupby('follower_level')[selected_metric_col].agg([
    'mean', 'std', 'min', 'max']).reset_index()
desc_stats.columns = ['Mức độ người theo dõi',
                      'Trung bình', 'Độ lệch chuẩn', 'Tối thiểu', 'Tối đa']

# Format the numeric columns to 2 decimal places
for col in ['Trung bình', 'Độ lệch chuẩn', 'Tối thiểu', 'Tối đa']:
    desc_stats[col] = desc_stats[col].round(2)

# Merge the two tables
desc_stats = pd.merge(
    left=group_counts, right=desc_stats, on='Mức độ người theo dõi', how='left'
)

# Reorder the DataFrame from "Thấp" - "Trung bình" - "Cao"
desc_stats = pd.concat(
    [desc_stats[desc_stats['Mức độ người theo dõi'] == 'Thấp'],
     desc_stats[desc_stats['Mức độ người theo dõi'] == 'Trung bình'],
     desc_stats[desc_stats['Mức độ người theo dõi'] == 'Cao']],
    ignore_index=True
)

# Display final tables
st.dataframe(desc_stats, hide_index=True)

# Perform statistical test (Kruskal-Wallis)
try:
    # Extract data for each group, dropping NaN values
    group1 = low_followers[selected_metric_col].dropna()
    group2 = medium_followers[selected_metric_col].dropna()
    group3 = high_followers[selected_metric_col].dropna()

    # Perform Kruskal-Wallis test (non-parametric alternative to ANOVA)
    stat, p_value = stats.kruskal(group1, group2, group3)

    # Display test results
    st.metric(
        label="Kiểm định Kruskal-Wallis",
        value=f"p-value = {p_value:.4f}",
        delta="Có sự khác biệt ý nghĩa" if p_value < 0.05 else "Không có sự khác biệt ý nghĩa"
    )

    # Display explanation based on p-value
    if p_value < 0.05:
        st.success(f"""
        **Kết luận:** Có sự khác biệt có ý nghĩa thống kê về {selected_metric_name} 
        giữa các nhóm người dùng có số lượng người theo dõi khác nhau (p = {p_value:.4f} < 0.05).
        """)

        # Report which group has highest/lowest mean
        highest_group = metric_means.loc[metric_means[selected_metric_col].idxmax(
        )]
        lowest_group = metric_means.loc[metric_means[selected_metric_col].idxmin(
        )]

        st.markdown(f"""
        - Nhóm có {selected_metric_name} cao nhất: **{highest_group['follower_level']}** ({highest_group[selected_metric_col]:.2f})
        - Nhóm có {selected_metric_name} thấp nhất: **{lowest_group['follower_level']}** ({lowest_group[selected_metric_col]:.2f})
        """)
    else:
        st.info(f"""
        **Kết luận:** Không có sự khác biệt có ý nghĩa thống kê về {selected_metric_name} 
        giữa các nhóm người dùng có số lượng người theo dõi khác nhau (p = {p_value:.4f} > 0.05).
        """)

    # Generate insights prompt for AI
    analysis_prompt = f"""
    Hãy phân tích mối quan hệ giữa số lượng người theo dõi của người dùng TikTok và {selected_metric_name}.
    Kết quả kiểm định Kruskal-Wallis cho p-value = {p_value:.4f}.

    Các thống kê mô tả:
    - Nhóm người theo dõi Thấp: Trung bình {group1.mean():.2f} (độ lệch chuẩn {group1.std():.2f})
    - Nhóm người theo dõi Trung bình: Trung bình {group2.mean():.2f} (độ lệch chuẩn {group2.std():.2f})
    - Nhóm người theo dõi Cao: Trung bình {group3.mean():.2f} (độ lệch chuẩn {group3.std():.2f})

    Dựa trên kết quả trên, hãy cung cấp nhận xét về mối quan hệ giữa số lượng người theo dõi và {selected_metric_name}. Nhận xét nên bao gồm các điểm sau:
    1. Liệu có sự khác biệt có ý nghĩa thống kê giữa các nhóm không?
    2. Nếu có, nhóm nào có {selected_metric_name} cao nhất/thấp nhất?
    3. Ý nghĩa của kết quả này đối với các nhà sáng tạo nội dung trên TikTok?
    4. Có thể rút ra chiến lược gì từ phân tích này?

    Hãy đưa ra nhận xét ngắn gọn, dưới 400 từ.
    """

    # Display AI-generated insights
    display_AI_generated_insights(
        prompt=analysis_prompt,
        api_key="AIzaSyCnUToo7FRJn8v3BwMOt3FWwrDDFf2b4UI"
    )

except Exception as e:
    st.error(f"Lỗi khi thực hiện kiểm định thống kê: {str(e)}")
    st.warning(
        "Không thể thực hiện kiểm định thống kê do dữ liệu không đủ hoặc không phù hợp.")
