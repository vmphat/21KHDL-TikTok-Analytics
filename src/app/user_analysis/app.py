import streamlit as st
from styles import apply_styles
from data_loader import load_data
from pages.correlation_analysis import correlation_analysis
from pages.personal_analysis import personal_analysis
from pages.hashtag_song_analysis import hashtag_song_analysis
from footer import display_footer


# Apply global styles
apply_styles()

# Load data
cleaned_user_info_df, cleaned_video_info_df = load_data()

# Sidebar navigation
st.sidebar.title("📊 TikTok Analysis Dashboard")
page = st.sidebar.radio("Select Page", ["Correlation Analysis", "Personal Analysis", "Hashtag & Song Analysis"])

# Page routing
if page == "Correlation Analysis":
    correlation_analysis(cleaned_user_info_df)
elif page == "Personal Analysis":
    personal_analysis(cleaned_video_info_df)
elif page == "Hashtag & Song Analysis":
    hashtag_song_analysis(cleaned_video_info_df)

st.write(f"Selected page: {page}")
# logger.debug("Minimal app rendered.")
# Display footer
display_footer()
