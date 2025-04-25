import os
import sys
try:
    import streamlit as st
    from google import genai
    import time
except ImportError as e:
    import traceback
    print(f"Error importing required packages: {e}")
    print(traceback.format_exc())
    try:
        # If streamlit is successfully imported, show error in UI
        if 'st' in globals():
            st.error(
                f"Failed to import required packages. Please install them using: pip install -r requirements.txt\n\nError: {e}")
            st.stop()
    except:
        # If we can't even use streamlit, exit the program
        sys.exit(1)


# App configuration
st.set_page_config(
    # Research on topics
    page_title="Nghiên cứu chủ đề",  # "Research on topics"
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon=":material/search:",  # "🔍"
)

# Định nghĩa system prompt và user prompt
# System prompt
system_prompt = f"""
Bạn là một chuyên gia nghiên cứu với kiến thức sâu rộng về nhiều lĩnh vực. Nhiệm vụ của bạn là cung cấp các bài giải thích chi tiết về một chủ đề được người dùng nhập vào. Khi nhận yêu cầu, hãy trả lời theo định dạng Markdown với từng phần sau (mỗi phần cách nhau bằng dòng trống):

```
### Overview
- Giới thiệu chung về chủ đề, giải thích ý nghĩa và tầm quan trọng của nó.

### Key Points
- Liệt kê và giải thích các yếu tố cốt lõi, những khía cạnh quan trọng của chủ đề.

### Examples
- Đưa ra các ví dụ cụ thể hoặc trường hợp nghiên cứu liên quan đến chủ đề.

### Challenges
- Nêu ra những thách thức, khó khăn hoặc những hiểu lầm phổ biến liên quan đến chủ đề.

### Best Practices
- Đề xuất các chiến lược, hướng dẫn hoặc mẹo hữu ích trong việc áp dụng chủ đề vào thực tiễn.

### Trends
- Phân tích các xu hướng hiện tại và dự đoán những hướng phát triển trong tương lai của chủ đề.

### Resources
- Gợi ý thêm các nguồn tài liệu, website, sách, bài viết hoặc video để người dùng có thể nghiên cứu sâu hơn.
```

**Chú ý:**
- Cung cấp thông tin một cách rõ ràng, súc tích và chính xác.
- Giữ cho mỗi phần có nội dung đầy đủ nhưng không quá dài dòng, dễ hiểu cho người dùng.
- Sử dụng định dạng Markdown với tiêu đề rõ ràng và danh sách gạch đầu dòng để tạo cấu trúc trực quan cho bài giải thích.
- Tập trung vào những điểm cốt lõi và thông tin hữu ích nhất cho người dùng.
- Chỉ trả về nội dung được giới hạn giữa các dấu ba dấu nháy đơn (```) mà không có bất kỳ văn bản nào khác bên ngoài.
- Nội dung giữa các dấu ba dấu nháy đơn có thể được thay đổi để phù hợp với yêu cầu của người dùng.
"""
# Default user prompt
default_user_prompt = f"""
Bài giải thích sẽ bao gồm các phần sau:

- Tổng quan: Giới thiệu về chủ đề và tầm quan trọng của nó.
- Các điểm chính: Liệt kê và giải thích các yếu tố quan trọng của chủ đề.
- Ví dụ: Cung cấp ví dụ hoặc trường hợp nghiên cứu liên quan đến chủ đề.
- Thách thức: Thảo luận về những thách thức hoặc hiểu lầm phổ biến.
- Best Practices: Đề xuất các chiến lược hoặc mẹo hiệu quả.
- Xu hướng: Xác định các xu hướng hiện tại hoặc hướng đi trong tương lai.
- Tài nguyên: Đề xuất các tài nguyên bổ sung để tìm hiểu thêm.
"""


# Available AI Models
available_models = [
    # Input token limit: 1,048,576
    # Output token limit: 65,536
    "gemini-2.5-pro-exp-03-25",

    # Input token limit: 1,048,576
    # Output token limit: 8,192
    "gemini-2.0-flash",

    # Input token limit 2,048,576
    # Output token limit 8,192
    "gemini-2.0-pro-exp",

    "gemini-2.0-flash-thinking-exp",

    # Input token limit 1,048,576
    # Output token limit 8,192
    "gemini-2.0-flash-lite",

    # Input token limit 1,048,576
    # Output token limit 8,192
    "gemini-1.5-flash",

    # Input token limit 1,048,576
    # Output token limit 8,192
    "gemini-1.5-flash-8b",
    "gemini-1.5-pro",
    "learnlm-1.5-pro-experimental",
    "gemma-3-27b-it",
]


def standardize_response(response: str) -> str:
    """ Standardize the response from Gemini API by removing unnecessary parts """

    # Remove first line
    if response.startswith("```"):
        response = response.split("\n", 1)[1]
    # Remove last line
    if response.endswith("```"):
        response = response.rsplit("\n", 1)[0]
    # Remove leading and trailing whitespace
    response = response.strip()

    return response


def get_model():
    # Function to get the selected model
    return st.sidebar.selectbox(
        label="Chọn mô hình AI:",
        options=available_models,
        index=available_models.index(
            "gemini-2.5-pro-exp-03-25"),  # Default model
    )


# Get selected model
model = get_model()
# print("Selected model:", model)

# Tiêu đề trang và mô tả
st.title("Nghiên cứu chủ đề")
st.markdown(
    "Tạo ra các giải thích chi tiết về nhiều chủ đề khác nhau với sự hỗ trợ của AI")


# Set start session time
if 'start_time' not in st.session_state:
    st.session_state.start_time = time.time()
# Prompt customization section
if 'prompt' not in st.session_state:
    st.session_state.research_prompt = default_user_prompt
# Store last response from the AI
if 'last_response' not in st.session_state:
    st.session_state.last_response = ""

# with st.expander("View/Edit Research Prompt", expanded=False):
with st.expander(f"**:blue[Xem/Chỉnh sửa prompt]**", expanded=False):
    st.markdown(
        "Đây là hướng dẫn gửi đến mô hình AI. Bạn có thể sửa đổi nó để phù hợp hơn với nhu cầu của bạn.")

    # Text area for editing the prompt
    custom_prompt = st.text_area(
        "**Bạn có thể tùy chỉnh prompt bên dưới:**",
        # Use the same key as the session state variable
        key=f"1_research_custom_prompt_{st.session_state.start_time}",
        value=st.session_state.research_prompt,
        height=300
    )

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Cập nhật prompt"):
            st.success("Đã cập nhật prompt!")
            st.session_state.research_prompt = custom_prompt
            # st.session_state.start_time = time.time()
            # st.rerun()

    with col2:
        if st.button("Khôi phục prompt mặc định"):
            st.success("Đã khôi phục prompt mặc định!")
            st.session_state.research_prompt = default_user_prompt
            # st.session_state.start_time = time.time()
            # st.rerun()

# # Cập nhật lại biến prompt
# prompt = st.session_state.research_prompt
# # print("Prompt:", prompt)


# Main content
topic = st.text_area(
    "**Nhập chủ đề bạn muốn nghiên cứu:**",
    height=100,
    placeholder="Chẳng hạn: Đánh giá món ăn, Nấu ăn, Du lịch, v.v.",
)
# Thể hiện 1 ví dụ minh họa
with st.expander(label="**Ví dụ minh họa**", expanded=True):
    st.write("Đánh giá món ăn")

# print(f"Topic: {topic}")

# Generate content when button is pressed
if st.button("Tiến hành nghiên cứu") and topic:
    try:
        # Research on the topic
        with st.spinner("Đang nghiên cứu..."):
            # print(prompt % topic)

            client = genai.Client(
                api_key="AIzaSyBYqr4g63GOBTslf5xP0-AbIcSSlAuvMnM")
            response = client.models.generate_content(
                model=model,
                contents=[
                    system_prompt,
                    f"Hãy giúp tôi tạo ra một bài giải thích chi tiết về chủ đề {topic}." +
                    st.session_state.research_prompt,
                ]
            )
            response = standardize_response(response.text)
            st.session_state.last_response = response

        # Display results
        st.subheader("Kết quả nghiên cứu:", divider="gray")
        # Display the response in a text area
        # st.write(response)
        st.write(st.session_state.last_response)

        # Cho phép người download nội dung
        st.download_button(
            label="Tải xuống nội dung",
            data=f"# Chủ đề: {topic}\n\n{response}",
            file_name="research_topic.md",
            mime="text/markdown",
            help="Tải xuống nội dung đã nghiên cứu dưới dạng tệp .md",
        )

        # # Expandable sections for additional info
        # with st.expander('Title History'):
        #     st.info(title_memory.buffer)

        # with st.expander('Script History'):
        #     st.info(script_memory.buffer)

        # with st.expander('Wikipedia Research'):
        #     st.info(wiki_research)

        # # Download options
        # st.download_button(
        #     label="Download Script",
        #     data=f"TITLE: {title}\n\n{script}",
        #     file_name="youtube_script.txt",
        #     mime="text/plain"
        # )

    except Exception as e:
        st.error(f"An error occurred: {e}")

elif topic == "":
    # Hướng dẫn nhanh cho người dùng
    st.info("Hãy nhập chủ đề bạn muốn nghiên cứu và nhấn nút 'Tiến hành nghiên cứu'.")
