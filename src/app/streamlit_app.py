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


# ******************** Introduction Pages ********************
about_us = st.Page(
    "introduction/about_us.py",
    title="Giới thiệu về chúng tôi",
    icon=":material/groups:",
)


# ******************** TikToker Analysis Pages ********************
user_analysis_overview = st.Page(
    "user_analysis/user_dashboard_app.py",
    title="Tổng quan",
    icon=":material/auto_graph:",
)
user_correlation = st.Page(
    "user_analysis/pages/correlation_analysis.py",
    title="Phân tích tương quan",
    icon=":material/auto_graph:",
)
engagement_insights = st.Page(
    "user_analysis/pages/engagement_insights.py",
    title="Phân tích mức độ tương tác",
    icon=":material/auto_graph:",
)
personal_analysis = st.Page(
    "user_analysis/pages/personal_analysis.py",
    title="Phân tích 1 TikToker",
    icon=":material/auto_graph:",
)
top_user_analysis = st.Page(
    "user_analysis/pages/top_user_analysis.py",
    title="Phân tích top TikToker",
    icon=":material/auto_graph:",
)


# ******************** Video Analysis Pages ********************
video_analysis_overview = st.Page(
    "video_analysis/video_dashboard_app.py",
    title="Tổng quan",
    icon=":material/auto_graph:",
)
hashtags_insights = st.Page(
    "video_analysis/pages/hashtags_insights.py",
    title="Phân tích hashtag nâng cao",
    icon=":material/auto_graph:",
)
single_hashtag = st.Page(
    "video_analysis/pages/single_hashtag.py",
    title="Phân tích hashtag đơn lẻ",
    icon=":material/auto_graph:",
)
video_performance = st.Page(
    "video_analysis/pages/video_performance.py",
    title="Phân tích hiệu suất video",
    icon=":material/auto_graph:",
)
content_analysis = st.Page(
    "video_analysis/pages/content_analysis.py",
    title="Phân tích nội dung",
    icon=":material/auto_graph:",
)


# ******************** Trend Analysis Pages ********************
trend_analysis_overview = st.Page(
    "trend_analysis/trend_dashboard_app.py",
    title="Tổng quan",
    icon=":material/auto_graph:",
)
food_location_analysis = st.Page(
    "trend_analysis/pages/food_location_analysis.py",
    title="Phân tích món ăn và địa điểm",
    icon=":material/auto_graph:",
)


# ******************** Scriptwriting Pages ********************
scriptwriting_app = st.Page(
    "scriptwriting/scriptwriting_app.py",
    title="Tổng quan",
    icon=":material/auto_awesome:",
)
research = st.Page("scriptwriting/pages/research.py",
                   title="Nghiên cứu chủ đề",  # "Research on topics"
                   icon=":material/search:")
suggestion = st.Page("scriptwriting/pages/suggestion.py",
                     title="Đề xuất quay video",  # "Video shooting suggestions"
                     icon=":material/lightbulb:")
scriptwriting = st.Page("scriptwriting/pages/write_scripts.py",
                        title="Viết kịch bản",  # "Write Scripts"
                        icon=":material/edit_note:")
insights = st.Page("scriptwriting/pages/insights.py",
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
                engagement_insights,
                personal_analysis,
                top_user_analysis,
            ],

            # Phân tích video
            "Phân tích video": [
                video_analysis_overview,
                hashtags_insights,
                single_hashtag,
                video_performance,
                content_analysis,
            ],


            # Phân tích xu hướng
            "Phân tích xu hướng": [
                trend_analysis_overview,
                food_location_analysis,
            ],


            # Các công cụ giúp người dùng nghiên cứu và viết kịch bản
            "Các công cụ hỗ trợ": [
                scriptwriting_app,
                research,
                suggestion,
                scriptwriting,
                insights,
            ],
        }
    )
else:
    # pg = st.navigation([login_page])
    pass

pg.run()
