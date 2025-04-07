import streamlit as st
import os
import sys


def read_markdown_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        return f"Error reading file: {e}"


def extract_sections(markdown_text):
    """Extract sections with headings from markdown text"""
    # Split the text into lines
    lines = markdown_text.split('\n')
    sections = []
    current_heading = None
    current_content = []

    for line in lines:
        # Check if line is a heading
        if line.startswith('#'):
            # If we already have a heading, save the previous section
            if current_heading:
                sections.append((current_heading, '\n'.join(current_content)))

            # Extract the new heading (remove # and trim)
            current_heading = line.lstrip('#').strip()
            current_content = []
        elif current_heading is not None:
            current_content.append(line)

    # Add the last section
    if current_heading:
        sections.append((current_heading, '\n'.join(current_content)))

    return sections


st.set_page_config(page_title="Project Insights", layout="wide")

# Viết tiêu đề cho trang
st.title("Gợi ý để tăng hiệu suất phát triển kênh TikTok")
st.write(
    "Thông qua việc phân tích các video TikTok, chúng tôi đã rút ra một số gợi ý để giúp bạn tối ưu hóa kênh của mình. Dưới đây là một số điểm nổi bật từ các video thành công nhất:")


# Path to the insights file
insights_path = "data/insights/insights.md"

# Check if file exists
if not os.path.exists(insights_path):
    st.error(f"Could not find insights file at {insights_path}")
    sys.exit(1)

# Read the markdown content
md_content = read_markdown_file(insights_path)

# Extract sections
sections = extract_sections(md_content)

# If sections exist, display them as expanders
if sections:
    for heading, content in sections:
        with st.expander(f"**:blue[{heading}]**", expanded=True):
            st.markdown(content)
else:
    # If no sections found, just show the whole content
    st.markdown(md_content)
