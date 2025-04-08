import streamlit as st


st.set_page_config(
    page_title="About Us",
    page_icon="🧑‍🤝‍🧑",
    layout="wide",
)

# Tiêu đề và mô tả chung
st.title("🧑‍🤝‍🧑 Giới thiệu về nhóm")
st.subheader("Chuyển hóa dữ liệu TikTok thành các insights chất lượng")
st.markdown(
    """
    **Môn học:** Ứng dụng Phân tích Dữ liệu Thông minh   
    **Lớp:** 21KHDL  
    **Nhóm:** 01  
    """
)

# Phần giới thiệu dự án của nhóm
st.header("🚀 Về Dự Án")
st.markdown(
    """
    Nhóm chúng tôi đang phát triển một webapp hiện đại giúp:
    - **Phân tích dữ liệu TikTok:** Tạo các dashboard trực quan hiển thị các số liệu quan trọng từ dữ liệu TikTok.
    - **Hỗ trợ viết kịch bản:** Sử dụng các insights từ phân tích để tạo ra nội dung kịch bản sáng tạo.
    
    Mục tiêu của dự án là cung cấp công cụ mạnh mẽ và dễ sử dụng cho các nhà sáng tạo nội dung, marketer và doanh nghiệp nhằm nắm bắt xu hướng cũng như tối ưu hóa chiến lược truyền thông.
    
    Để biết thêm chi tiết về mã nguồn và tiến trình phát triển, bạn hãy truy cập [GitHub của nhóm chúng tôi](https://github.com/vphuhan/21KHDL-TikTok-Analytics/tree/main).
    """
)

# Phần giới thiệu về công nghệ và quy trình làm việc
st.header("⚙️ Công Nghệ & Quy Trình Phát Triển")
st.markdown(
    """
    **Công nghệ sử dụng:**  
    - **Ngôn ngữ lập trình:** Python  
    - **Framework:** Streamlit cho giao diện dashboard  
    - **Cơ sở dữ liệu & Dữ liệu lớn:** Các công cụ xử lý và phân tích dữ liệu tiên tiến
    
    **Quy trình phát triển:**  
    - Phân tích yêu cầu và thu thập dữ liệu từ TikTok  
    - Xây dựng và đánh giá các mô hình phân tích dữ liệu  
    - Phát triển giao diện tương tác trên web  
    - Liên tục cập nhật và tối ưu hóa dựa trên phản hồi người dùng  
    """
)

# Giới thiệu thành viên trong nhóm
st.header("👥 Thành Viên Nhóm")
members = [
    "21127739 - Vũ Minh Phát",
    "21127038 - Võ Phú Hãn",
    "21127731 - Nguyễn Trọng Tín",
    "21127351 - Hồ Đinh Duy Lực",
    "19127216 - Đặng Hoàn Mỹ",
    "21127742 - Nguyễn Minh Hiếu"
]
for member in members:
    st.markdown(f"- {member}")

# Giảng viên hướng dẫn
st.header("🎓 Giảng Viên Hướng Dẫn")
instructors = [
    "Nguyễn Tiến Huy",
    "Nguyễn Trần Duy Minh"
]
for instructor in instructors:
    st.markdown(f"- {instructor}")

# Thông điệp của nhóm và lời kêu gọi
st.header("🌟 Tầm Nhìn & Sứ Mệnh")
st.markdown(
    """
    Chúng tôi tin rằng, trong kỷ nguyên số, dữ liệu chính là nguồn cảm hứng sáng tạo.  
    **Tầm nhìn:** Mang lại những giải pháp phân tích dữ liệu tối ưu cho mọi người dùng.  
    **Sứ mệnh:** Giúp các nhà sáng tạo nội dung khai thác triệt để những dữ liệu giá trị, từ đó tạo ra các nội dung độc đáo và hiệu quả.
    """
)

st.header("🤝 Liên hệ và Cộng Tác")
st.markdown(
    """
    Nếu bạn có ý tưởng, góp ý hoặc muốn hợp tác cùng chúng tôi, hãy liên hệ qua email hoặc truy cập trang [GitHub của nhóm](https://github.com/vphuhan/21KHDL-TikTok-Analytics/tree/main) để biết thêm thông tin.
    """
)
