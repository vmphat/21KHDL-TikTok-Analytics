import streamlit as st

# Page configuration
st.set_page_config(
    page_title="About Us",
    page_icon="🧑‍🤝‍🧑",
    layout="wide",
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 42px;
        font-weight: 700;
        color: #3a69c7;
        text-align: center;
        margin-bottom: 10px;
    }
    .sub-header {
        font-size: 24px;
        font-weight: 500;
        color: #555;
        text-align: center;
        margin-bottom: 30px;
    }
    .section-header {
        font-size: 28px;
        font-weight: 600;
        color: #2D3A4A;
        margin-top: 20px;
        margin-bottom: 20px;
        padding-bottom: 10px;
        border-bottom: 2px solid #3a69c7;
    }
    .card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
    }
    .team-member {
        padding: 8px 15px;
        margin: 5px;
        background-color: #E8F4F9;
        border-radius: 50px;
        display: inline-block;
        font-weight: 500;
    }
    .highlight {
        color: #3a69c7;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header">🧑‍🤝‍🧑 Giới thiệu về nhóm</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Chuyển hóa dữ liệu TikTok thành các insights chất lượng</div>', unsafe_allow_html=True)

# Course information
st.markdown('<div class="section-header">📚 Giới thiệu về môn học</div>', unsafe_allow_html=True)

col1, space, col2 = st.columns([5, 0.5, 5])
with col1:    
    st.markdown("""
    <div class="card">
    <b>Môn học:</b> Ứng dụng Phân tích Dữ liệu Thông minh<br>
    <b>Lớp:</b> 21KHDL<br>
    <b>Nhóm:</b> 01<br>
    <b>Giảng viên hướng dẫn:</b><br>
    &bull; Nguyễn Tiến Huy<br>
    &bull; Nguyễn Trần Duy Minh
    </div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown("""
    <div class="card">
    <b>Môn học:</b> Khoa học Dữ liệu Ứng dụng<br>
    <b>Lớp:</b> 21KHDL<br>
    <b>Nhóm:</b> 05<br>
    <b>Giảng viên hướng dẫn:</b><br>
    &bull; Lê Ngọc Thành<br>
    &bull; Trần Quốc Huy<br>
    &bull; Lê Nhựt Nam
    </div>
    """, unsafe_allow_html=True)

# About project
st.markdown('<div class="section-header">🚀 Về dự án</div>', unsafe_allow_html=True)
st.markdown("""
<div class="card">
Nhóm đang phát triển một webapp hiện đại giúp:
<ul>
    <li><b>Phân tích dữ liệu TikTok:</b> Tạo các dashboard trực quan hiển thị các số liệu quan trọng từ dữ liệu TikTok.</li>
    <li><b>Hỗ trợ viết kịch bản:</b> Sử dụng các insights từ phân tích để tạo ra nội dung kịch bản sáng tạo.</li>
</ul>

Mục tiêu của dự án là cung cấp công cụ mạnh mẽ và dễ sử dụng cho các nhà sáng tạo nội dung, marketer và doanh nghiệp nhằm nắm bắt xu hướng cũng như tối ưu hóa chiến lược truyền thông.

Để biết thêm chi tiết về mã nguồn và tiến trình phát triển, bạn hãy truy cập <a href="https://github.com/vphuhan/21KHDL-TikTok-Analytics/tree/main">GitHub của nhóm</a>.
</div>
""", unsafe_allow_html=True)

# Technologies
st.markdown('<div class="section-header">⚙️ Công nghệ & Quy trình phát triển</div>', unsafe_allow_html=True)
col1, col2 = st.columns(spec=2, gap="small")
with col1:
    st.markdown("""
    <div class="card">
    <h3>🛠️ Công nghệ sử dụng</h3>
    <ul>
        <li><b>Ngôn ngữ lập trình:</b> Python</li>
        <li><b>Trực quan hóa dữ liệu:</b> Plotly</li>
        <li><b>Webapp:</b> Streamlit cho giao diện dashboard</li>
        <li><b>AI agents:</b> Sử dụng Gemini API trong hầu hết các tác vụ thông minh</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="card">
    <h3>📋 Quy trình phát triển</h3>
    <ul>
        <li>Phân tích yêu cầu và thu thập dữ liệu từ TikTok</li>
        <li>Thực hiện tiền xử lý dữ liệu và rút trích các đặc trưng cần thiết</li>
        <li>Xây dựng các dashboard có thể tương tác được thông qua giao diện web</li>
        <li>Tạo ra một công cụ hỗ trợ viết kịch bản mạnh mẽ từ kết quả phân tích dữ liệu</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

# Team members
st.markdown('<div class="section-header">👥 Thành viên tham gia thực hiện</div>', unsafe_allow_html=True)
st.markdown("""
<div class="card" style="text-align: center;">
<div class="team-member">21127739 - Vũ Minh Phát</div>
<div class="team-member">21127038 - Võ Phú Hãn</div>
<div class="team-member">21127731 - Nguyễn Trọng Tín</div>
<div class="team-member">21127351 - Hồ Đinh Duy Lực</div>
<div class="team-member">19127216 - Đặng Hoàn Mỹ</div>
<div class="team-member">21127742 - Nguyễn Minh Hiếu</div>
</div>
""", unsafe_allow_html=True)


# Vision and mission
st.markdown('<div class="section-header">🌟 Tầm nhìn & Sứ mệnh</div>', unsafe_allow_html=True)
st.markdown("""
<div class="card">
<p>Nhóm tin rằng, trong kỷ nguyên số, dữ liệu chính là nguồn cảm hứng sáng tạo.</p>

<p><b>Tầm nhìn:</b> Mang lại những giải pháp phân tích dữ liệu tối ưu cho mọi người dùng.</p>

<p><b>Sứ mệnh:</b> Giúp các nhà sáng tạo nội dung khai thác triệt để những dữ liệu giá trị, từ đó tạo ra các nội dung độc đáo và hiệu quả.</p>
</div>
""", unsafe_allow_html=True)

# Contact
st.markdown('<div class="section-header">🤝 Liên hệ và Cộng Tác</div>', unsafe_allow_html=True)
st.markdown("""
<div class="card">
<p>Nếu bạn có ý tưởng, góp ý hoặc muốn hợp tác cùng nhóm, hãy liên hệ qua email hoặc truy cập trang <a href="https://github.com/vphuhan/21KHDL-TikTok-Analytics/tree/main">GitHub của nhóm</a> để biết thêm thông tin.</p>
</div>
""", unsafe_allow_html=True)
