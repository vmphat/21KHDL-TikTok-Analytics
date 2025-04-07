import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np
from google import genai
from user_analysis.utils.footer import display_footer
from user_analysis.utils.styles import apply_styles


@st.cache_data
def generate_report(data_str: str) -> str:
    """ Generate a report using Gemini API """

    # Generate content
    try:
        prompt = f"""
        Bạn là một nhà phân tích dữ liệu chuyên nghiệp. Hãy viết một báo cáo về phân tích dữ liệu TikTok từ kết quả thống kê như sau:
        {data_str}
        Hãy viết báo cáo này bằng tiếng Việt và sử dụng các từ ngữ đơn giản, dễ hiểu. Hãy làm cho nó thật hấp dẫn và thú vị.
        Hãy viết báo cáo này với định dạng Markdown, bao gồm các tiêu đề và danh sách nếu cần thiết.
        """
        client = genai.Client(
            api_key="AIzaSyAdbNfxlQQQjKSgAcOjQt-XUwil-FMl6V8")
        response = client.models.generate_content(
            model="gemini-2.0-flash-lite",
            contents=[
                prompt
            ])
        return response.text
    except Exception as e:
        st.error(f"Lỗi khi tạo nội dung: {e}")
        return ""


# Hằng số
COLORS_RGBA = [
    "rgba(99, 110, 250, 0.9)",  # Xanh dương
    "rgba(239, 85, 59, 0.8)",   # Đỏ
    "rgba(0, 204, 150, 0.7)"    # Xanh lá
]
METRICS = ['stats.followerCount', 'stats.heart', 'stats.videoCount']
METRIC_LABELS = ["Người theo dõi", "Lượt thích", "Video"]

# Tải dữ liệu


@st.cache_data
def load_data():
    """Tải và lưu trữ dữ liệu người dùng đã được làm sạch từ tệp CSV"""
    return pd.read_csv("data/interim/cleaned_user_info.csv")


# Hàm trực quan hóa
def create_scatter_matrix(df, template):
    """Tạo một biểu đồ ma trận phân tán chỉ hiển thị tam giác dưới bên trái"""
    fig = px.scatter_matrix(
        df,
        dimensions=METRICS,
        color_discrete_sequence=COLORS_RGBA,
        height=450,
        opacity=0.6,
        title="Ma trận phân tán"
    )
    fig.update_traces(diagonal_visible=False)
    # Chỉ hiển thị tam giác dưới bên trái
    for i, _ in enumerate(METRICS):
        for j, _ in enumerate(METRICS):
            if j >= i:  # Ẩn các ô ở tam giác trên và đường chéo chính
                fig.update_traces(visible=False, selector=dict(
                    subplot=f"x{j+1}y{i+1}"))
    fig.update_layout(template=template)
    return fig


def create_correlation_heatmap(df, template):
    """Tạo một biểu đồ nhiệt tương quan chỉ hiển thị tam giác dưới bên trái"""
    correlation_matrix = df[METRICS].corr()
    # Tạo mặt nạ cho tam giác trên
    mask = np.triu(np.ones_like(correlation_matrix, dtype=bool))
    masked_correlation = correlation_matrix.mask(mask)

    global masked_correlation_latex
    masked_correlation_latex = masked_correlation.to_latex()

    fig = px.imshow(
        masked_correlation,
        text_auto=".2f",
        aspect="equal",
        color_continuous_scale="Blues",
        labels=dict(x="Chỉ số", y="Chỉ số", color="Tương quan"),
        height=500
    )
    fig.update_layout(
        xaxis=dict(tickvals=[0, 1, 2], ticktext=METRIC_LABELS),
        yaxis=dict(tickvals=[0, 1, 2], ticktext=METRIC_LABELS),
        template=template
    )
    return fig


def create_histogram(df, metric, bins, log_scale, color, template):
    """Tạo một biểu đồ histogram dựa trên chỉ số đã chọn"""
    titles = {
        'stats.followerCount': "Phân phối người theo dõi",
        'stats.heart': "Phân phối lượt thích",
        'stats.videoCount': "Phân phối số lượng video"
    }
    fig = px.histogram(
        df,
        x=metric,
        nbins=bins,
        log_y=log_scale,
        color_discrete_sequence=[color],
        height=450,
        marginal="box",
        title=titles[metric]
    )
    fig.update_layout(template=template, bargap=0.1, showlegend=False)
    return fig


# Ứng dụng chính
# Áp dụng kiểu dáng và tải dữ liệu
apply_styles()
df = load_data()

# Cấu hình thanh bên
st.sidebar.title("⚙️ Cài đặt")
theme = "Sáng"
plotly_template = "plotly_white" if theme == "Tối" else "plotly_dark"

st.sidebar.markdown("### Tùy chọn trực quan hóa")
chart_option = st.sidebar.selectbox(
    "Chọn kiểu trực quan hóa",
    ["Phân phối người theo dõi", "Phân phối lượt thích",
        "Phân phối số lượng video"],
    help="Chọn một chỉ số để trực quan hóa phân phối của nó"
)
num_bins = st.sidebar.slider(
    "Số lượng ngăn", 10, 100, 50, 5,
    help="Điều chỉnh độ chi tiết của histogram"
)
log_scale = st.sidebar.checkbox(
    "Thang đo logarit", value=True,
    help="Bật để trực quan hóa dữ liệu lệch tốt hơn"
)

# Nội dung chính
st.title("📊 Phân tích tương quan TikTok")
st.markdown(
    "Khám phá mối quan hệ giữa người theo dõi, lượt thích và số lượng video với các hình ảnh trực quan tương tác.",
    help="Sử dụng thanh bên để tùy chỉnh phân tích của bạn"
)

# Thống kê tóm tắt
with st.container():
    st.subheader("Tổng quan dữ liệu")
    st.metric("Tổng số người dùng", f"{len(df):,}")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Trung bình người theo dõi",
                  f"{df['stats.followerCount'].mean():,.0f}")
    with col2:
        st.metric("Trung bình lượt thích",
                  f"{df['stats.heart'].mean():,.0f}")
    with col3:
        st.metric("Trung bình video",
                  f"{df['stats.videoCount'].mean():,.0f}")

# Trực quan hóa chính
col1, col2 = st.columns(2)
with col1:
    st.markdown("#### 🔍 Ma trận phân tán")
    scatter_fig = create_scatter_matrix(df, plotly_template)
    st.plotly_chart(scatter_fig, use_container_width=True)

with col2:
    st.markdown("#### 📊 Biểu đồ nhiệt tương quan")
    heatmap_fig = create_correlation_heatmap(df, plotly_template)
    st.plotly_chart(heatmap_fig, use_container_width=True)

# Histogram động
metric_map = {
    "Phân phối người theo dõi": ('stats.followerCount', 0),
    "Phân phối lượt thích": ('stats.heart', 1),
    "Phân phối số lượng video": ('stats.videoCount', 2)
}
metric, color_idx = metric_map[chart_option]

with st.spinner(f"Đang tạo {chart_option.lower()}... Vui lòng đợi."):
    hist_fig = create_histogram(
        df, metric, num_bins, log_scale, COLORS_RGBA[color_idx], plotly_template)
    st.plotly_chart(hist_fig, use_container_width=True)

# Nút tải xuống
data_to_download = df[METRICS]
st.download_button(
    label="📥 Tải dữ liệu",
    data=data_to_download.to_csv(index=False),
    file_name=f"{chart_option.lower().replace(' ', '_')}.csv",
    mime="text/csv",
    help="Tải dữ liệu được sử dụng trong biểu đồ này dưới dạng tệp CSV"
)

# Khai báo biến toàn cục
global distribution_dataframe_latex
distribution_dataframe_latex = df[METRICS].to_latex()

# st.markdown(f'''
# ## Dataframe tương quan sau khi đưa qua latex
# {masked_correlation_latex}
# '''
#             )
st.header("Báo cáo từ phân tích tương quan")
corr_report_data = generate_report(masked_correlation_latex)
st.markdown(corr_report_data)

# st.markdown(f'''
# ## Dataframe phân phối sau khi đưa qua latex
# {distribution_dataframe_latex}
# ''')
st.header("Báo cáo từ phân phối")
dist_report_data = generate_report(distribution_dataframe_latex)
st.markdown(dist_report_data)
