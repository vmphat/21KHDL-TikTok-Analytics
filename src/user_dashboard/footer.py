import streamlit as st
from datetime import datetime
import pytz

def display_footer():
    vn_timezone = pytz.timezone("Asia/Ho_Chi_Minh")
    vn_time = datetime.now(vn_timezone).strftime("%Y-%m-%d %H:%M:%S")

    # Updated CSS for better centering of subject name
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap');
        .main .block-container {
            min-height: 100vh;
            padding-bottom: 10px;
        }
        .footer-content {
            position: relative;
            margin-top: 20px;
            background-color: #0b5345;
            color: #ffffff;
            padding: 25px;
            font-family: 'Roboto', sans-serif;
            font-size: 15px;
            width: 100%;
            text-align: center;
            box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.3);
        }
        .footer-container {
            max-width: 1600px;
            margin: 0 auto;
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        .title-container {
            display: flex;
            justify-content: center;
            align-items: center;
            width: 100%;
            padding: 10px 0;
            margin-bottom: 15px;
        }
        .title-text {
            font-size: 22px; /* Larger font size */
            font-weight: 900;
            background: linear-gradient(45deg, #27548A, #4ecdc4);
            -webkit-background-clip: text;
            background-clip: text;
            color: transparent;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
            white-space: nowrap;
        }
        .footer-content {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            gap: 30px;
        }
        .footer-column {
            flex: 1;
            text-align: left;
            padding: 10px;
        }
        .footer-column span {
            color: #b0b0d0;
        }
        </style>
    """, unsafe_allow_html=True)

    # Footer Content
    st.markdown('<div class="footer-container">', unsafe_allow_html=True)
    st.markdown(f'''
        <div class="title-container">
            <span class="title-text">PHÂN TÍCH DỮ LIỆU THÔNG MINH</span>
        </div>
        <div class="footer-content">
            <div class="footer-column">
                Teacher: Nguyễn Tiến Huy<br>
                Teacher: Nguyễn Trần Duy Minh<br>
                Năm học: 2024-2025
            </div>
            <div class="footer-column student-container">
                <b>21127739</b> - <span>Vũ Minh Phát</span><br>
                <b>21127038</b> - <span>Võ Phú Hãn</span><br>
                <b>21127731</b> - <span>Nguyễn Trọng Tín</span>
            </div>
            <div class="footer-column student-container">
                <b>21127351</b> - <span>Hồ Đinh Duy Lực</span><br>
                <b>19127216</b> - <span>Đặng Hoàn Mỹ</span><br>
                <b>21127742</b> - <span>Nguyễn Minh Hiếu</span>
            </div>
            <div class="footer-column">
                🕒 Last updated: {vn_time}
            </div>
        </div>
    ''', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

