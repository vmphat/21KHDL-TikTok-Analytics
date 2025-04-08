import streamlit as st

# Set page configuration
st.set_page_config(
    page_title="Phân Tích Xu Hướng Ẩm Thực TikTok",
    page_icon="🍜",
    initial_sidebar_state="expanded",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .title {font-size: 2.5rem; font-weight: 700; color: #1E3A8A; text-align: center; margin-bottom: 1.5rem;}
    .subtitle {font-size: 1.5rem; font-weight: 500; color: #4B5563; text-align: center; margin-bottom: 2rem;}
    .card {background-color: #F3F4F6; border-radius: 8px; padding: 1.2rem; margin-bottom: 1rem; border-left: 4px solid #2563EB;}
    .card-title {font-size: 1.2rem; font-weight: 600; color: #1E40AF;}
</style>
""", unsafe_allow_html=True)

# Main header
st.markdown("<h1 class='title'>Phân Tích Xu Hướng Ẩm Thực Việt Nam Trên TikTok</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Khám phá các món ăn Việt Nam được yêu thích qua dữ liệu TikTok</p>", unsafe_allow_html=True)

# Introduction
st.markdown("""
Ứng dụng này giúp bạn khám phá xu hướng ẩm thực Việt Nam được đề cập trên TikTok, phân tích:

- **Danh mục món ăn** phổ biến và phân loại 
- **Phân bố địa lý** của các món ăn trên toàn quốc
- **Xu hướng theo tuần** - các món ăn đang được quan tâm 
""")

# Feature cards in 3 columns
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="card">
        <div class="card-title">📊 Phân Tích Món Ăn</div>
        <p>Xem chi tiết các món ăn được đề cập nhiều nhất và phân loại theo danh mục.</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="card">
        <div class="card-title">🗺️ Phân Bố Địa Lý</div>
        <p>Khám phá các món ăn phổ biến theo thành phố và quận/huyện trên toàn Việt Nam.</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="card">
        <div class="card-title">📈 Xu Hướng Theo Tuần</div>
        <p>Xem những món ăn mới nổi và đang trở thành xu hướng qua từng tuần.</p>
    </div>
    """, unsafe_allow_html=True)

# Call-to-action
st.markdown("### 🚀 Bắt đầu khám phá")
st.markdown("Chọn một chức năng từ menu để bắt đầu phân tích dữ liệu!")
