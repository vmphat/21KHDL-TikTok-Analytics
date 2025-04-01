import streamlit as st
from datetime import datetime
import pytz

def display_footer():
    vn_timezone = pytz.timezone("Asia/Ho_Chi_Minh")
    vn_time = datetime.now(vn_timezone).strftime("%Y-%m-%d %H:%M:%S")
    st.markdown(f'''
        <div style="position: absolute; bottom: 10px; right: 20px; margin: -20px; color: #999; font-size: 18px;">
            🕒 Last updated: {vn_time}
        </div>
    ''', unsafe_allow_html=True)
