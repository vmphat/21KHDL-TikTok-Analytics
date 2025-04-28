import streamlit as st

# Set page configuration
st.set_page_config(
    page_title="Scriptwriting App",
    page_icon="📝",
    layout="wide"
)

# Main page content
st.title("Webapp hỗ trợ viết kịch bản video TikTok")
st.write("Chào mừng đến với ứng dụng hỗ trợ viết kịch bản video TikTok! Sử dụng thanh bên để điều hướng đến các trang khác nhau.")


research_page = st.Page(
    "scriptwriting/pages/research.py",
    title="Nghiên cứu chủ đề",
    icon=":material/search:"
)
suggestion_page = st.Page(
    "scriptwriting/pages/suggestion.py",
    title="Gợi ý cách quay video",
    icon=":material/lightbulb:"
)
scriptwriting_page = st.Page(
    "scriptwriting/pages/write_scripts.py",
    title="Viết kịch bản",
    icon=":material/edit_note:"
)
insights_page = st.Page(
    "scriptwriting/pages/insights.py",
    title="Tối ưu kênh TikTok",
    icon=":material/insights:"
)


page_link_title = "**:blue[%s]**"

# Add some content to the main page
st.divider()
st.header("Các chức năng chính của ứng dụng")
st.write(
    "Ứng dụng này cung cấp các công cụ giúp bạn nghiên cứu và viết kịch bản cho video TikTok một cách dễ dàng và hiệu quả.")
st.write(
    "Bạn có thể sử dụng các công cụ sau để hỗ trợ quá trình sáng tạo nội dung của mình:")

# Tạo liên kết từ tên trang đến các trang con dùng `st.page_link`
st.page_link(research_page, icon="1️⃣",
             label=page_link_title % "Nghiên cứu chủ đề",
             )
st.page_link(suggestion_page, icon="2️⃣",
             label=page_link_title % "Gợi ý cách quay video",
             )
st.page_link(scriptwriting_page, icon="3️⃣",
             label=page_link_title % "Viết kịch bản",
             )
st.page_link(insights_page, icon="4️⃣",
             label=page_link_title % "Tối ưu kênh TikTok",
             )
