import streamlit as st
import plotly.express as px
import pandas as pd
from user_analysis.utils.footer import display_footer


# Hằng số
DATA_PATH = "data/interim/cleaned_user_info.csv"
CHART_OPTIONS = {
    "Nhiều lượt thích nhất": ("stats.heart", "reds", "Tổng số lượt thích (Trái tim)"),
    "Nhiều video nhất": ("stats.videoCount", "greens", "Tổng số video"),
    "Nhiều người theo dõi nhất": ("stats.followerCount", "blues", "Tổng số người theo dõi"),
    "Tỷ lệ tương tác": ("engagement_rate", "purples", "Tỷ lệ tương tác")
}


# Tải dữ liệu
@st.cache_data
def load_data():
    """Tải và lưu trữ dữ liệu người dùng đã được làm sạch từ tệp CSV"""
    return pd.read_csv(DATA_PATH)


# Hàm trực quan hóa
def create_bar_chart(data, metric, title, color_scale, y_label):
    """Tạo biểu đồ cột cho người dùng hàng đầu"""
    fig = px.bar(
        data,
        x='user.uniqueId',
        y=metric,
        color=metric,
        color_continuous_scale=color_scale,
        text=data[metric].apply(
            lambda x: f'{x:,.1f}' if metric == 'engagement_rate' else f'{x:,}'),
        height=500
    )
    fig.update_traces(textposition='outside', textfont_size=12)
    fig.update_layout(
        xaxis_title="ID Người dùng",
        yaxis_title=y_label,
        template="plotly_white",
        xaxis_tickangle=-45,
        showlegend=False,
        margin=dict(t=50, b=50),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)"
    )
    return fig


def create_pie_chart(data, metric, chart_option):
    """Tạo biểu đồ tròn cho người dùng hàng đầu"""
    fig = px.pie(
        data,
        names='user.uniqueId',
        values=metric,
        color_discrete_sequence=px.colors.sequential.RdBu,
        height=500
    )
    fig.update_traces(textinfo='percent+label', pull=[0.1] + [0]*(len(data)-1))
    fig.update_layout(
        template="plotly_white",
        margin=dict(t=50, b=50),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)"
    )
    return fig


def top_users(df):
    """Phân tích và trực quan hóa người dùng hoạt động hàng đầu"""
    # Tiêu đề trang
    st.markdown(
        '<div class="main-title" style="font-size: 28px; font-weight: bold; color: #1E90FF;">🏆 Phân tích người dùng hàng đầu</div>',
        unsafe_allow_html=True
    )
    st.markdown(
        '<p style="color: #666;">Khám phá những người dùng hoạt động hàng đầu dựa trên các chỉ số tương tác như lượt thích và số lượng video.</p>',
        unsafe_allow_html=True
    )

    # Giao diện người dùng
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        top_n = st.slider("Chọn số lượng N người dùng hàng đầu", 1, 50, 10, 1)
    with col2:
        chart_option = st.selectbox(
            "Chọn loại biểu đồ", list(CHART_OPTIONS.keys()))
    with col3:
        sort_order = st.radio(
            "Thứ tự sắp xếp", ["Giảm dần", "Tăng dần"], index=0)

    # Xử lý dữ liệu
    if chart_option == "Tỷ lệ tương tác":
        df['engagement_rate'] = df['stats.heart'] / \
            df['stats.videoCount'].replace(0, 1)

    metric, color_scale, y_label = CHART_OPTIONS[chart_option]
    title = f"Top {top_n} người dùng với {chart_option}"
    top_data = (df.nlargest(top_n, metric) if sort_order == "Giảm dần"
                else df.nsmallest(top_n, metric))[['user.uniqueId', metric]]

    # Trực quan hóa
    tab_bar, tab_pie = st.tabs(["Biểu đồ cột", "Biểu đồ tròn"])
    with st.spinner(f"Đang tạo hình ảnh cho Top {top_n} người dùng..."):
        with tab_bar:
            st.markdown(
                f'<div class="subheader" style="color: #333; font-weight: bold;">{title}</div>',
                unsafe_allow_html=True
            )
            bar_fig = create_bar_chart(
                top_data, metric, title, color_scale, y_label)
            st.plotly_chart(bar_fig, use_container_width=True)

        with tab_pie:
            st.markdown(
                f'<div class="subheader" style="color: #333; font-weight: bold;">Phân phối của {chart_option}</div>',
                unsafe_allow_html=True
            )
            pie_fig = create_pie_chart(top_data, metric, chart_option)
            st.plotly_chart(pie_fig, use_container_width=True)

    # Dữ liệu chi tiết
    with st.expander("Xem dữ liệu chi tiết", expanded=False):
        st.dataframe(
            top_data.style.format(
                {metric: "{:,.2f}" if metric == 'engagement_rate' else "{:,}"}),
            use_container_width=True
        )

    # Tùy chọn tải xuống
    csv = top_data.to_csv(index=False)
    st.download_button(
        label="📥 Tải dữ liệu dưới dạng CSV",
        data=csv,
        file_name=f"top_{top_n}_{chart_option.lower().replace(' ', '_')}_{sort_order.lower()}.csv",
        mime="text/csv"
    )


"""Hàm ứng dụng chính"""
df = load_data()
st.session_state['cleaned_user_info_df'] = df
if not df.empty:
    top_users(df)
    display_footer()
else:
    st.warning(
        "Vui lòng tải lên hoặc cung cấp dữ liệu người dùng hợp lệ để phân tích.")
