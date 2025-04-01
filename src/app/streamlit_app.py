import streamlit as st

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False


def login():
    if st.button("Log in"):
        st.session_state.logged_in = True
        st.rerun()


def logout():
    if st.button("Log out"):
        st.session_state.logged_in = False
        st.rerun()


login_page = st.Page(login, title="Log in", icon=":material/login:")
logout_page = st.Page(logout, title="Log out", icon=":material/logout:")

# dashboard = st.Page(
#     "reports/dashboard.py", title="Dashboard", icon=":material/dashboard:", default=True
# )
# bugs = st.Page("reports/bugs.py", title="Bug reports",
#                icon=":material/bug_report:")
# alerts = st.Page(
#     "reports/alerts.py", title="System alerts", icon=":material/notification_important:"
# )


# ******************** TikToker Analysis Pages ********************
user_analysis_overview = st.Page(
    "user_analysis/user_overview_page.py",
    title="Tổng quan",
    icon=":material/auto_graph:",
    # default=True,
)
user_correlation = st.Page(
    "user_analysis/correlation_analysis.py",
    title="Phân tích tương quan",
    icon=":material/auto_graph:",
)
personal_analysis = st.Page(
    "user_analysis/personal_analysis.py",
    title="Phân tích 1 TikToker",
    icon=":material/auto_graph:",
)
hashtag_song_analysis = st.Page(
    "user_analysis/hashtag_song_analysis.py",
    title="Phân tích hashtag và bài hát",
    icon=":material/auto_graph:",
)

# ******************** Introduction Pages ********************
about_us = st.Page(
    "introduction/about_us.py",
    title="Giới thiệu về chúng tôi",
    icon=":material/groups:",
)


# ******************** Video Analysis Pages ********************
video_analysis_overview = st.Page(
    "video_analysis/video_overview_page.py",
    title="Tổng quan",
    icon=":material/auto_graph:",
    # default=True,
)
video_analysis = st.Page(
    "video_analysis/video_analysis.py",
    title="Phân tích video",
    icon=":material/auto_graph:",
)
content_analysis = st.Page(
    "video_analysis/content_analysis.py",
    title="Phân tích nội dung",
    icon=":material/auto_graph:",
)

# ******************** Scriptwriting Pages ********************
scriptwriting_app = st.Page(
    "scriptwriting/scriptwriting_app.py",
    title="Tổng quan",
    icon=":material/auto_awesome:",
    # default=True,
)
research = st.Page("scriptwriting/research.py",
                   title="Nghiên cứu chủ đề",  # "Research on topics"
                   icon=":material/search:")
scriptwriting = st.Page("scriptwriting/write_scripts.py",
                        title="Viết kịch bản",  # "Write Scripts"
                        icon=":material/edit_note:")
insights = st.Page("scriptwriting/insights.py",
                   title="Tối ưu kênh TikTok",  # "Optimize TikTok channel"
                   icon=":material/insights:")

st.session_state.logged_in = True
if st.session_state.logged_in:
    pg = st.navigation(
        {
            # "Account": [logout_page],
            # "Reports": [dashboard, bugs, alerts],

            # Giới thiệu về chúng tôi
            "Giới thiệu về chúng tôi": [
                about_us,
            ],

            # Phân tích về các TikToker
            "Phân tích TikToker": [
                user_analysis_overview,
                user_correlation,
                personal_analysis,
                hashtag_song_analysis,
            ],

            # Phân tích video
            "Phân tích video": [
                video_analysis_overview,
                video_analysis,
                content_analysis,
            ],

            # Các công cụ giúp người dùng nghiên cứu và viết kịch bản
            "Các công cụ hỗ trợ": [
                scriptwriting_app,
                research,
                scriptwriting,
                insights,
            ],
        }
    )
else:
    # pg = st.navigation([login_page])
    pass

pg.run()
