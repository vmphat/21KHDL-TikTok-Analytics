import streamlit as st
import plotly.express as px
import pandas as pd
from google import genai
from typing import List, Tuple


# ================================================================
# *_____________________ [Define constants] _____________________*
# ================================================================
DARK_GRAY: str = "#444444"
# CLEANED_USER_DATA_FILE: str = "data/interim/cleaned_user_info.csv"
CLEANED_USER_DATA_FILE: str = "data/processed/cleaned_user_info.parquet"


# ================================================================
# *____________________ [Utility functions] _____________________*
# ================================================================
# Hàm giúp tạo nhận xét và rút ra insights từ kết quả phân tích và trực quan hóa dữ liệu
@st.cache_data(show_spinner=False)
def generate_insights(prompt: str, api_key: str) -> str:
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
def display_AI_generated_insights(prompt: str, api_key: str) -> None:
    """ End-to-end module để rút trích insights từ biểu đồ và hiện thị lên trang web """

    with st.expander(
            label=":blue-background[:blue[**:material/auto_awesome: Nhận xét từ AI**]]",
            expanded=True):
        # Tạo nhận xét từ Gemini API
        with st.spinner(text="Đang tạo nhận xét từ AI...", show_time=True):
            insights = generate_insights(prompt=prompt, api_key=api_key)
            if not insights:
                st.error("Hiện tại hệ thống đang quá tải, vui lòng thử lại sau.")
            else:
                st.markdown(insights)


# Tải dữ liệu
@st.cache_data(persist="disk")
def load_user_data() -> pd.DataFrame:
    """ Tải và lưu trữ dữ liệu người dùng đã được làm sạch từ tệp """
    if CLEANED_USER_DATA_FILE.endswith(".csv"):
        return pd.read_csv(CLEANED_USER_DATA_FILE)
    elif CLEANED_USER_DATA_FILE.endswith(".parquet"):
        # Đọc tệp Parquet
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

    # Lọc theo mức tương tác
    if engagement_level == "Thấp":
        filtered_df = filtered_df[
            filtered_df['engagement_ratio'] <= low_engagement]
    elif engagement_level == "Trung bình":
        filtered_df = filtered_df[
            (filtered_df['engagement_ratio'] > low_engagement) &
            (filtered_df['engagement_ratio'] <= high_engagement)
        ]
    else:
        filtered_df = filtered_df[
            filtered_df['engagement_ratio'] > high_engagement]

    return filtered_df


# Hàm để vẽ biểu đồ scatter plot thể hiện mối quan hệ giữa người theo dõi và mức độ tương tác
@st.cache_data(show_spinner=False)
def plot_engagement_scatter(df: pd.DataFrame):
    """ Vẽ biểu đồ phân tán thể hiện mối quan hệ giữa người theo dõi và mức độ tương tác """

    # Tạo biểu đồ phân tán
    fig = px.scatter(
        df,
        x='stats.followerCount',
        y='stats.heartCount',
        size='stats.videoCount',
        color='engagement_ratio',
        color_continuous_scale='YlGnBu',
        hover_data=['user.uniqueId'],
        height=600,
        opacity=0.75,
    )

    # Cập nhật marker và màu sắc
    fig.update_traces(
        marker=dict(line=dict(width=1, color=DARK_GRAY)),
    )

    # Cập nhật bố cục biểu đồ
    fig.update_layout(
        xaxis_title="👥 Số lượng người theo dõi",
        yaxis_title="❤️ Tổng số lượt thích",
        xaxis_type="log",
        yaxis_type="log",
        showlegend=True,
        coloraxis_colorbar_title="Tỷ lệ tương tác 🔥",

        # Thay đổi màu nền và kích thước tiêu đề
        plot_bgcolor="#fafafa",
        title_x=0.5,
        title_y=0.95,
        title_xanchor="center",
        title_yanchor="top",
        title_font_size=26,
        title_font_color=DARK_GRAY,
        title_text="📊 Mối quan hệ giữa số người theo dõi và mức độ tương tác",

        # Thay đổi kích thước x, y-axis label
        xaxis_title_font=dict(size=16),
        yaxis_title_font=dict(size=16),

        # Thay đổi kích thước x, y-axis tick labels
        xaxis_tickfont=dict(size=14),
        yaxis_tickfont=dict(size=14),
    )

    # Add annotation for the user to know the size of the markers
    # are proportional to the number of videos
    fig.add_annotation(
        text=" Kích thước của các điểm thể hiện số lượng video của người dùng ",
        xref="paper",
        yref="paper",
        x=0.02,
        y=0.98,
        showarrow=False,
        font=dict(size=18, color="#2c7d33"),
        bgcolor='#e7f4ea',
        bordercolor='#39a342',
        borderwidth=1,
    )

    return fig


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
st.title("🏆 Phân tích mức độ tương tác của các TikToker")
st.write(
    "Phân tích mối quan hệ giữa **người theo dõi** và **mức độ tương tác (lượt thích/trái tim)**.")
st.divider()


# ================================================================
# *_______________ [Read data and set up styles] ________________*
# ================================================================
# Tải dữ liệu đã lưu trữ
cleaned_user_info_df = load_user_data()


# ================================================================
# *___________________ [Data transformation] ____________________*
# ================================================================
# Tính tỷ lệ tương tác
cleaned_user_info_df = calculate_engagement_ratio(
    cleaned_user_info_df)

# Xác định các phân vị để lọc
percentiles = [0, 0.33, 0.66, 1]
low_followers, high_followers, low_engagement, high_engagement = \
    calculate_percentiles(cleaned_user_info_df, percentiles)


# ================================================================
# *_________________ [UI for selecting filters] _________________*
# ================================================================
# Tạo 2 cột, cột bên trái để người dùng chọn các filter
# và cột bên phải để hiển thị biểu đồ
filter_col, chart_col = st.columns(spec=[0.2, 0.8], gap="large", border=False)


with filter_col:  # Cho người dùng chọn các bộ lọc
    with st.expander(label="Chọn bộ lọc", expanded=True):
        st.subheader(
            body="🔍 Chọn bộ lọc để phân tích",
            help="Chọn các bộ lọc để phân tích mức độ tương tác của người dùng TikTok.",
        )
        st.write(
            "Chọn các bộ lọc để phân tích mức độ tương tác của người dùng TikTok.")

        follower_level = st.selectbox(
            label="📌 :red[**Chọn mức người theo dõi:**]",
            options=["Thấp", "Trung bình", "Cao"]
        )
        engagement_level = st.selectbox(
            label="🔥 :orange[**Chọn mức tương tác:**]",
            options=["Thấp", "Trung bình", "Cao"]
        )

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

with chart_col:
    # Hiển thị tiêu đề cho biểu đồ
    st.subheader(
        body=f"Thông tin chi tiết về tương tác: Số người theo dõi {follower_level} & Mức độ tương tác {engagement_level}",
    )

    # Hiển thị số liệu thống kê
    col1, col2, col3 = st.columns(spec=3, gap="medium", border=False)
    # Số lượng người dùng, trung bình lượt thích và người theo dõi
    with col1:
        st.metric(label="📌 Số lượng người dùng",
                  value=f"{len(filtered_df):,}",
                  border=True,
                  )
    with col2:
        st.metric(label="❤️ Số lượt thích trung bình",
                  value=f"{filtered_df['stats.heart'].mean():,.0f}",
                  border=True,
                  )
    with col3:
        st.metric(label="👥 Số người theo dõi trung bình",
                  value=f"{filtered_df['stats.followerCount'].mean():,.0f}",
                  border=True,
                  )

    # Hiển thị trực quan với vòng quay chờ
    with st.spinner(text="Đang tải biểu đồ...", show_time=True):
        # Vẽ biểu đồ phân tán thể hiện mối quan hệ giữa người theo dõi và mức độ tương tác
        fig = plot_engagement_scatter(df=filtered_df)
        # Hiển thị biểu đồ
        st.plotly_chart(fig, use_container_width=True)

# Dùng AI để rút ra insights từ biểu đồ
correlation_analysis_prompt = f"""
Hãy giúp tôi viết 1 đoạn nhận xét về mức độ tương quan giữa 'Số lượng người theo dõi', 'Tổng số lượt thích', 'Tổng số video' và 'Tỷ lệ tương tác' của các TikToker thuộc vào nhóm người dùng có đồng thời 2 đặc điểm: số người theo dõi '{follower_level}' và mức độ tương tác '{engagement_level}'. Đoạn nhận xét này nên ngắn gọn, xúc tích, tập trung vào những điểm nổi bật từ phân phối quan sát được. Đoạn văn chỉ nên có khoảng 300 đến 500 từ.

Tôi sẽ cung cấp cho bạn 4 thông tin về dữ liệu mà tôi đã phân tích.
Đầu tiên là một biểu đồ phân tán thể hiện mối quan hệ giữa các chỉ số. Biểu đồ này cho thấy mối tương quan giữa 'Số lượng người theo dõi' (trên trục x) với 'Tổng số lượt thích' (trên trục y), kích thước của các điểm thể hiện 'Số lượng video' (kích thước càng lớn thì số lượng video càng nhiều) và màu sắc của các điểm thể hiện 'Tỷ lệ tương tác' (màu sắc càng đậm thì tỷ lệ tương tác càng cao). Biểu đồ này sẽ được đính kèm dưới dạng byte:
{fig.to_image()}

Thứ hai là thống kê về số lượng TikToker thuộc vào nhóm này. Số lượng TikToker này là {len(filtered_df):,} người dùng. 

Thứ ba là thông tin về số lượt thích trung bình của các TikToker trong nhóm này. Số lượt thích trung bình là {filtered_df['stats.heart'].mean():,.0f} lượt thích.

Thứ tư là thông tin về số người theo dõi trung bình của các TikToker trong nhóm này. Số người theo dõi trung bình là {filtered_df['stats.followerCount'].mean():,.0f} người theo dõi.

Đừng bắt đầu câu trả lời bằng các cụm từ như: "Dựa trên ..." mà hãy trực tiếp đi vào nội dung nhận xét.
"""
with chart_col:
    display_AI_generated_insights(
        prompt=correlation_analysis_prompt,
        api_key="AIzaSyCnUToo7FRJn8v3BwMOt3FWwrDDFf2b4UI")
