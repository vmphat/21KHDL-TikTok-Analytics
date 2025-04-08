import streamlit as st
from footer import display_footer
from data_load import load_data

# Set page configuration
st.set_page_config(
    layout="wide"
)

# Load data once when the app starts and cache it
df = load_data()

# Store the dataframe in session state so all pages can access it
if 'df' not in st.session_state:
    st.session_state.df = df

# Title of the main page
st.title("🎵 Bảng Điều Khiển Phân Tích TikTok")

# Introduction section
st.markdown("""
<div style="font-size: 18px; line-height: 1.6; color: #333;">
Chào mừng bạn đến với <b>Bảng Điều Khiển Phân Tích TikTok</b>, một công cụ mạnh mẽ sử dụng Streamlit để khám phá dữ liệu người dùng, chỉ số tương tác và xu hướng trên TikTok. 
Dù bạn là người đam mê dữ liệu, nhà tiếp thị hay người sáng tạo nội dung trên TikTok, bảng điều khiển này mang đến <span style="color: #FF5555;">hình ảnh trực quan tương tác</span> giúp bạn dễ dàng nắm bắt sự phát triển của nền tảng này.
</div>
""", unsafe_allow_html=True)

# Divider
st.markdown("---")

# Features section
st.header("✨ Tính Năng")
st.markdown("""
<div style="font-size: 16px; line-height: 1.5;">
<ul style="list-style-type: none; padding-left: 0;">
    <li>📊 <a href="?page=hashtags_insights" style="color: #636EFA; text-decoration: none;">Bảng Phân Tích Hashtag Nâng Cao</a>: Khám phá hashtag được đánh giá hiệu quả nhất, số lượng hashtag tối ưu cho video, xu hướng sử dụng hashtag theo thời gian.</li>
    <li>🏆 <a href="?page=single_hashtag" style="color: #EF553B; text-decoration: none;">Phân Tích Hashtag Đơn Lẻ</a>: Xác định hiệu suất theo thời gian, những hashtag thường được cùng sử dụng và người dùng sử dụng hiệu quả nhất.</li>
    <li>📈 <a href="?page=video_performance" style="color: #00CC96; text-decoration: none;">Phân Tích Hiệu Suất Video TikTok </a>: Đánh giá các chỉ số tương tác - Lượt xem, lượt thích, bình luận và chia sẻ; các top video hiệu suất cao theo thời gian đăng của video.</li>
</ul>
</div>
""", unsafe_allow_html=True)

# Divider
st.markdown("---")

# Instructions section
st.header("🚀 Hướng Dẫn Sử Dụng")
st.markdown("""
<div style="font-size: 16px; line-height: 1.5;">
<ol style="padding-left: 20px;">
    <li><b>Điều Hướng</b>: Sử dụng thanh bên để chuyển đổi giữa các trang.</li>
    <li><b>Tương Tác</b>: Điều chỉnh thanh trượt, danh sách thả xuống.</li>
    <li><b>Khám Phá</b>: Xem dữ liệu qua các biểu đồ trực quan tương tác và tải xuống thông tin chi tiết.</li>
    <li><b>Lọc</b>: Sử dụng bộ lọc Chỉ số / Loại tổng hợp / Nhóm thời gian trên các trang cụ thể để tập trung vào khoảng thời gian bạn quan tâm.</li>
</ol>
</div>
""", unsafe_allow_html=True)

display_footer()