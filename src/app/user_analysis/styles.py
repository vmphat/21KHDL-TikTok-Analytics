import streamlit as st

def apply_styles():
    st.markdown("""
        <style>
        .main-title {
            font-size: 28px;
            font-weight: bold;
            color: #FFFFFF;
            text-align: center;
            padding-bottom: 20px;
        }
        .subheader {
            font-size: 20px;
            font-weight: bold;
            color: #282c35;
            padding-top: 10px;
        }
        .stButton>button {
            background-color: #4CAF50;
            color: white;
            border-radius: 5px;
        }
        .stExpander {
            border-radius: 10px;
            padding: 10px;
        }

        </style>
    """, unsafe_allow_html=True)

def personal_styles():
    st.markdown("""
        <style>
        h1, h2, h3 { color: #1f2a44; font-family: 'Helvetica', sans-serif; }
        .stMetric { border-radius: 8px; padding: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        </style>
    """, unsafe_allow_html=True)

def hashtag_song_styles():
    st.markdown("""
        <style>
        h1, h3 { color: #2c3e50; font-family: 'Arial', sans-serif; }
        </style>
    """, unsafe_allow_html=True)
