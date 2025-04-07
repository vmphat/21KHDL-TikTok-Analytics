stat_type = st.radio(
        "Loại thống kê:",
        options=list(STAT_TYPES.keys()),
        format_func=lambda x: STAT_TYPES.get(x, x),
        horizontal=True
    )