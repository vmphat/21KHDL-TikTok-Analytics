import streamlit as st
from user_analysis.utils.footer import display_footer

# Set page configuration
st.set_page_config(
    layout="wide"
)

# Nội dung trang chính
st.title("🎵 Bảng Điều Khiển Phân Tích TikTok", anchor=None)
st.markdown("""
<div style="font-size: 18px; line-height: 1.6; color: #333;">
Chào mừng bạn đến với <b>Bảng Điều Khiển Phân Tích TikTok</b>, một công cụ mạnh mẽ sử dụng Streamlit để khám phá dữ liệu người dùng, chỉ số tương tác và xu hướng trên TikTok. 
Dù bạn là người đam mê dữ liệu, nhà tiếp thị hay người sáng tạo nội dung trên TikTok, bảng điều khiển này mang đến <span style="color: #FF5555;">hình ảnh trực quan tương tác</span> giúp bạn dễ dàng nắm bắt sự phát triển của nền tảng này.
</div>
""", unsafe_allow_html=True)

# Đường phân cách
st.markdown("---")

# Mục Tính Năng
st.header("✨ Tính Năng", anchor=None)
st.markdown("""
<div style="font-size: 16px; line-height: 1.5;">
<ul style="list-style-type: none; padding-left: 0;">
    <li>📊 <a href="?page=correlation_analysisanalysis" style="color: #636EFA; text-decoration: none;">Phân Tích Tương Quan</a>: Khám phá mối quan hệ giữa số người theo dõi, lượt thích và số lượng video qua biểu đồ histogram, ma trận phân tán và bản đồ nhiệt.</li>
    <li>🏆 <a href="?page=top_users" style="color: #EF553B; text-decoration: none;">Người Dùng Hàng Đầu</a>: Xác định những người có ảnh hưởng nhất trên TikTok dựa trên lượt thích, người theo dõi hoặc tỷ lệ tương tác.</li>
    <li>📈 <a href="?page=engagement_insight" style="color: #00CC96; text-decoration: none;">Phân Tích Tương Tác</a>: Đánh giá cách mức độ tương tác thay đổi theo số lượng người theo dõi.</li>
    <li>👤 <a href="?page=personal_analysis" style="color: #AB63FA; text-decoration: none;">Phân Tích Cá Nhân</a>: Khám phá hồ sơ của từng TikToker, xu hướng video, việc sử dụng nhạc và mô hình hashtag.</li>
    <li>🎶 <a href="?page=personal_analysis" style="color: #FFA15A; text-decoration: none;">Phân Tích Hashtag & Bài Hát</a>: Tìm kiếm các hashtag và bài hát phổ biến trong một khoảng thời gian cụ thể.</li>
    <li>🖌️ <a href="?page=personal_analysis" style="color: #19D3F3; text-decoration: none;">Hình Ảnh Trực Quan Tương Tác</a>: Được xây dựng với Plotly để tạo biểu đồ động và có thể tùy chỉnh.</li>
    <li>📥 <a href="?page=top_users" style="color: #FF6692; text-decoration: none;">Xuất Dữ Liệu</a>: Tải xuống dữ liệu biểu đồ dưới dạng tệp CSV để phân tích sâu hơn.</li>
</ul>
</div>
""", unsafe_allow_html=True)

# Đường phân cách
st.markdown("---")

# Mục Hướng Dẫn Sử Dụng
st.header("🚀 Hướng Dẫn Sử Dụng", anchor=None)
st.markdown("""
<div style="font-size: 16px; line-height: 1.5;">
<ol style="padding-left: 20px;">
    <li><b>Điều Hướng</b>: Sử dụng thanh bên để chuyển đổi giữa các trang.</li>
    <li><b>Tương Tác</b>: Điều chỉnh thanh trượt, danh sách thả xuống và hộp kiểm để tùy chỉnh biểu đồ.</li>
    <li><b>Khám Phá</b>: Xem dữ liệu qua các biểu đồ trực quan tương tác và tải xuống thông tin chi tiết.</li>
    <li><b>Lọc</b>: Sử dụng bộ lọc thời gian trên các trang cụ thể để tập trung vào khoảng thời gian bạn quan tâm.</li>
</ol>
</div>
""", unsafe_allow_html=True)

# Đường phân cách
st.markdown("---")

# Mục Bắt Đầu
st.header("🌟 Bắt Đầu", anchor=None)
st.markdown("""
<div style="font-size: 16px; line-height: 1.5;">
<ul style="list-style-type: none; padding-left: 0;">
    <li>✅ Ứng dụng đã sẵn sàng! Chỉ cần chọn một trang từ thanh bên để bắt đầu.</li>
    <li>📂 Dữ liệu được tải trước từ <code>cleaned_user_info.csv</code> và <code>cleaned_video_info.csv</code>.</li>
    <li>ℹ️ Để biết thêm thông tin, hãy xem <a href="https://github.com/vphuhan/21KHDL-TikTok-Analytics" target="_blank">README</a> hoặc liên hệ với chúng tôi tại <a href="https://github.com/vphuhan/21KHDL-TikTok-Analytics" target="_blank">Nhóm IDA</a>.</li>
</ul>
</div>
""", unsafe_allow_html=True)

# Lời kêu gọi hành động
st.markdown("<br>", unsafe_allow_html=True)  # Thêm khoảng cách
st.success("Sẵn sàng khám phá? Chọn một trang từ thanh bên và bắt đầu phân tích xu hướng TikTok ngay bây giờ!", icon="🚀")

# Hiển thị phần chân trang
# Thêm khoảng cách trước phần chân trang
st.markdown("<br>", unsafe_allow_html=True)
display_footer()
