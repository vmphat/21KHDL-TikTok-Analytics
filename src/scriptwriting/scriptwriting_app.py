import streamlit as st

# Set page configuration
st.set_page_config(
    page_title="Scriptwriting App",
    page_icon="📝",
    layout="wide"
)

# Main page content
st.title("Scriptwriting App")
st.write("Welcome to the Scriptwriting App! Use the sidebar to navigate to different pages.")

# Add some content to the main page
st.markdown("""
## Features
- Research on your interesting topic
- Script Writing for your content
- Optimize Your TikTok: Creator Insights & Performance Tips

Select a feature from the sidebar to get started!
""")

# Note: For this to work with Streamlit's multipage app feature:
# 1. Create a 'pages' folder in the same directory as this file
# 2. Add your page files inside that folder with names like "1_page1.py", "2_page2.py"
# 3. Each page file should be a standalone Streamlit script

# Example of what page1.py might look like:
# ```
# import streamlit as st
# st.title("Character Development")
# st.write("This is the character development page!")
# ```

# Streamlit will automatically add these pages to the sidebar navigation
