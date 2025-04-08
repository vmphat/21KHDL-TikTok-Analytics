import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
# from data_preprocessing import video_info_df as df
from google import genai


# ================================================================
# *_____________________ [Define constants] _____________________*
# ================================================================
# Constants
METRIC_LABELS = {
    "Lượt xem": "statsV2.playCount",
    "Lượt thích": "statsV2.diggCount",
    "Lượt bình luận": "statsV2.commentCount",
    "Lượt chia sẻ": "statsV2.shareCount"
}

METRIC_COLORS = {
    "statsV2.playCount": "viridis",
    "statsV2.diggCount": "blues",
    "statsV2.commentCount": "greens",
    "statsV2.shareCount": "reds"
}


# ================================================================
# *____________________ [Utility functions] _____________________*
# ================================================================
# Initialize Gemini client (same as in video_performance.py)
@st.cache_resource
def get_genai_client() -> genai.Client:
    """Initialize and cache the Gemini client"""
    try:
        # Use secrets in production
        return genai.Client(api_key="AIzaSyAY8nfoP7DXfL571ovT8V_HlMWCTdHqdgc")
    except Exception as e:
        st.error(f"Failed to initialize Gemini client: {e}")
        return None


@st.cache_data(show_spinner=False)
def generate_report(data_str: str, model_name: str = "gemini-2.0-flash-lite") -> str:
    """
    Generate an analytical report using Gemini API.

    Args:
        data_str: Data to analyze in string format
        model_name: Gemini model to use

    Returns:
        Generated report in Markdown format
    """
    try:
        prompt = f"""
        Bạn là một nhà phân tích dữ liệu chuyên nghiệp. Hãy viết một vài dòng về phân tích dữ liệu TikTok từ kết quả thống kê như sau:
        {data_str}
        
        Yêu cầu:
        - Viết bằng tiếng Việt, ngôn ngữ đơn giản, dễ hiểu
        - Giọng văn hấp dẫn, thú vị
        - Định dạng Markdown với tiêu đề rõ ràng
        - Bắt đầu bằng 1-2 câu tóm tắt về dữ liệu
        - Tiếp theo, bao gồm ít nhất 3 insight quan trọng, mỗi insight chứa trong 1 câu
        - Tập trung vào phân tích hashtag và mối quan hệ với tương tác
        """

        client = get_genai_client()
        if not client:
            return "Không thể kết nối với dịch vụ phân tích."

        response = client.models.generate_content(
            model=model_name,
            contents=[prompt]
        )
        return response.text if hasattr(response, "text") else "Không nhận được phản hồi từ hệ thống."
    except Exception as e:
        st.error(f"Lỗi khi tạo báo cáo: {e}")
        return ""


def analyze_hashtag_engagement(df: pd.DataFrame, top_n: int = 5, metric_col: str = "statsV2.playCount"):
    """Phân tích hashtag hàng đầu theo chỉ số tương tác"""
    hashtag_counts = df.explode("hashtags")
    hashtag_counts = hashtag_counts[hashtag_counts["hashtags"].notna() & (
        hashtag_counts["hashtags"] != "")]

    result = hashtag_counts.groupby("hashtags").agg(
        total_engagement=(metric_col, "sum"),
        video_count=("video.id", "count"),
        avg_engagement=(metric_col, "mean")
    ).reset_index()

    result['engagement_per_video'] = result['total_engagement'] / \
        result['video_count']

    return result.nlargest(top_n, 'total_engagement')


def analyze_hashtag_count_effect(df: pd.DataFrame, metric_col: str = "statsV2.playCount"):
    """Phân tích mối quan hệ giữa số lượng hashtag và tương tác"""
    return df.groupby("hashtag_count").agg(
        avg_engagement=(metric_col, "mean"),
        video_count=("video.id", "count"),
        median_engagement=(metric_col, "median")
    ).reset_index()


def plot_hashtag_count_vs_engagement(df: pd.DataFrame, metric_col: str = "statsV2.playCount"):
    """Vẽ biểu đồ số lượng hashtag vs tương tác"""
    metric_name = next(k for k, v in METRIC_LABELS.items() if v == metric_col)

    fig = px.scatter(
        df,
        x="hashtag_count",
        y="avg_engagement",
        size="video_count",
        title=f"Số lượng Hashtag vs. Tương tác trung bình ({metric_name})",
        labels={
            "hashtag_count": "Số lượng Hashtag",
            "avg_engagement": f"{metric_name} trung bình",
            "video_count": "Số lượng video"
        },
        color="avg_engagement",
        color_continuous_scale=METRIC_COLORS.get(metric_col, "viridis"),
        trendline="lowess",
        trendline_options=dict(frac=0.3)
    )

    fig.update_traces(
        marker=dict(opacity=0.7, line=dict(width=1, color='DarkSlateGrey')),
        selector=dict(mode='markers')
    )

    return fig


def plot_top_hashtags(top_hashtags, metric_col="statsV2.playCount"):
    """Vẽ biểu đồ hiệu quả hashtag hàng đầu dưới dạng biểu đồ nhóm"""
    metric_name = next(k for k, v in METRIC_LABELS.items() if v == metric_col)

    # Create figure with secondary y-axis
    fig = go.Figure()

    # Add bars for total engagement (primary y-axis)
    fig.add_trace(
        go.Bar(
            x=top_hashtags["hashtags"],
            y=top_hashtags["total_engagement"],
            name=f"Tổng {metric_name}",
            marker_color='#636EFA',  # Blue
            opacity=0.7,
            yaxis="y"
        )
    )

    # Add bars for engagement per video (secondary y-axis)
    fig.add_trace(
        go.Bar(
            x=top_hashtags["hashtags"],
            y=top_hashtags["engagement_per_video"],
            name=f"{metric_name} mỗi video",
            marker_color='#EF553B',  # Red
            opacity=0.7,
            yaxis="y2"
        )
    )

    # Add line for video count (secondary y-axis)
    fig.add_trace(
        go.Scatter(
            x=top_hashtags["hashtags"],
            y=top_hashtags["video_count"],
            name="Số video",
            mode='lines+markers',
            line=dict(color='#00CC96', width=3),
            marker=dict(size=10),
            yaxis="y2"
        )
    )

    # Update layout for dual y-axes
    fig.update_layout(
        title=f"Hiệu Quả Hashtag Hàng Đầu - {metric_name}",
        xaxis=dict(
            title="Hashtag",
            tickangle=45
        ),
        yaxis=dict(
            title=f"Tổng {metric_name}",
            title_font=dict(color='#636EFA')
        ),
        yaxis2=dict(
            title=f"{metric_name} mỗi video & Số video",
            title_font=dict(color='#EF553B'),
            overlaying='y',
            side='right',
            showgrid=False
        ),
        barmode='group',
        bargap=0.15,
        bargroupgap=0.1,
        height=500,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )

    return fig


def plot_hashtag_trends(df: pd.DateOffset, time_agg: str = "Theo tháng",
                        top_n: int = 5, metric_col: str = "statsV2.playCount"):
    """Vẽ biểu đồ xu hướng hashtag theo thời gian"""
    metric_name = next(k for k, v in METRIC_LABELS.items() if v == metric_col)

    if time_agg == "Theo ngày":
        df["time_group"] = df["createTime"].dt.strftime("%Y-%m-%d")
    elif time_agg == "Theo tuần":
        df["time_group"] = df["createTime"].dt.to_period("W").dt.to_timestamp()
    else:  # Theo tháng
        df["time_group"] = df["createTime"].dt.to_period("M").dt.to_timestamp()

    top_hashtags = analyze_hashtag_engagement(df, top_n, metric_col)[
        "hashtags"].tolist()

    exploded = df.explode("hashtags")
    filtered = exploded[exploded["hashtags"].isin(top_hashtags)]

    grouped = filtered.groupby(["time_group", "hashtags"])[
        metric_col].sum().reset_index()

    fig = px.line(
        grouped,
        x="time_group",
        y=metric_col,
        color="hashtags",
        title=f"Top {top_n} Hashtag Theo Thời Gian ({time_agg})",
        labels={
            "time_group": "Ngày",
            metric_col: metric_name,
            "hashtags": "Hashtag"
        },
        line_shape="spline",
        render_mode="svg"
    )

    fig.update_layout(
        hovermode="x unified",
        xaxis=dict(
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label="1 tháng",
                         step="month", stepmode="backward"),
                    dict(count=6, label="6 tháng",
                         step="month", stepmode="backward"),
                    dict(count=1, label="YTD", step="year", stepmode="todate"),
                    dict(count=1, label="1 năm",
                         step="year", stepmode="backward"),
                    dict(step="all")
                ])
            ),
            rangeslider=dict(visible=True),
            type="date"
        )
    )

    return fig


def display_hashtag_insights(df: pd.DataFrame):
    """Hiển thị bảng điều khiển phân tích hashtag"""
    st.title("🔍 Bảng Phân Tích Hashtag Nâng Cao")

    # Add metric selection
    selected_metric = st.sidebar.selectbox(
        "Chọn chỉ số phân tích",
        list(METRIC_LABELS.keys()),
        index=0
    )
    metric_col = METRIC_LABELS[selected_metric]

    with st.sidebar:
        st.header("⚙️ Cài Đặt Phân Tích")
        top_n = st.slider("Số lượng Hashtag hàng đầu", 3, 15, 5)
        time_agg = st.selectbox("Nhóm theo thời gian", [
                                "Theo ngày", "Theo tuần", "Theo tháng"], index=2)

        # Add report generation button
        if st.button("📊 Tạo báo cáo tổng thể"):
            with st.spinner("Đang phân tích dữ liệu..."):
                report_data = df.describe().to_string()
                report = generate_report(report_data)
                st.session_state.full_report = report

        st.markdown("---")
        st.info(f"Đang phân tích: **{selected_metric}**")

    # Display full report if generated
    if "full_report" in st.session_state:
        with st.expander("📝 Báo cáo tổng thể", expanded=True):
            st.markdown(st.session_state.full_report)

    # Top Hashtags Section
    st.header(f"🏆 Hashtag Hiệu Quả Nhất theo {selected_metric}")
    top_hashtags = analyze_hashtag_engagement(df, top_n, metric_col)
    st.plotly_chart(plot_top_hashtags(
        top_hashtags, metric_col), use_container_width=True)

    with st.expander("Xem Dữ Liệu Chi Tiết"):
        display_df = top_hashtags.copy()
        display_df.columns = ["Hashtag", "Tổng tương tác",
                              "Số video", "Tương tác trung bình", "Tương tác/video"]
        st.dataframe(
            display_df.style.format({
                "Tổng tương tác": "{:,.0f}",
                "Tương tác trung bình": "{:,.0f}",
                "Tương tác/video": "{:,.0f}"
            }),
            use_container_width=True
        )

    # Hashtag Count Analysis
    st.header("🔢 Số lượng Hashtag Tối Ưu")
    col1, col2 = st.columns([2, 1])

    with col1:
        hashtag_count_df = analyze_hashtag_count_effect(df, metric_col)
        st.plotly_chart(
            plot_hashtag_count_vs_engagement(hashtag_count_df, metric_col),
            use_container_width=True
        )

    with col2:
        # * Dùng AI để phân tích mối quan hệ giữa số lượng hashtag và tương tác
        with st.expander(
                label=":blue-background[:blue[**:material/auto_awesome: Nhận xét từ AI**]]",
                expanded=True):
            st.markdown("### Nhận Xét")
            with st.spinner("Đang phân tích..."):
                # Get data for the chart
                analysis_data = hashtag_count_df[[
                    'hashtag_count', 'avg_engagement', 'video_count']].to_string()

                # Generate insights specific to this chart
                chart_prompt = f"""
                Đây là dữ liệu phân tích mối quan hệ giữa số lượng hashtag và tương tác:
                {analysis_data}
                
                Hãy đưa ra 3-4 nhận xét ngắn gọn dưới 100 từ bằng tiếng Việt về:
                1. Số lượng hashtag tối ưu cho tương tác
                2. Xu hướng chung giữa số hashtag và tương tác
                3. Bất kỳ điểm bất thường nào đáng chú ý
                """

                insights = generate_report(chart_prompt)
                st.markdown(insights)

        # Add button to regenerate insights
        if st.button("🔄 Làm mới nhận xét", key="hashtag_count_insights"):
            st.rerun()

    # Hashtag Trends Over Time
    st.header("📈 Xu Hướng Hashtag Theo Thời Gian")
    st.plotly_chart(
        plot_hashtag_trends(df, time_agg, top_n, metric_col),
        use_container_width=True
    )

    # * Add AI insights for trends chart
    # with st.expander("📝 Nhận xét về xu hướng", expanded=False):
    with st.expander(
            label=":blue-background[:blue[**:material/auto_awesome: Nhận xét từ AI về xu hướng**]]",
            expanded=True):
        with st.spinner("Đang phân tích xu hướng..."):
            # Get top hashtags data for analysis
            trends_data = analyze_hashtag_engagement(
                df, top_n, metric_col).to_string()

            # Generate insights specific to trends
            trends_prompt = f"""
            Đây là dữ liệu về xu hướng hashtag theo thời gian:
            {trends_data}
            
            Hãy đưa ra 3-4 nhận xét dưới 100 từ bằng tiếng Việt về:
            1. Xu hướng phổ biến của các hashtag hàng đầu
            2. Hashtag nào đang tăng/giảm độ phổ biến
            3. Thời điểm có tương tác cao nhất
            4. Gợi ý về thời điểm đăng bài tốt nhất
            """

            trends_insights = generate_report(trends_prompt)
            st.markdown(trends_insights)


@st.cache_data
def load_data() -> pd.DataFrame:
    """Load data from session state"""
    return pd.read_parquet("data/processed/cleaned_video_info.parquet")


# ================================================================
# *_______________________ [Basic setup] ________________________*
# ================================================================
# Cấu hình Streamlit
st.set_page_config(
    page_title="Advanced Hashtag Analysis",
    page_icon="📊",
    layout="wide",
)


# ================================================================
# *________________________ [Read data] _________________________*
# ================================================================
# Get the cached data from session state
df = load_data()


# ================================================================
# *_______________ [Show dashboard and insights] ________________*
# ================================================================
display_hashtag_insights(df)
