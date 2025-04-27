from typing import List, Dict, Any
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import re
from collections import defaultdict
import os
from google import genai
import warnings
from scipy import stats
warnings.filterwarnings('ignore')


# ================================================================
# *_____________________ [Define constants] _____________________*
# ================================================================
DARK_GRAY: str = "#444444"
CLEANED_FOOD_LOCATION_DATA_FILE: str = "src/app/trend_analysis/data/final_location_food_data.parquet"


# ================================================================
# *____________________ [Utility functions] _____________________*
# ================================================================
# Hàm giúp tạo nhận xét và rút ra insights từ kết quả phân tích và trực quan hóa dữ liệu
@st.cache_data(show_spinner=False)
def generate_insights(prompt: str, api_key: str) -> str:
    # return "[TEMPORARY] Chức năng này hiện đang tạm dừng hoạt động."
    """ Tạo nhận xét từ Gemini API """
    # Generate content
    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model="gemini-2.0-flash-lite",
            contents=[prompt]
        )
        return response.text
    except Exception as e:
        print(f"Lỗi khi tạo nội dung: {e}")
        return ""


# Tạo 1 module dành riêng cho việc rút trích insights từ biểu đồ
# và thể hiện lên trang web
def display_AI_generated_insights(prompt: str, api_key: str,
                                  print_to_console: bool = False,
                                  expanded: bool = True
                                  ) -> None:
    """ End-to-end module để rút trích insights từ biểu đồ và hiện thị lên trang web """

    with st.expander(
            label=":blue-background[:blue[**:material/auto_awesome: Nhận xét từ AI**]]",
            expanded=expanded):
        # Tạo nhận xét từ Gemini API
        with st.spinner(text="Đang tạo nhận xét từ AI...", show_time=True):
            insights = generate_insights(prompt=prompt, api_key=api_key)
            if not insights:
                st.error("Hiện tại hệ thống đang quá tải, vui lòng thử lại sau.")
            else:
                st.markdown(insights)
                if print_to_console:
                    print(f"Nhận xét từ AI:\n{insights}")


# Function to properly capitalize names for visualization
@st.cache_data(show_spinner=False, ttl=3600)
def proper_capitalize(text: str) -> str:
    """ Capitalize the first letter of each word in a string """

    if not isinstance(text, str):
        return text
    # Captialize the first letter of the string
    return " ".join([word.capitalize() for word in text.split()])


# Function to load and cache data
@st.cache_data
def load_food_location_data() -> pd.DataFrame:
    """ Load and cache the cleaned food location data """
    return pd.read_parquet(CLEANED_FOOD_LOCATION_DATA_FILE)


# Define functions for each section
@st.cache_data
def get_data_overview_info(df: pd.DataFrame) -> Dict[str, Any]:
    """Prepare data overview information without widgets"""
    # Calculate time range and metrics
    min_date = df['date'].min().strftime('%d/%m/%Y')
    max_date = df['date'].max().strftime('%d/%m/%Y')
    total_records = len(df)
    unique_weeks = df['year_week'].nunique()

    # Format year_week for display (Y2023_W47 format)
    df['year_week_formatted'] = df['year_week'].apply(
        lambda x: f"Y{x.split('-')[0]}_W{int(x.split('-')[1]):02d}" if '-' in str(x) else x
    )

    # Get formatted min and max year_week for display
    min_year_week: str = df['year_week'].min()
    max_year_week: str = df['year_week'].max()
    min_year_week_display: str = min_year_week.replace(
        "Y", "Năm ").replace("_W", " - Tuần ")
    max_year_week_display: str = max_year_week.replace(
        "Y", "Năm ").replace("_W", " - Tuần ")

    # Count records by week
    weekly_counts = df.groupby('year_week').size().reset_index(name='count')

    # Add the formatted display version
    weekly_counts['year_week_display'] = weekly_counts['year_week'].apply(
        lambda x: f"Y{x.split('-')[0]}_W{int(x.split('-')[1]):02d}" if '-' in str(x) else x
    )

    return {
        'min_date': min_date,
        'max_date': max_date,
        'total_records': total_records,
        'unique_weeks': unique_weeks,
        'min_year_week_display': min_year_week_display,
        'max_year_week_display': max_year_week_display,
        'weekly_counts': weekly_counts,
    }


def display_data_overview(df: pd.DataFrame) -> None:
    """ Display general overview and statistics about the dataset """

    st.markdown("<h2 class='sub-header'>Tổng Quan Dữ Liệu</h2>",
                unsafe_allow_html=True)

    overview_info = get_data_overview_info(df)

    # Hiển thị 4 cột thống kê cơ bản
    col1, col2, col3, col4 = st.columns(
        spec=[15, 35, 35, 15], gap="small", border=True)
    with col1:
        st.metric(label=":material/tag: Tổng số bản ghi",
                  value=f"{int(overview_info['total_records']):,}")
    with col2:
        st.metric(label=":material/first_page: Thời gian bắt đầu",
                  value=overview_info['min_year_week_display'])
    with col3:
        st.metric(label=":material/last_page: Thời gian kết thúc",
                  value=overview_info['max_year_week_display'])
    with col4:
        st.metric(label=":material/equalizer: Số tuần phân tích",
                  value=int(overview_info['unique_weeks']))

    # Vẽ biểu đồ cột thể hiện số lượng video theo tuần
    fig = px.bar(
        overview_info['weekly_counts'],
        x='year_week',
        y='count',
        labels={'count': 'Số lượng bản ghi'},
    )
    fig.update_layout(
        xaxis_title="",
        yaxis_title="",
        height=500,
        hovermode="x unified",
        yaxis=dict(range=[0, 300]),
        margin=dict(b=120),

        # Đặt tiêu đề cho biểu đồ
        title=dict(
            text='Số lượng bản ghi theo tuần',
            font=dict(size=26, color=DARK_GRAY),
            x=0,     # Adjust horizontal position
            # y=0.95,  # Adjust vertical position
        ),
    )
    fig.update_xaxes(
        tickmode='array',
        tickvals=overview_info['weekly_counts']['year_week'].tolist(),
        ticktext=overview_info['weekly_counts']['year_week_display'].tolist(),
        tickangle=60,
        tickfont=dict(size=10)
    )
    # Add custom hover template
    fig.update_traces(
        hovertemplate='<b>%{x}</b><br>Số lượng: %{y:,.0f}<extra></extra>',
    )

    st.plotly_chart(fig, use_container_width=True)


def analyze_weekly_trends(df: pd.DataFrame) -> None:
    """
    Analyze and visualize the weekly trends of Vietnamese food videos on TikTok
    over the entire dataset period.
    """
    st.markdown("<h2 class='sub-header'>Phân Tích Xu Hướng Theo Thời Gian</h2>",
                unsafe_allow_html=True)

    # Group by week and count records
    weekly_counts = df.groupby('year_week').size().reset_index(name='count')

    # Make sure weekly_counts is sorted chronologically
    weekly_counts = weekly_counts.sort_values('year_week')

    # Calculate statistics
    total_weeks = len(weekly_counts)
    average_videos = weekly_counts['count'].mean()
    median_videos = weekly_counts['count'].median()
    max_videos = weekly_counts['count'].max()
    min_videos = weekly_counts['count'].min()

    # Calculate growth metrics
    first_4_weeks_avg = weekly_counts['count'].iloc[:4].mean()
    last_4_weeks_avg = weekly_counts['count'].iloc[-4:].mean()
    growth_rate = ((last_4_weeks_avg - first_4_weeks_avg) /
                   first_4_weeks_avg) * 100 if first_4_weeks_avg > 0 else 0

    # Calculate moving averages
    weekly_counts['4_week_ma'] = weekly_counts['count'].rolling(
        window=4, min_periods=1).mean()

    # Calculate week-over-week changes
    weekly_counts['wow_change'] = weekly_counts['count'].pct_change() * 100

    # Format year_week for better display
    weekly_counts['year_week_display'] = weekly_counts['year_week'].apply(
        lambda x: f"Y{x.split('-')[0]}_W{int(x.split('-')[1]):02d}" if '-' in str(x) else x
    )

    # Display key metrics
    st.markdown("#### Chỉ số thống kê theo tuần")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Số video trung bình/tuần",
                  value=f"{average_videos:,.0f}",
                  border=True,
                  )
    with col2:
        st.metric(label="Số video trung vị/tuần",
                  value=f"{median_videos:,.0f}",
                  border=True,
                  )
    with col3:
        st.metric(label="Tăng trưởng tổng thể",
                  value=f"{growth_rate:.1f}%",
                  delta=f"{int(last_4_weeks_avg - first_4_weeks_avg)}",
                  border=True,
                  help="So sánh số lượng video trung bình trong 4 tuần cuối cùng với 4 tuần đầu tiên trong tập dữ liệu đang phân tích"
                  )

    # Câu hỏi nghiên cứu: Biến động về số lượng video ẩm thực Việt Nam được đăng tải trên TikTok trong suốt 70 tuần qua diễn ra như thế nào?
    st.subheader(
        ":blue-background[:blue[Câu hỏi:]] Biến động về số lượng video ẩm thực Việt Nam được đăng tải trên TikTok trong suốt 70 tuần từ tập dữ liệu thu thập được diễn ra như thế nào?")

    # Create a line chart with trend line using Plotly
    fig = go.Figure()

    # Add actual values line
    fig.add_trace(go.Scatter(
        x=weekly_counts['year_week_display'],
        y=weekly_counts['count'],
        mode='lines+markers',
        name='Số lượng video theo tuần',
        line=dict(color='#2563EB', width=2),
        marker=dict(size=6),
        hovertemplate='<b>%{x}</b><br>Số lượng: %{y:,.0f}<extra></extra>'
    ))

    # Add 4-week moving average
    fig.add_trace(go.Scatter(
        x=weekly_counts['year_week_display'],
        y=weekly_counts['4_week_ma'],
        mode='lines',
        name='Trung bình động 4 tuần',
        line=dict(color='#FF5722', width=2, dash='dot'),
        hovertemplate='<b>%{x}</b><br>TB 4 tuần: %{y:.1f}<extra></extra>'
    ))

    # Add a trendline using linear regression
    x = np.arange(len(weekly_counts))
    y = weekly_counts['count']
    slope, intercept = np.polyfit(x, y, 1)
    trendline = slope * x + intercept

    fig.add_trace(go.Scatter(
        x=weekly_counts['year_week_display'],
        y=trendline,
        mode='lines',
        name='Xu hướng tổng thể',
        line=dict(color='green', width=2, dash='dash'),
        hovertemplate='<b>%{x}</b><br>Xu hướng: %{y:.1f}<extra></extra>'
    ))

    # Add highlight rectangles for specific periods
    holiday_periods = [
        {'start': 'Y2023_W51', 'end': 'Y2024_W02', 'label': 'Giáng sinh 2023'},
        {'start': 'Y2024_W50', 'end': 'Y2025_W01', 'label': 'Giáng sinh 2024'},
        {'start': 'Y2024_W07', 'end': 'Y2024_W10', 'label': 'Tết Nguyên Đán 2024'},
        {'start': 'Y2025_W04', 'end': 'Y2025_W07', 'label': 'Tết Nguyên Đán 2025'},
        {'start': 'Y2024_W39', 'end': 'Y2024_W42', 'label': 'Trung thu 2024'},
    ]

    for period in holiday_periods:
        if period['start'] in weekly_counts['year_week_display'].values:
            start_idx = weekly_counts[weekly_counts['year_week_display']
                                      == period['start']].index[0]
            end_idx = min(start_idx + 4, len(weekly_counts) - 1)
            if period['end'] in weekly_counts['year_week_display'].values:
                end_idx = weekly_counts[weekly_counts['year_week_display']
                                        == period['end']].index[0]

            fig.add_shape(
                type="rect",
                xref="x",
                yref="paper",
                x0=weekly_counts['year_week_display'].iloc[start_idx],
                x1=weekly_counts['year_week_display'].iloc[end_idx],
                y0=0,
                y1=1,
                fillcolor="rgba(255, 235, 59, 0.3)",
                line=dict(width=0),
            )

            fig.add_annotation(
                x=weekly_counts['year_week_display'].iloc[(
                    start_idx + end_idx)//2],
                y=1.04,
                xref="x",
                yref="paper",
                text=period['label'],
                showarrow=False,
                font=dict(size=12, color="#FF5722"),
            )

    # Identify peaks and troughs
    peaks = []
    troughs = []
    for i in range(1, len(weekly_counts)-1):
        if weekly_counts['count'].iloc[i] > weekly_counts['count'].iloc[i-1] and weekly_counts['count'].iloc[i] > weekly_counts['count'].iloc[i+1]:
            if weekly_counts['count'].iloc[i] > weekly_counts['count'].mean() + weekly_counts['count'].std():
                peaks.append(i)
        elif weekly_counts['count'].iloc[i] < weekly_counts['count'].iloc[i-1] and weekly_counts['count'].iloc[i] < weekly_counts['count'].iloc[i+1]:
            if weekly_counts['count'].iloc[i] < weekly_counts['count'].mean() - weekly_counts['count'].std():
                troughs.append(i)

    # Add annotations for significant peaks and troughs
    for peak_idx in peaks:
        fig.add_annotation(
            x=weekly_counts['year_week_display'].iloc[peak_idx],
            y=weekly_counts['count'].iloc[peak_idx],
            text="Đỉnh",
            showarrow=True,
            arrowhead=1,
            ax=0,
            ay=-40
        )

    for trough_idx in troughs:
        fig.add_annotation(
            x=weekly_counts['year_week_display'].iloc[trough_idx],
            y=weekly_counts['count'].iloc[trough_idx],
            text="Đáy",
            showarrow=True,
            arrowhead=1,
            ax=0,
            ay=40
        )

    # Update layout
    fig.update_layout(
        title=dict(
            text='Xu hướng số lượng video ẩm thực Việt Nam trên TikTok theo tuần',
            font=dict(size=22, color=DARK_GRAY),
            x=0,
            # y=0.95,
        ),
        xaxis_title='Tuần',
        yaxis_title='Số lượng video',
        hovermode="x unified",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        height=600,
    )

    # Show only every nth tick to avoid overcrowding
    n = max(1, len(weekly_counts) // 10)
    fig.update_xaxes(
        tickmode='array',
        tickvals=weekly_counts['year_week_display'][::n].tolist(),
        ticktext=weekly_counts['year_week_display'][::n].tolist(),
        tickangle=45
    )

    st.plotly_chart(fig, use_container_width=True)

    # Display YoY comparison if we have more than one year of data
    years = sorted(set([x.split('-')[0] if '-' in str(x) else x.split('_')[0].replace('Y', '')
                        for x in weekly_counts['year_week']]))
    if len(years) > 1:
        st.markdown("### So sánh theo năm")

        # Create a year-week pivot for comparison
        weekly_counts['year'] = weekly_counts['year_week'].apply(
            lambda x: x.split(
                '-')[0] if '-' in str(x) else x.split('_W')[0].replace('Y', '')
        )
        weekly_counts['week_num'] = weekly_counts['year_week'].apply(
            lambda x: int(
                x.split('-')[1]) if '-' in str(x) else int(x.split('_W')[1])
        )

        pivot_df = weekly_counts.pivot(
            index='week_num', columns='year', values='count').reset_index()

        yoy_fig = go.Figure()

        for year in years:
            if year in pivot_df.columns:
                yoy_fig.add_trace(go.Scatter(
                    x=pivot_df['week_num'],
                    y=pivot_df[year],
                    mode='lines+markers',
                    name=f'Năm {year}',
                    hovertemplate=f'Năm {year}<br>Tuần %{{x}}: %{{y:,.0f}} video<extra></extra>'
                ))

        yoy_fig.update_layout(
            title=dict(
                text='So sánh số lượng video ẩm thực theo tuần qua các năm',
                font=dict(size=22, color=DARK_GRAY),
                x=0,
                # y=0.95,
            ),
            xaxis_title='Tuần trong năm',
            yaxis_title='Số lượng video',
            hovermode="x unified",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            height=500,
        )

        st.plotly_chart(yoy_fig, use_container_width=True)

    # Add statistical comparison between specific time periods
    st.markdown("#### So sánh thống kê giữa các giai đoạn")

    # Helper function for extracting year and week from formatted strings
    def extract_year_week(year_week_str):
        """Extract year and week number from different format strings"""
        if isinstance(year_week_str, str):
            if '-' in year_week_str:  # Format "2023-52"
                parts = year_week_str.split('-')
                if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                    return int(parts[0]), int(parts[1])
            elif '_W' in year_week_str:  # Format "Y2023_W52"
                year_part = year_week_str.split('_W')[0].replace('Y', '')
                week_part = year_week_str.split('_W')[1]
                if year_part.isdigit() and week_part.isdigit():
                    return int(year_part), int(week_part)
        return None, None

    # Filter weekly data based on year and week range
    def filter_by_year_week(df, target_year, start_week, end_week):
        """Filter data for specific year and week range"""
        filtered_rows = []

        for _, row in df.iterrows():
            year, week = extract_year_week(row['year_week_display'])
            if year == target_year and start_week <= week <= end_week:
                filtered_rows.append(row)

        return pd.DataFrame(filtered_rows) if filtered_rows else pd.DataFrame(columns=df.columns)

    # Compare two periods and calculate statistics
    def compare_periods(period1_name, period1_data, period2_name, period2_data):
        """Calculate and compare statistics between two periods"""
        if period1_data.empty or period2_data.empty:
            return None

        period1_stats = {
            'mean': period1_data['count'].mean(),
            'median': period1_data['count'].median(),
            'total': period1_data['count'].sum(),
            'std': period1_data['count'].std(),
            'min': period1_data['count'].min(),
            'max': period1_data['count'].max(),
        }

        period2_stats = {
            'mean': period2_data['count'].mean(),
            'median': period2_data['count'].median(),
            'total': period2_data['count'].sum(),
            'std': period2_data['count'].std(),
            'min': period2_data['count'].min(),
            'max': period2_data['count'].max(),
        }

        # Calculate percentage difference
        if period1_stats['total'] > 0:
            percent_diff = ((period2_stats['total'] - period1_stats['total']) /
                            period1_stats['total'] * 100)
        else:
            percent_diff = 0

        return {
            'period1_name': period1_name,
            'period2_name': period2_name,
            'period1_stats': period1_stats,
            'period2_stats': period2_stats,
            'percent_diff': percent_diff
        }

    # Display period comparison in UI
    def display_period_comparison(period1_data, period2_data, period1_name, period2_name):
        """Display the comparison between two periods with charts and statistics"""
        if period1_data.empty or period2_data.empty:
            st.warning(
                f"Không đủ dữ liệu để so sánh {period1_name} và {period2_name}.")
            return

        comparison = compare_periods(
            period1_name, period1_data, period2_name, period2_data)

        # Display metrics in three columns
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(
                label=f"Tổng số video ({comparison['period1_name']})",
                value=f"{int(comparison['period1_stats']['total']):,}",
                border=True,
            )
        with col2:
            st.metric(
                label=f"Tổng số video ({comparison['period2_name']})",
                value=f"{int(comparison['period2_stats']['total']):,}",
                delta=f"{comparison['percent_diff']:.1f}%",
                border=True,
            )
        with col3:
            st.metric(
                label="Video trung bình mỗi tuần",
                value=f"{comparison['period1_stats']['mean']:.1f} → {comparison['period2_stats']['mean']:.1f}",
                border=True,
            )

        # Create butterfly chart comparison
        fig = go.Figure()

        # Extract week numbers from the display string (e.g., Y2023_W48 -> 48)
        def extract_week_number(year_week_str):
            if '_W' in year_week_str:
                return int(year_week_str.split('_W')[1])
            return 0

        # Get week numbers
        period1_data['week_num'] = period1_data['year_week_display'].apply(
            extract_week_number)
        period2_data['week_num'] = period2_data['year_week_display'].apply(
            extract_week_number)

        # Add data for first period (negative direction - old year)
        fig.add_trace(go.Bar(
            y=period1_data['week_num'],
            x=-period1_data['count'],  # Negative values for left side
            name=comparison['period1_name'],
            marker_color='rgb(55, 83, 109)',
            orientation='h',
            hovertemplate='<b>%{y}</b><br>Số lượng: %{customdata}<extra></extra>',
            # Store actual positive count for hover
            customdata=period1_data['count']
        ))

        # Add data for second period (positive direction - new year)
        fig.add_trace(go.Bar(
            y=period2_data['week_num'],
            x=period2_data['count'],  # Positive values for right side
            name=comparison['period2_name'],
            marker_color='rgb(26, 118, 255)',
            orientation='h',
            hovertemplate='<b>%{y}</b><br>Số lượng: %{x}<extra></extra>'
        ))

        # Find max value for symmetrical axes
        max_value = max(
            period1_data['count'].max() if not period1_data.empty else 0,
            period2_data['count'].max() if not period2_data.empty else 0
        )
        max_value = int(max_value * 1.1)  # Add 10% padding

        # Get unique week numbers for y-axis
        all_weeks = sorted(
            set(period1_data['week_num'].tolist() + period2_data['week_num'].tolist()))

        # Update layout
        fig.update_layout(
            title=f'So sánh số lượng video theo tuần: {period1_name} vs {period2_name}',
            title_font_size=20,
            title_font_color=DARK_GRAY,
            title_font_family="Arial",

            # Adjust height based on weeks
            height=max(500, len(all_weeks) * 30),
            barmode='relative',
            xaxis=dict(
                title='Số lượng video',
                zeroline=True,
                zerolinecolor='black',
                zerolinewidth=1
            ),
            yaxis=dict(
                title='Tuần',
                tickmode='array',
                tickvals=all_weeks,
                ticktext=[f"Tuần {w}" for w in all_weeks],
                autorange="reversed"  # Show weeks in ascending order from top to bottom
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="center",
                x=0.5
            )
        )

        # Create symmetric ticks with absolute values for both sides
        # Ensure reasonable number of ticks
        tick_step = max(10, max_value // 5)
        pos_ticks = list(range(0, max_value + 1, tick_step))  # Positive ticks
        # Negative ticks (excluding 0)
        neg_ticks = [-x for x in pos_ticks if x > 0]
        tick_vals = sorted(neg_ticks + [0] + pos_ticks)  # Combine and sort

        # Create tick text showing absolute values
        tick_text = [str(abs(x)) for x in tick_vals]

        # Set explicit range to ensure both sides are symmetric
        fig.update_xaxes(
            tickvals=tick_vals,
            ticktext=tick_text,
            range=[-max_value, max_value],
            zeroline=True,
            zerolinecolor='black',
            zerolinewidth=1
        )

        st.plotly_chart(fig, use_container_width=True)

        # Add statistical significance test
        if len(period1_data) >= 3 and len(period2_data) >= 3:
            import scipy.stats as stats
            t_stat, p_value = stats.ttest_ind(
                period1_data['count'],
                period2_data['count'],
                # Welch's t-test (doesn't assume equal variance)
                equal_var=False
            )

            st.write("### Kiểm định thống kê")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("t-value", f"{t_stat:.3f}", border=True)
            with col2:
                st.metric("p-value", f"{p_value:.4f}", border=True)

            if p_value < 0.05:
                st.success("Sự khác biệt có ý nghĩa thống kê (p < 0.05)")
            else:
                st.info("Sự khác biệt không có ý nghĩa thống kê (p >= 0.05)")

    # Create two tabs for the two comparisons
    tab1, tab2 = st.tabs(["Cuối năm 2023 vs 2024", "Đầu năm 2024 vs 2025"])

    with tab1:
        st.write(
            "So sánh 5 tuần cuối năm 2023 và 5 tuần cuối năm 2024 (loại bỏ tuần đầu tiên)")

        # Filter data for last 5 weeks of 2023 and 2024 (excluding the first week)
        end_2023_data = filter_by_year_week(weekly_counts, 2023, 48, 52)
        end_2024_data = filter_by_year_week(weekly_counts, 2024, 48, 52)

        # Display the comparison
        display_period_comparison(
            end_2023_data,
            end_2024_data,
            "Cuối năm 2023",
            "Cuối năm 2024"
        )

    with tab2:
        st.write(
            "So sánh 11 tuần đầu năm 2024 và 11 tuần đầu năm 2025 (loại bỏ tuần cuối cùng)")

        # Filter data for first 11 weeks of 2024 and 2025 (excluding the last week)
        start_2024_data = filter_by_year_week(weekly_counts, 2024, 1, 11)
        start_2025_data = filter_by_year_week(weekly_counts, 2025, 1, 11)

        # Display the comparison
        display_period_comparison(
            start_2024_data,
            start_2025_data,
            "Đầu năm 2024",
            "Đầu năm 2025"
        )

    # AI insights if available
    prompt = f"""
    Bạn là một chuyên gia phân tích dữ liệu. Dưới đây là thông tin về số lượng video ẩm thực Việt Nam trên TikTok theo thời gian:

    - Tổng số tuần phân tích: {total_weeks} tuần
    - Số lượng video trung bình mỗi tuần: {average_videos:.1f}
    - Số lượng video trung vị mỗi tuần: {median_videos:.1f}
    - Giá trị cao nhất: {max_videos} (vào tuần {weekly_counts.loc[weekly_counts['count'] == max_videos, 'year_week_display'].iloc[0]})
    - Giá trị thấp nhất: {min_videos} (vào tuần {weekly_counts.loc[weekly_counts['count'] == min_videos, 'year_week_display'].iloc[0]})
    - Tăng trưởng tổng thể: {growth_rate:.1f}% (so sánh 4 tuần đầu và 4 tuần cuối)

    Hãy phân tích xu hướng tổng thể của dữ liệu này và trả lời chi tiết các câu hỏi sau:
    1. Xu hướng tổng thể theo thời gian là gì? (tăng, giảm hay ổn định)
    2. Có những biến động đáng kể nào trong suốt thời gian phân tích không?
    3. Có thấy được tính mùa vụ hoặc chu kỳ trong dữ liệu không?
    4. Giải thích các nguyên nhân có thể dẫn đến những đỉnh cao hoặc điểm thấp trong dữ liệu.
    5. Dựa vào dữ liệu này, có thể dự đoán xu hướng tiếp theo không?

    Hãy giải thích chi tiết, đi sâu vào từng phân tích cụ thể.
    """

    # display_AI_generated_insights(
    #     prompt=prompt,
    #     api_key="AIzaSyBrTgG4YDzJMuK9WknMTbdnnoskSX1nvMY",
    #     print_to_console=False,
    #     expanded=True
    # )

# --------------------------------------------------------


@st.cache_data
def get_food_category_data(df: pd.DataFrame) -> Dict[str, Any]:
    all_foods = df['foods'].explode().dropna()
    food_counts = all_foods.value_counts()

    def identify_food_groups(food_counts):
        # Dictionary to store tokens for each food
        food_tokens = {}
        for food in food_counts.index:
            tokens = food.lower().split()
            food_tokens[food] = tokens

        # Common Vietnamese food prefixes that typically come first
        prefixes = {"mì", "bún", "cơm", "bánh", "chả",
                    "chân gà", "thịt", "cá", "hải", "phở", "phô"}

        # Track which foods have been processed and mappings
        food_to_group = {}
        food_groups = defaultdict(list)
        processed_foods = set()

        # Process each food
        for food in food_counts.index:
            if food in processed_foods:
                continue

            base_tokens = food_tokens[food]
            current_group = []

            # Find similar foods based on common words
            for other_food in food_counts.index:
                if other_food in processed_foods:
                    continue

                other_tokens = food_tokens[other_food]
                common_words = set(base_tokens) & set(other_tokens)

                # If at least 2 words are common, group these foods
                if len(common_words) >= 2:
                    current_group.append(other_food)
                    processed_foods.add(other_food)

            # Create a meaningful group name
            if current_group:
                # Collect all words from the foods in this group
                all_words = []
                original_phrases = []

                for group_food in current_group:
                    all_words.extend(food_tokens[group_food])
                    # Store original words with their order
                    for i in range(len(food_tokens[group_food]) - 1):
                        original_phrases.append(
                            f"{food_tokens[group_food][i]} {food_tokens[group_food][i+1]}")

                # Find most common words
                word_counts = pd.Series(all_words).value_counts()
                top_words = word_counts.head(2).index.tolist()

                # Determine correct word order
                if len(top_words) >= 2:
                    # Check if the two words appear together in original phrases
                    word_pair = f"{top_words[0]} {top_words[1]}"
                    reversed_pair = f"{top_words[1]} {top_words[0]}"

                    pair_count = sum(
                        1 for phrase in original_phrases if phrase == word_pair)
                    reversed_count = sum(
                        1 for phrase in original_phrases if phrase == reversed_pair)

                    # If prefix word is second, swap the order
                    if top_words[1] in prefixes and top_words[0] not in prefixes:
                        group_name = f"{top_words[1]} {top_words[0]}"
                    # Use the order that appears most in original phrases
                    elif reversed_count > pair_count:
                        group_name = reversed_pair
                    else:
                        group_name = word_pair
                else:
                    group_name = " ".join(top_words)

                # Map foods to group
                for group_food in current_group:
                    food_to_group[group_food] = group_name
                    food_groups[group_name].append(group_food)

        return food_groups, food_to_group

    # Generate food groups
    food_groups, food_to_group = identify_food_groups(food_counts)

    # Count occurrences for each group
    group_counts = {}
    for group_name, variants in food_groups.items():
        total_count = sum(food_counts[variant] for variant in variants)
        group_counts[group_name] = {
            'total_count': total_count,
            'variants': variants,
            'variant_counts': {variant: food_counts[variant] for variant in variants}
        }

    # Sort groups by total count
    sorted_groups = sorted(group_counts.items(),
                           key=lambda x: x[1]['total_count'], reverse=True)

    return {
        'food_groups': food_groups,
        'food_to_group': food_to_group,
        'group_counts': group_counts,
        'sorted_groups': sorted_groups,
        'food_counts': food_counts
    }


@st.cache_data
def prepare_category_details(category_name, category_data, food_counts) -> Dict[str, Any]:
    variants = sorted(
        category_data['variant_counts'].items(),
        key=lambda x: x[1],
        reverse=True
    )

    variant_df = pd.DataFrame(variants, columns=['variant', 'count'])
    total = variant_df['count'].sum()
    variant_df['percentage'] = variant_df['count'] / total * 100

    main_variants = variant_df[variant_df['percentage'] >= 5]
    other_variants = variant_df[variant_df['percentage'] < 5]

    if len(main_variants) > 10:
        main_variants = main_variants.head(10)
        other_variants = pd.concat([
            variant_df.iloc[10:],
            other_variants
        ])

    plot_data = main_variants.copy()

    if not other_variants.empty:
        other_sum = other_variants['count'].sum()
        other_row = pd.DataFrame({
            'variant': ['Các phân loại khác'],
            'count': [other_sum],
            'percentage': [other_sum / total * 100]
        })
        plot_data = pd.concat([plot_data, other_row])

    # Format the data for table view
    all_variants_df = pd.DataFrame(variants, columns=['Biến Thể', 'Số Lượng'])
    all_variants_df['Tỉ Lệ'] = all_variants_df['Số Lượng'] / \
        all_variants_df['Số Lượng'].sum() * 100
    all_variants_df['Tỉ Lệ'] = all_variants_df['Tỉ Lệ'].round(
        2).astype(str) + '%'

    return {
        'category_name': category_name,
        'total_count': category_data['total_count'],
        'num_variants': len(category_data['variants']),
        'plot_data': plot_data,
        'all_variants_df': all_variants_df
    }


def analyze_food_categories(df: pd.DataFrame) -> None:
    """Analyze and visualize food categories and their variants"""

    st.markdown("<h2 class='sub-header'>Phân Tích Món Ăn Theo Danh Mục</h2>",
                unsafe_allow_html=True)

    # Get processed food category data
    category_data = get_food_category_data(df)
    sorted_groups = category_data['sorted_groups']

    # Use fixed default values instead of slider
    default_count = 15
    extended_count = 20

    # Add a "Show More" checkbox to control display
    show_more = st.checkbox("Hiển thị thêm danh mục", value=False)

    # Determine how many categories to display based on checkbox
    display_count = extended_count if show_more else default_count
    display_categories = sorted_groups[:min(display_count, len(sorted_groups))]

    # Create overview bar chart of categories with proper capitalization
    category_names = [proper_capitalize(group[0])
                      for group in display_categories]
    category_values = [group[1]['total_count'] for group in display_categories]

    # Create a dataframe for better control over display
    chart_df = pd.DataFrame({
        'category': category_names,
        'count': category_values
    })

    # * Barchart thể hiện số lượng món ăn theo danh mục
    # Sort for horizontal bar chart (smallest to largest)
    chart_df = chart_df.sort_values('count', ascending=True)
    fig = px.bar(
        chart_df,
        x='count',
        y='category',
        orientation='h',
        labels={'count': 'Số lượng đề cập', 'category': 'Danh mục món ăn'},
    )
    # Improve text visibility by adjusting margins and spacing
    fig.update_layout(
        # Dynamic height based on categories
        height=max(500, 25 * len(display_categories)),
        # Increased left margin for category names
        margin=dict(l=250, r=50, t=50, b=50),
        yaxis=dict(
            tickfont=dict(size=12),  # Larger font for y-axis labels
            ticksuffix="   "  # Add padding after tick labels
        ),
        # Đặt tiêu đề cho biểu đồ
        title=dict(
            text=f'Top {len(display_categories)} Danh Mục Món Ăn Được Đề Cập Nhiều Nhất',
            font=dict(size=22, color=DARK_GRAY),
            x=0,     # Adjust horizontal position
            # y=0.95,  # Adjust vertical position
        ),
    )
    st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(
        spec=[3, 7], gap="small", border=True)
    with col1:
        # * Create detailed view for selected category
        st.subheader("Chi tiết danh mục món ăn")
        st.write("Chọn một danh mục để xem chi tiết của từng loại món ăn:")

        # Get top categories for selectbox
        # Always show top 15 in dropdown
        top_categories = sorted_groups[:default_count]

        # Convert category names to a more readable format for the selectbox with proper capitalization
        readable_categories = [
            f"{proper_capitalize(cat[0])} ({cat[1]['total_count']} đề cập)" for cat in top_categories]
        selected_category_index = st.selectbox(
            label="**Danh sách món ăn**",
            options=range(len(readable_categories)),
            format_func=lambda i: readable_categories[i]
        )

        # Get the selected category details
        selected_category = top_categories[selected_category_index]
        category_name = selected_category[0]
        category_details = prepare_category_details(
            category_name,
            selected_category[1],
            category_data['food_counts']
        )

        # Display category information with proper capitalization
        st.markdown(
            f"**Loại món: :blue[{proper_capitalize(category_details['category_name'])}]**")
        st.markdown(
            f"- Tổng số đề cập: {category_details['total_count']}")
        st.markdown(
            f"- Số lượng phân loại: {category_details['num_variants']}")
    with col2:
        # * Create pie chart for top variants
        # Modify pie chart to show more variants based on the same "show more" checkbox
        plot_data = category_details['plot_data'].copy()

        # Determine how many variants to show in the pie chart based on the checkbox
        max_variants = extended_count if show_more else default_count

        # If we have more variants than our display limit, group the rest
        if len(plot_data) > max_variants and 'Các phân loại khác' not in plot_data['variant'].values:
            main_variants = plot_data.iloc[:max_variants-1].copy()
            other_variants = plot_data.iloc[max_variants-1:].copy()

            other_sum = other_variants['count'].sum()
            other_pct = other_variants['percentage'].sum()

            other_row = pd.DataFrame({
                'variant': ['Các phân loại khác'],
                'count': [other_sum],
                'percentage': [other_pct]
            })

            plot_data = pd.concat([main_variants, other_row])
        elif len(plot_data) > max_variants:
            plot_data = plot_data.iloc[:max_variants]

        # Piechart hiển thị tỉ lệ các món ăn trong danh mục
        # Apply capitalization to variant names if they're not "Các phân loại khác"
        plot_data['variant'] = plot_data['variant'].apply(
            lambda x: proper_capitalize(x) if x != "Các phân loại khác" else x
        )
        fig = px.pie(
            plot_data,
            values='count',
            names='variant',
            hover_data=['percentage']
        )
        # Improve text visibility in pie chart
        fig.update_traces(
            textposition='inside',
            textinfo='percent+label',
            hovertemplate='<b>%{label}</b><br>Số lượng: %{value}<br>Tỉ lệ: %{percent}<extra></extra>',
            textfont=dict(size=11)  # Slightly larger text font
        )
        # Adjust pie chart layout for better text visibility
        fig.update_layout(
            height=450,  # Taller pie chart
            margin=dict(t=50, b=50, l=20, r=20),
            legend=dict(
                font=dict(size=12),  # Larger legend font
                orientation="v",  # Vertical legend
                yanchor="top",
                y=1.0,
                xanchor="right",
                x=1.1
            ),
            # Đặt tiêu đề cho biểu đồ
            title=dict(
                text=f'Phân bố thức ăn trong món {proper_capitalize(category_details["category_name"])}',
                font=dict(size=22, color=DARK_GRAY),
                x=0,     # Adjust horizontal position
                # y=0.95,  # Adjust vertical position
            ),
        )
        st.plotly_chart(fig, use_container_width=True)

    # Show table of all variants with proper capitalization
    with st.expander("Xem chi tiết từng phân loại"):
        all_variants_df = category_details['all_variants_df'].copy()
        # Apply proper capitalization to the "Biến Thể" column
        all_variants_df["Biến Thể"] = all_variants_df["Biến Thể"].apply(
            proper_capitalize)

        # Show top 15 by default, with option to show all
        show_all_variants = st.checkbox(
            "Hiển thị tất cả phân loại", value=False)
        if not show_all_variants:
            display_df = all_variants_df.head(default_count)
            st.dataframe(display_df, use_container_width=True)
            if len(all_variants_df) > default_count:
                st.text(
                    f"Hiển thị {default_count}/{len(all_variants_df)} phân loại. Chọn 'Hiển thị tất cả phân loại' để xem thêm.")
        else:
            st.dataframe(all_variants_df, use_container_width=True)


# -------------------------------------------------------------
@st.cache_data
def get_location_data(df, city_list=None):
    """Process location data for visualization with optional city filtering"""
    # Convert city list to lowercase for case-insensitive matching
    city_list = [city.lower() for city in city_list]

    # Standardize city data with filtering
    city_counts = df['city_std'].explode().dropna().str.lower()
    filtered_cities = city_counts[city_counts.isin(city_list)]
    city_data = filtered_cities.value_counts().reset_index()
    city_data.columns = ['city', 'count']

    # Create district data with city information - filter out null districts
    district_city_data = df[['city_std', 'district_std']].explode(
        'district_std').dropna()

    # Additional filter to ensure both city and district are non-null
    district_city_data = district_city_data[
        (district_city_data['city_std'].notna()) &
        (district_city_data['district_std'].notna()) &
        (district_city_data['district_std'] != 'null') &
        (district_city_data['district_std'] != '')
    ]

    hcm_districts = [
        'quận 1', 'quận 2', 'quận 3', 'quận 4', 'quận 5',
        'quận 6', 'quận 7', 'quận 8', 'quận 9', 'quận 10',
        'quận 11', 'quận 12', 'thủ đức', 'bình thạnh', 'phú nhuận',
        'gò vấp', 'tân bình', 'tân phú', 'bình tân'
    ]

    hanoi_districts = [
        'ba đình', 'hoàn kiếm', 'hai bà trưng', 'đống đa', 'cầu giấy',
        'thanh xuân', 'tây hồ', 'hà đông', 'long biên', 'bắc từ liêm',
        'nam từ liêm', 'hoàng mai'
    ]

    # Apply the district corrections - create a copy first to avoid SettingWithCopyWarning
    district_city_data = district_city_data.copy()

    # For visualization only: correct city assignments based on district
    for idx, row in district_city_data.iterrows():
        district = row['district_std'].lower() if isinstance(
            row['district_std'], str) else ""

        # Correct HCM districts
        if district in hcm_districts:
            district_city_data.at[idx, 'city_std'] = 'hồ chí minh'

        # Correct Hanoi districts
        elif district in hanoi_districts:
            district_city_data.at[idx, 'city_std'] = 'hà nội'

    # Filter to only include districts from our selected cities
    district_city_data = district_city_data[
        district_city_data['city_std'].str.lower().isin(city_list)
    ]

    # Create district data with city hierarchy for treemap
    district_data_with_city = district_city_data.groupby(
        ['city_std', 'district_std']
    ).size().reset_index(name='count')

    # Make sure city names are properly capitalized for display
    city_data['city'] = city_data['city'].str.title()
    district_data_with_city['city_std'] = district_data_with_city['city_std'].str.title(
    )
    district_data_with_city['district_std'] = district_data_with_city['district_std'].str.title(
    )

    return {
        'city_data': city_data,
        'district_data_with_city': district_data_with_city
    }


def analyze_geospatial_distribution(df: pd.DataFrame) -> None:
    """Analyze and visualize geographical distribution of food mentions with predefined cities"""
    st.markdown("<h2 class='sub-header'>Phân Bố Địa Lý</h2>",
                unsafe_allow_html=True)

    # *--------------------------------------------------------*
    # *__________________[ Chuẩn bị dữ liệu ]__________________*
    # *--------------------------------------------------------*
    # Define list of cities to include
    predefined_cities = [
        "hà nội", "hồ chí minh", "sài gòn", "nha trang", "đà nẵng",
        "huế", "cần thơ", "hải phòng", "đà lạt", "vũng tàu",
        "biên hòa", "quy nhơn", "buôn ma thuột", "thái nguyên", "vinh",
        "hạ long", "phan thiết", "long xuyên", "việt trì", "thanh hóa",
        "hòa bình", "mỹ tho", "rạch giá", "cam ranh", "đồng hới",
        "tuy hòa", "hà tĩnh", "pleiku", "nam định", "bắc ninh",
        "thái bình", "ninh bình", "cao bằng", "lạng sơn", "tuyên quang",
        "yên bái", "lào cai", "điện biên phủ", "sơn la", "hải dương",
        "hưng yên", "phủ lý", "bắc giang", "lạng sơn", "móng cái",
        "uông bí", "cẩm phả", "bắc kạn", "sapa", "tam đảo",
        "hà giang", "lai châu", "quảng ninh", "hà nam", "quảng ngãi",
        "tam kỳ", "hội an", "kon tum", "gia nghĩa", "buôn hồ",
        "bảo lộc", "bến tre", "trà vinh", "cao lãnh", "sa đéc",
        "vĩnh long", "sóc trăng", "bạc liêu", "cà mau", "hà tiên",
        "tân an", "gò công", "châu đốc", "tây ninh", "thủ dầu một",
        "đồng xoài", "phan rang-tháp chàm", "bà rịa", "thuận an", "dĩ an"
    ]

    # Get location data with custom city filtering
    location_data = get_location_data(df, city_list=predefined_cities)
    city_data = location_data['city_data']
    district_data_with_city = location_data['district_data_with_city']

    # *--------------------------------------------------------*
    # *______________[ Phân tích theo thành phố ]______________*
    # *--------------------------------------------------------*
    if city_data.empty:
        st.warning("Không tìm thấy dữ liệu cho các thành phố đã chọn!")
        return

    # * Barchart thể hiện số lượng món ăn theo thành phố/tỉnh
    # Sort by count (descending) then take only top 10
    sorted_city_data = city_data.sort_values('count', ascending=False).head(10)
    # Re-sort for display (ascending for horizontal bar chart)
    sorted_city_data = sorted_city_data.sort_values('count', ascending=True)

    # Create visualization
    fig = px.bar(
        sorted_city_data, x='count', y='city', orientation='h',
        labels={'count': 'Số lượng đề cập', 'city': 'Thành phố/Tỉnh'},
    )
    fig.update_layout(
        xaxis_title="Số lượng đề cập",
        yaxis_title="Tỉnh/Thành phố",
        height=400,  # Fixed height for top 10
        # Đặt tiêu đề cho biểu đồ
        title=dict(
            text='Top 10 tỉnh/thành phố có nhiều đề cập nhất',
            font=dict(size=22, color=DARK_GRAY),
            x=0,     # Adjust horizontal position
            # y=0.95,  # Adjust vertical position
        ),
    )
    st.plotly_chart(fig, use_container_width=True)

    # *--------------------------------------------------------*
    # *_____________[ Phân tích theo quận/huyện ]______________*
    # *--------------------------------------------------------*
    # * Treemap hiển thị phân bố địa điểm theo thành phố và quận/huyện
    # Prepare data for hierarchical treemap
    if district_data_with_city.empty:
        st.warning("Không tìm thấy dữ liệu cho các quận/huyện đã chọn!")
        return

    # Định nghĩa một số khu vực ẩm thực phổ biến theo các quận/huyện
    vibrant_culinary_neighborhoods = {
        "Quận 1": ["Hẻm ăn vặt 76", "Chợ đêm Tân Định", "Phố ẩm thực Cô Giang"],
        "Quận 10": ["Phố ẩm thực Hồ Thị Kỷ"],
        "Quận 3": ["Phố ẩm thực Nguyễn Thượng Hiền", "Hồ Con Rùa"],
        "Quận 4": ["Hẻm 200 Xóm Chiếu", "Khu Ẩm Thực Chợ 200"],
        "Quận 11": ["Khu sủi cảo Hà Tôn Quyền", "Chợ Thái Bình"],
        "Tân Bình": ["Chợ Bà Hoa"],

        "Hoàn Kiếm": ["Phố Tống Duy Tân", "Phố Hàng Buồm", "Chợ Đồng Xuân", "Phố bia Tạ Hiện",
                      "Chợ Đồng Xuân"],
        "Hà Đông": ["Phố Tô Hiệu", "Ngõ Ao Sen"],
        "Cầu Giấy": ["Làng Cốm Vòng"],
        "Ba Đình": ["Phố phở cuốn Ngũ Xá", "Phố bít tết Hòe Nhai", "Chợ Thành Công"],
        "Nam Từ Liêm": ["Ngõ 67 chợ Phùng Khoang"],
        "Tây Hồ": ["Phố ốc Hồ Tây"],
    }

    # Get only districts for the top 10 cities
    top_10_cities = sorted_city_data['city'].tolist()
    filtered_district_data = district_data_with_city[
        district_data_with_city['city_std'].isin(top_10_cities)
    ]
    # Create a copy to avoid SettingWithCopyWarning
    filtered_district_data = filtered_district_data.copy()
    filtered_district_data['city_std'] = filtered_district_data['city_std'].apply(
        proper_capitalize)
    filtered_district_data['district_std'] = filtered_district_data['district_std'].apply(
        proper_capitalize)

    # Add culinary regions for hover text
    filtered_district_data['culinary_info'] = filtered_district_data['district_std'].apply(
        lambda x: ", ".join(
            vibrant_culinary_neighborhoods.get(x, ["Không có dữ liệu"]))
        if x in vibrant_culinary_neighborhoods else "Không có dữ liệu"
    )

    # Create custom text that includes culinary areas
    def create_display_text(row):
        district = row['district_std']
        count = row['count']
        culinary_areas = vibrant_culinary_neighborhoods.get(district, [])

        template = f"<b>{district}</b><br>Số lượng: {count}"

        # Format text with the district name, count, and culinary areas
        if culinary_areas and culinary_areas[0] != "Không có dữ liệu":
            culinary_areas_str = "<br>• ".join(culinary_areas)
            # return f"<b>{district}</b><br>Số lượng: {count}<br>{culinary_areas_str}"
            template += f"<br>Khu vực ẩm thực nổi tiếng:<br>• {culinary_areas_str}"
        return template

    # Add the custom text to the dataframe
    filtered_district_data['display_text'] = filtered_district_data.apply(
        create_display_text, axis=1)

    # Create treemap with city -> district hierarchy
    fig = px.treemap(
        filtered_district_data,
        path=['city_std', 'district_std'],  # Hierarchical path
        values='count',
        color='count',
        color_continuous_scale=[[0, 'rgb(0,68,137)'], [0.5, 'rgb(0,142,171)'], [
            1, 'rgb(0,204,150)']],
        # Include both for hover and text display
        custom_data=['culinary_info', 'display_text']
    )
    # Improve treemap appearance
    fig.update_traces(
        hovertemplate='<b>%{label}</b><br>Số lượng: %{value}<br>Khu vực ẩm thực: %{customdata[0]}<extra></extra>',
        # hovertemplate="",
        # Use the custom text that includes culinary areas
        texttemplate='%{customdata[1]}',
    )
    fig.update_layout(
        height=700,  # Larger height for better visibility
        margin=dict(t=75, l=25, r=25, b=25),
        # Đặt tiêu đề cho biểu đồ
        title=dict(
            text='Phân bố địa điểm theo Top 10 thành phố và quận/huyện',
            font=dict(size=26, color=DARK_GRAY),
            x=0,     # Adjust horizontal position
            # y=0.95,  # Adjust vertical position
        ),
    )
    st.plotly_chart(fig, use_container_width=True)

    # *--------------------------------------------------------*
    # *_______________[ Các câu hỏi nghiên cứu ]_______________*
    # *--------------------------------------------------------*
    # ['Hà Nội' 'Hồ Chí Minh' 'Hải Phòng' 'Đà Lạt' 'Vũng Tàu' 'Cần Thơ'
    # 'Nha Trang' 'Huế' 'Đà Nẵng' 'Phan Thiết' 'Tây Ninh' 'Hạ Long' 'Cà Mau'
    # 'Thái Bình' 'Lào Cai' 'Hà Giang' 'Mỹ Tho' 'Trà Vinh' 'Lạng Sơn'
    # 'Bắc Ninh' 'Cao Bằng' 'Biên Hòa' 'Long Xuyên' 'Bến Tre' 'Hội An'
    # 'Hà Tiên' 'Quảng Ngãi' 'Nam Định' 'Quy Nhơn' 'Sóc Trăng' 'Sapa'
    # 'Châu Đốc' 'Quảng Ninh' 'Bạc Liêu' 'Hà Tĩnh' 'Ninh Bình' 'Hải Dương'
    # 'Thái Nguyên' 'Rạch Giá' 'Gò Công' 'Vĩnh Long' 'Bắc Kạn' 'Hà Nam'
    # 'Sơn La' 'Pleiku' 'Buôn Ma Thuột' 'Cẩm Phả' 'Bảo Lộc' 'Tam Đảo' 'Sa Đéc'
    # 'Tuy Hòa' 'Vinh' 'Lai Châu' 'Hưng Yên' 'Bắc Giang']
    # Câu hỏi nghiên cứu: Mức độ tập trung của video ở Hà Nội và Thành phố Hồ Chí Minh có cao hơn đáng kể và có ý nghĩa thống kê so với các tỉnh/thành phố khác không?

    st.subheader(
        ":blue-background[:blue[Câu hỏi:]] Mức độ tập trung của video ở Hà Nội và Thành phố Hồ Chí Minh có cao hơn đáng kể và có ý nghĩa thống kê so với các tỉnh/thành phố khác không?")

    # Tạo các nhóm để phân tích
    # Standardize Hanoi and HCMC names for consistent grouping
    city_data_copy = city_data.copy()
    hanoi_hcmc = ['Hà Nội', 'Hồ Chí Minh']
    # print(city_data_copy['city'].unique())
    city_data_copy['group'] = city_data_copy['city'].apply(
        lambda x: 'Hà Nội & TP.HCM' if x.lower() in [c.lower(
        ) for c in hanoi_hcmc] else 'Các tỉnh/thành phố khác'
    )

    # Tính toán thống kê cơ bản
    group_stats = city_data_copy.groupby('group')['count'].agg(
        ['sum', 'count']).reset_index()
    total_mentions = group_stats['sum'].sum()
    group_stats['percentage'] = (
        group_stats['sum'] / total_mentions * 100).round(2)

    # Hiển thị thông tin thống kê
    col1, col2 = st.columns(spec=[5, 5], gap="medium")

    with col1:
        st.write("#### Số liệu thống kê theo nhóm")
        st.dataframe(
            data=group_stats.rename(columns={
                'group': 'Nhóm',
                'sum': 'Tổng số đề cập',
                'count': 'Số lượng thành phố/tỉnh',
                'percentage': 'Tỉ lệ đề cập (%)'
            }),
            use_container_width=True,
            hide_index=True
        )

        # Tính tỷ lệ tập trung
        if len(group_stats) >= 2:
            try:
                hanoi_hcmc_stats = group_stats[group_stats['group']
                                               == 'Hà Nội & TP.HCM'].iloc[0]
                other_cities_stats = group_stats[group_stats['group']
                                                 != 'Hà Nội & TP.HCM'].iloc[0]

                concentration_ratio = hanoi_hcmc_stats['sum'] / \
                    other_cities_stats['sum']

                st.metric(
                    label="⚖️ Tỷ lệ tập trung (Hà Nội & TP.HCM so với các tỉnh/thành phố khác)",
                    value=f"{concentration_ratio:.2f} : 1",
                    delta=f"{(hanoi_hcmc_stats['sum'] - other_cities_stats['sum']) / other_cities_stats['sum']:.2%}",
                    help="Tỷ lệ này cho thấy số lượng đề cập ở Hà Nội và TP.HCM so với các tỉnh/thành phố khác.",
                    border=True
                )
            except (IndexError, ZeroDivisionError):
                st.warning("Không đủ dữ liệu để tính tỷ lệ tập trung")

        # Tiến hành kiểm định thống kê
        st.write("#### Kiểm định thống kê")  # Mann-Whitney U test

        # Chuẩn bị dữ liệu cho kiểm định
        hanoi_hcmc_cities = [city.lower() for city in hanoi_hcmc]
        group1 = city_data_copy[city_data_copy['city'].str.lower().isin(
            hanoi_hcmc_cities)]['count']
        group2 = city_data_copy[~city_data_copy['city'].str.lower().isin(
            hanoi_hcmc_cities)]['count']

        # Kiểm tra nếu có đủ dữ liệu để thực hiện kiểm định
        if len(group1) > 0 and len(group2) > 0:

            # Thực hiện kiểm định Mann-Whitney (phi tham số) vì phân phối có thể không chuẩn
            stat, p_value = stats.mannwhitneyu(
                group1, group2, alternative='greater')

            st.metric("p-value", f"{p_value:.4f}", border=True)

            # Hiển thị kết quả
            alpha = 0.05
            if p_value < alpha:
                st.success(f"**Kết luận**: Có ý nghĩa thống kê (p < {alpha})")
                st.write(
                    "Số lượng đề cập ở Hà Nội và TP.HCM cao hơn đáng kể so với các tỉnh/thành phố khác một cách có ý nghĩa thống kê.")
            else:
                st.info(
                    f"**Kết luận**: Không có ý nghĩa thống kê (p ≥ {alpha})")
                st.write(
                    "Không có bằng chứng thống kê cho thấy số lượng đề cập ở Hà Nội và TP.HCM cao hơn đáng kể so với các tỉnh/thành phố khác.")
        else:
            st.warning("Không đủ dữ liệu để thực hiện kiểm định thống kê")

    with col2:
        # Biểu đồ tròn so sánh tỷ lệ
        fig = px.pie(
            group_stats,
            values='sum',
            names='group',
            title='Tỷ lệ đề cập theo nhóm',
            color='group',
            color_discrete_map={
                'Hà Nội & TP.HCM': '#2563EB',
                'Các tỉnh/thành phố khác': '#60A5FA'
            },
            hole=0.4
        )
        fig.update_traces(
            textposition='inside',
            textinfo='percent+label',
            hovertemplate='<b>%{label}</b><br>Số lượng: %{value}<br>Tỉ lệ: %{percent}<extra></extra>',
        )
        fig.update_layout(
            title_font_size=20,
            title_font_color=DARK_GRAY,
            title_font_family="Arial",
        )
        st.plotly_chart(fig, use_container_width=True)

    # Câu hỏi nghiên cứu: Miền nào (Bắc, Trung, Nam) là khu vực đóng góp số lượng video ẩm thực lớn nhất trên TikTok trong giai đoạn nghiên cứu, và liệu sự chiếm ưu thế về số lượng video này có ý nghĩa thống kê so với hai miền còn lại không?
    city_to_region = {
        'Hà Nội': 'Miền Bắc',
        'Hồ Chí Minh': 'Miền Nam',
        'Hải Phòng': 'Miền Bắc',
        'Đà Lạt': 'Miền Trung',
        'Vũng Tàu': 'Miền Nam',
        'Cần Thơ': 'Miền Nam',
        'Nha Trang': 'Miền Trung',
        'Huế': 'Miền Trung',
        'Đà Nẵng': 'Miền Trung',
        'Phan Thiết': 'Miền Trung',
        'Tây Ninh': 'Miền Nam',
        'Hạ Long': 'Miền Bắc',
        'Cà Mau': 'Miền Nam',
        'Thái Bình': 'Miền Bắc',
        'Lào Cai': 'Miền Bắc',
        'Hà Giang': 'Miền Bắc',
        'Mỹ Tho': 'Miền Nam',
        'Trà Vinh': 'Miền Nam',
        'Lạng Sơn': 'Miền Bắc',
        'Bắc Ninh': 'Miền Bắc',
        'Cao Bằng': 'Miền Bắc',
        'Biên Hòa': 'Miền Nam',
        'Long Xuyên': 'Miền Nam',
        'Bến Tre': 'Miền Nam',
        'Hội An': 'Miền Trung',
        'Hà Tiên': 'Miền Nam',
        'Quảng Ngãi': 'Miền Trung',
        'Nam Định': 'Miền Bắc',
        'Quy Nhơn': 'Miền Trung',
        'Sóc Trăng': 'Miền Nam',
        'Sapa': 'Miền Bắc',  # Thuộc tỉnh Lào Cai
        'Châu Đốc': 'Miền Nam',  # Thuộc tỉnh An Giang
        'Quảng Ninh': 'Miền Bắc',
        'Bạc Liêu': 'Miền Nam',
        'Hà Tĩnh': 'Miền Trung',
        'Ninh Bình': 'Miền Bắc',
        'Hải Dương': 'Miền Bắc',
        'Thái Nguyên': 'Miền Bắc',
        'Rạch Giá': 'Miền Nam',
        'Gò Công': 'Miền Nam',  # Thuộc tỉnh Tiền Giang
        'Vĩnh Long': 'Miền Nam',
        'Bắc Kạn': 'Miền Bắc',
        'Hà Nam': 'Miền Bắc',
        'Sơn La': 'Miền Bắc',
        'Pleiku': 'Miền Trung',
        'Buôn Ma Thuột': 'Miền Trung',
        'Cẩm Phả': 'Miền Bắc',
        'Bảo Lộc': 'Miền Trung',
        'Tam Đảo': 'Miền Bắc',  # Thuộc tỉnh Vĩnh Phúc
        'Sa Đéc': 'Miền Nam',  # Thuộc tỉnh Đồng Tháp
        'Tuy Hòa': 'Miền Trung',
        'Vinh': 'Miền Trung',
        'Lai Châu': 'Miền Bắc',
        'Hưng Yên': 'Miền Bắc',
        'Bắc Giang': 'Miền Bắc'
    }

    # Research question
    st.subheader(
        ":blue-background[:blue[Câu hỏi:]] Miền nào (Bắc, Trung, Nam) là khu vực đóng góp số lượng video ẩm thực lớn nhất trên TikTok? Trong phạm vi mỗi miền, tỉnh/thành phố nào có sự đóng góp nhiều nhất về số lượng video?")
    # Answer
    with st.expander(label=":green[**:material/check_box: Trả lời**]", expanded=False):
        st.markdown(f"""
            **Tổng quan:**
            Phân tích dữ liệu về xu hướng ẩm thực Việt Nam trên TikTok theo tiêu chí địa lý cho thấy sự tập trung đáng kể ở một số khu vực nhất định trong giai đoạn nghiên cứu.

            **Kết quả chính:**

            1.  **Tập trung ở các thành phố lớn:** Hà Nội và Thành phố Hồ Chí Minh là hai địa phương được đề cập/xuất hiện nhiều nhất trong tập dữ liệu, phản ánh vai trò trung tâm của hai đô thị này trong hoạt động sản xuất và tiêu thụ nội dung ẩm thực trên TikTok.
            2.  **Phân bố theo 3 miền:** Khi phân chia theo ba miền địa lý chính, Miền Nam và Miền Bắc chiếm tỷ trọng đề cập vượt trội, với tổng cộng khoảng 93% số lượng video/đề cập. Miền Trung có số lượng đề cập thấp nhất.
            3.  **Sự ảnh hưởng của thành phố trung tâm trong mỗi miền:** Tỷ lệ đề cập trong mỗi miền (Bắc và Nam) bị chi phối mạnh mẽ bởi thành phố trung tâm của miền đó. Cụ thể, Hà Nội đóng góp tới 85% số đề cập trong Miền Bắc và Thành phố Hồ Chí Minh đóng góp tới 85% số đề cập trong Miền Nam.
            4.  **Đặc điểm của Miền Trung:** Trái ngược với Miền Bắc và Miền Nam, số lượng đề cập đến các tỉnh thành trong Miền Trung có sự phân bố đồng đều hơn giữa các địa phương, không quá phụ thuộc vào một vài thành phố dẫn đầu. Các địa phương xuất hiện nhiều nhất tại Miền Trung chủ yếu là các thành phố du lịch trọng điểm như Đà Lạt, Nha Trang, Huế, Đà Nẵng.

            **Nhận xét và Hàm ý Chiến lược:**

            Sự phân bố địa lý này gợi ý rằng trong khi Hà Nội và Thành phố Hồ Chí Minh là những trung tâm nội dung ẩm thực lớn và sầm uất, chúng cũng đồng thời là những thị trường có độ cạnh tranh rất cao.

            Đối với các nhà sáng tạo nội dung, dữ liệu cho thấy một hướng đi tiềm năng: thay vì cố gắng cạnh tranh trực tiếp trong những thị trường đã bão hòa như Hà Nội và TP. Hồ Chí Minh, việc tập trung khai thác các **thị trường ngách tại các thành phố du lịch** (đặc biệt là ở Miền Trung) có thể là chiến lược hiệu quả. Tại những địa điểm này, sự cạnh tranh có thể ít gay gắt hơn, và nhà sáng tạo có cơ hội xây dựng một tệp người xem/khán giả riêng, quan tâm đến ẩm thực đặc trưng hoặc trải nghiệm ăn uống tại các điểm du lịch.
            """)

    # Thêm cột Region vào city_data
    city_data_region = city_data.copy()
    city_data_region['region'] = city_data_region['city'].apply(
        lambda x: city_to_region.get(
            x, "Khác") if x in city_to_region else "Khác"
    )

    # Lọc ra các thành phố không có trong city_to_region
    unknown_cities = city_data_region[city_data_region['region']
                                      == "Khác"]['city'].tolist()
    if unknown_cities:
        with st.expander("Các thành phố chưa được phân loại"):
            st.write(", ".join(unknown_cities))

    # Loại bỏ các thành phố không có trong city_to_region
    city_data_region = city_data_region[city_data_region['region'] != "Khác"]

    # Tính tổng số lượng theo miền
    region_stats = city_data_region.groupby('region')['count'].agg(
        ['sum', 'count', 'mean']).reset_index()
    region_stats.columns = ['Miền', 'Tổng số đề cập',
                            'Số tỉnh/thành phố', 'Trung bình đề cập/thành phố']
    region_stats = region_stats.sort_values('Tổng số đề cập', ascending=False)

    # Hiển thị thông tin thống kê
    col1, col2 = st.columns(spec=[5, 5], gap="large")

    with col1:
        st.write("#### Số liệu thống kê theo miền")
        # Format 'Trung bình đề cập/thành phố' to round to 2 decimal places
        region_stats['Trung bình đề cập/thành phố'] = region_stats['Trung bình đề cập/thành phố'].round(
            2)
        st.dataframe(
            region_stats,
            use_container_width=True,
            hide_index=True
        )

        # Tính toán tỷ lệ đề cập giữa các miền
        total_mentions = region_stats['Tổng số đề cập'].sum()
        region_stats['Tỉ lệ (%)'] = (
            region_stats['Tổng số đề cập'] / total_mentions * 100).round(2)

        # Tạo biểu đồ tròn theo tỷ lệ
        pie_fig = px.pie(
            region_stats,
            values='Tổng số đề cập',
            names='Miền',
            title='Tỷ lệ đề cập theo miền',
            color='Miền',
            color_discrete_map={
                'Miền Bắc': '#2563EB',
                'Miền Trung': '#FF5722',
                'Miền Nam': '#10B981'
            },
            hole=0.4
        )
        pie_fig.update_traces(
            textposition='inside',
            textinfo='percent+label',
            hovertemplate='<b>%{label}</b><br>Số lượng: %{value}<br>Tỉ lệ: %{percent}<extra></extra>'
        )
        pie_fig.update_layout(
            title_font_size=20,
            title_font_color=DARK_GRAY,
            title_font_family="Arial",
            height=400
        )
        st.plotly_chart(pie_fig, use_container_width=True)

    with col2:
        # Kiểm định thống kê
        st.write("#### Kiểm định thống kê")

        # Chi-square test to see if distribution is uniform across regions
        observed = region_stats['Tổng số đề cập'].values
        expected = [total_mentions/len(observed)] * len(observed)
        chi2_stat, p_value = stats.chisquare(observed, expected)

        st.metric("Chi-square statistic", f"{chi2_stat:.2f}", border=True)
        st.metric("p-value", f"{p_value:.4f}", border=True)

        # Hiển thị kết luận
        alpha = 0.05
        if p_value < alpha:
            st.success(
                f"**Kết luận**: Có sự khác biệt có ý nghĩa thống kê giữa các miền (p < {alpha})")

            # Tìm miền chiếm ưu thế
            dominant_region = region_stats.iloc[0]['Miền']
            st.write(
                f"**{dominant_region}** chiếm ưu thế với **{region_stats.iloc[0]['Tỉ lệ (%)']:.2f}%** số lượng đề cập.")
        else:
            st.info(
                f"**Kết luận**: Không có sự khác biệt có ý nghĩa thống kê giữa các miền (p ≥ {alpha})")

        # Phân tích chi tiết hơn: top 5 tỉnh/thành phố mỗi miền
    st.write("#### Top tỉnh/thành phố đóng góp nhiều nhất theo từng miền")

    region_tabs = st.tabs(
        [f"Miền {region}" for region in region_stats['Miền']])

    for i, region in enumerate(region_stats['Miền']):
        with region_tabs[i]:
            # Lọc dữ liệu cho miền hiện tại
            region_cities = city_data_region[city_data_region['region'] == region]
            top_cities = region_cities.sort_values(
                'count', ascending=False).head(10)

            # Trực quan hóa top thành phố của miền
            fig = px.bar(
                top_cities,
                y='city',
                x='count',
                orientation='h',
                title=f'Top 10 tỉnh/thành phố đóng góp nhiều nhất ở {region}',
                labels={'count': 'Số lượng đề cập', 'city': 'Tỉnh/Thành phố'},
                color_discrete_sequence=['#60A5FA'] if region == 'Miền Bắc' else (
                    ['#FF8A65'] if region == 'Miền Trung' else ['#34D399'])
            )
            fig.update_layout(
                height=400,
                xaxis_title="Số lượng đề cập",
                yaxis_title="",

                title_font_size=20,
                title_font_color=DARK_GRAY,
                title_font_family="Arial",
            )
            st.plotly_chart(fig, use_container_width=True)

            # Hiển thị tỉ lệ đóng góp của từng thành phố trong miền
            total_region_count = region_cities['count'].sum()
            top_cities['contribution'] = (
                top_cities['count'] / total_region_count * 100).round(2)

            st.write(f"##### Tỉ lệ đóng góp của top thành phố trong {region}")
            contribution_df = top_cities[['city', 'count', 'contribution']].rename(
                columns={'city': 'Tỉnh/Thành phố', 'count': 'Số lượng đề cập', 'contribution': 'Tỉ lệ (%)'})
            st.dataframe(contribution_df,
                         use_container_width=True, hide_index=True)


# -------------------------------------------------------------
@st.cache_data
def prepare_weekly_trend_data(df, food_to_group):
    """Prepare weekly trend data without widgets"""
    # Make sure createTime is processed properly
    if 'year_week' not in df.columns:
        df['year_week'] = pd.to_datetime(
            df['createTime'], unit='s').dt.strftime('%Y-%U')

    # Get all unique weeks
    weeks = sorted(df['year_week'].unique())

    # Process weekly trends
    category_counts = defaultdict(lambda: defaultdict(int))

    # Group by week and category
    for _, row in df.iterrows():
        if not isinstance(row['foods'], list) or not row['foods']:
            continue

        week = row['year_week']
        for food in row['foods']:
            if food in food_to_group:  # Check if food exists in the mapping
                category = food_to_group.get(food, "Khác")
                category_counts[week][category] += 1

    # Transform to DataFrame format
    trend_data = []
    for week, categories in category_counts.items():
        for category, count in categories.items():
            trend_data.append({
                'week': week,
                'category': category,
                'count': count
            })

    # Create a DataFrame and check if it's empty or missing the required columns
    result_df = pd.DataFrame(trend_data)

    # If the DataFrame is empty, create a default one with the required columns
    if result_df.empty or 'category' not in result_df.columns:
        result_df = pd.DataFrame(columns=['week', 'category', 'count'])

    return result_df


@st.cache_data
def find_unique_weekly_foods(df, comparison_weeks=3):
    # Ensure we have a date column with proper week formatting
    if 'date' not in df.columns and 'createTime' in df.columns:
        df['date'] = pd.to_datetime(df['createTime'], unit='s')

    # Use the standardized year_week column if it exists, otherwise create it
    if 'year_week' not in df.columns:
        df['year_week'] = df['date'].dt.strftime('%Y-%U')

    # Explode foods list to get individual food items
    exploded_df = df.explode('foods')[['year_week', 'foods']].dropna()

    # Get all weeks in chronological order
    all_weeks = sorted(exploded_df['year_week'].unique())

    # Create a lookup for formatted week display
    week_display = {}
    for week in all_weeks:
        if '-' in str(week):
            year, w_num = week.split('-')
            week_display[week] = f"Y{year}_W{int(w_num):02d}"
        else:
            week_display[week] = week

    # Calculate food counts for all weeks
    all_food_counts = exploded_df.groupby(
        ['year_week', 'foods']).size().reset_index(name='count')

    # Get a list of consistently popular foods (appear in most weeks)
    # Lowered from 0.7 to be less strict
    popular_threshold = len(all_weeks) * 0.6
    common_foods = exploded_df.groupby('foods')['year_week'].nunique()
    consistently_popular = common_foods[common_foods >=
                                        popular_threshold].index.tolist()

    # Dictionary to store unique foods by week
    unique_weekly_foods = {}

    # Process each week with adaptive thresholds
    for i, current_week in enumerate(all_weeks):
        # Get previous weeks for comparison
        if i < comparison_weeks:
            # This will be empty for i=0 (first week)
            previous_weeks = all_weeks[:i]
        else:
            previous_weeks = all_weeks[max(0, i-comparison_weeks):i]

        # Get foods for current week
        current_week_foods = all_food_counts[all_food_counts['year_week']
                                             == current_week]

        # Skip consistently popular foods
        current_week_foods = current_week_foods[~current_week_foods['foods'].isin(
            consistently_popular)]

        # For the first week (when previous_weeks is empty), identify top mentioned foods
        if i == 0 or not previous_weeks:
            # No previous weeks to compare, just take top mentioned foods
            top_foods = current_week_foods.nlargest(10, 'count')
            unique_foods = [(row['foods'], row['count'], 100.0)
                            for _, row in top_foods.iterrows()]
            unique_weekly_foods[current_week] = unique_foods
            continue

        # For other weeks, use adaptive thresholds
        # (min_mentions, threshold_pct)
        thresholds = [(3, 60), (2, 50), (1, 40)]
        unique_foods = []

        for min_mentions, threshold_pct in thresholds:
            # Apply current threshold
            filtered_foods = current_week_foods[current_week_foods['count']
                                                >= min_mentions]

            for _, row in filtered_foods.iterrows():
                food = row['foods']
                current_count = row['count']

                # Skip foods already identified as unique
                if any(food == f[0] for f in unique_foods):
                    continue

                # Get counts for this food in previous weeks
                previous_counts = all_food_counts[
                    (all_food_counts['foods'] == food) &
                    (all_food_counts['year_week'].isin(previous_weeks))
                ]['count'].sum()

                # Calculate percentage
                total_mentions = current_count + previous_counts
                if total_mentions == 0:
                    continue

                current_percentage = (current_count / total_mentions) * 100

                # Check if it meets threshold
                if current_percentage >= threshold_pct:
                    unique_foods.append(
                        (food, current_count, current_percentage))

            # If we have enough unique foods at this threshold, we're done
            if len(unique_foods) >= 5:
                break

        # If we still have no unique foods, get the most mentioned foods this week
        if not unique_foods and not current_week_foods.empty:
            top_foods = current_week_foods.nlargest(5, 'count')
            for _, row in top_foods.iterrows():
                food = row['foods']
                current_count = row['count']

                # Get counts for this food in previous weeks
                previous_counts = all_food_counts[
                    (all_food_counts['foods'] == food) &
                    (all_food_counts['year_week'].isin(previous_weeks))
                ]['count'].sum()

                # Calculate percentage (even if lower than threshold)
                total_mentions = current_count + previous_counts
                if total_mentions == 0:
                    continue

                current_percentage = (current_count / total_mentions) * 100
                unique_foods.append((food, current_count, current_percentage))

        # Sort unique foods by count and store in dictionary
        unique_foods.sort(key=lambda x: x[1], reverse=True)
        unique_weekly_foods[current_week] = unique_foods

    return unique_weekly_foods, week_display


@st.cache_data
def prepare_unique_food_visualization_data(unique_foods_by_week, week_display, top_n=10):
    """Prepare visualization data for unique foods"""
    viz_data = []
    for week, foods in unique_foods_by_week.items():
        formatted_week = week_display[week]
        for i, (food, count, percentage) in enumerate(foods[:top_n]):
            viz_data.append({
                'week': week,
                'week_display': formatted_week,
                'food': food,
                'count': count,
                'percentage': percentage,
                'rank': i + 1
            })

    if not viz_data:
        return None

    viz_df = pd.DataFrame(viz_data)

    # Create a proper sort key for weeks to ensure chronological order
    if 'week' in viz_df.columns and not viz_df.empty:
        viz_df['week_sort'] = viz_df['week'].apply(
            lambda w: int(w.replace('-', '')) if '-' in w else w
        )
        viz_df = viz_df.sort_values('week_sort')

    weeks_with_data = [week for week,
                       foods in unique_foods_by_week.items() if foods]

    return {
        'viz_df': viz_df,
        'weeks_with_data': weeks_with_data
    }


def analyze_unique_weekly_foods(df: pd.DataFrame):
    """Visualize uniquely trending foods by week with simplified controls"""
    st.markdown("<h2 class='sub-header'>Các Món Ăn Nổi Bật Theo Tuần</h2>",
                unsafe_allow_html=True)

    # Adjust ratio as needed (1:2 means the slider takes 1/3 of the width)
    col1, col2, _ = st.columns(spec=[3, 3, 3], gap="medium", border=False)
    with col1:  # * Filter chọn số lượng tuần để so sánh
        comparison_weeks = st.slider(
            "Số tuần so sánh:",
            min_value=1,
            max_value=8,
            value=3,
            help="Số tuần trước đó để so sánh khi xác định món ăn nổi bật"
        )

    unique_foods_by_week, week_display = find_unique_weekly_foods(
        df, comparison_weeks=comparison_weeks)

    # Prepare visualization data
    viz_data_container = prepare_unique_food_visualization_data(
        unique_foods_by_week,
        week_display,
        top_n=10
    )

    if viz_data_container is None or viz_data_container['viz_df'].empty:
        st.warning("Không có đủ dữ liệu để hiển thị món ăn nổi bật.")
        return

    viz_df = viz_data_container['viz_df']
    weeks_with_data = viz_data_container['weeks_with_data']

    # Show week selector
    if not weeks_with_data:
        st.warning("Không tìm thấy tuần nào có món ăn nổi bật.")
        return

    # Format all weeks for display in the dropdown
    all_formatted_weeks = []
    for week in sorted(df['year_week'].unique()):
        if '-' in str(week):
            year, w_num = week.split('-')
            all_formatted_weeks.append((week, f"Y{year}_W{int(w_num):02d}"))
        else:
            all_formatted_weeks.append((week, week))

    # Create a dictionary for lookup
    week_to_display = {k: v for k, v in all_formatted_weeks}
    display_to_week = {v: k for k, v in all_formatted_weeks}

    formatted_weeks_display = []
    formatted_to_original = {}

    for w in sorted(df['year_week'].unique()):
        # Get the existing Y2024_W27 format
        original_format = week_to_display[w]

        # Extract year and week numbers from the original format
        if '_W' in original_format:
            year_part = original_format.split('_W')[0].replace('Y', '')
            week_part = original_format.split('_W')[1]

            # Create the new user-friendly format
            user_friendly_format = f"Năm {year_part} - Tuần {int(week_part):02d}"

            # Store in our lists
            formatted_weeks_display.append(user_friendly_format)
            formatted_to_original[user_friendly_format] = original_format
        else:
            # Handle any edge cases where the format is different
            formatted_weeks_display.append(original_format)
            formatted_to_original[original_format] = original_format

    with col2:  # * Filter chọn tuần để phân tích
        # Use the new user-friendly format in the selectbox
        selected_display_friendly = st.selectbox(
            label="Chọn tuần để phân tích:",
            options=formatted_weeks_display,
            index=min(len(formatted_weeks_display)-1, 0)
        )

    selected_display = formatted_to_original.get(selected_display_friendly)
    # Convert display format back to the actual week value
    selected_year_week = display_to_week.get(selected_display)

    # Create two columns - one for selected week, one for overview
    col1, col2 = st.columns([1, 1])

    with col1:
        # Create a formatted header for the week
        selected_week_friendly = formatted_weeks_display[formatted_weeks_display.index(
            selected_display_friendly)]
        week_header = f"Món ăn nổi bật trong {selected_week_friendly}"
        # st.markdown(f"##### {week_header}")
        st.subheader(f":blue[{week_header}]")

        # Get foods for selected week
        week_foods = []
        if selected_year_week in unique_foods_by_week:
            week_foods = unique_foods_by_week[selected_year_week]

        if not week_foods:
            st.info("Không có món ăn nổi bật nào trong tuần này.")
        else:
            # Create a simple list of foods with count and percentage
            for i, (food, count, percentage) in enumerate(week_foods[:10], 1):
                st.markdown(
                    f"**{i}. {proper_capitalize(food)}**"
                )

    with col2:
        # Show a preview of other weeks' unique foods
        # st.markdown("##### Xem thông tin các tuần gần nhất")
        st.subheader(f":blue[Xem thông tin các tuần gần nhất]")

        # Create tabs for nearby weeks
        all_weeks = sorted(unique_foods_by_week.keys())
        if selected_year_week in all_weeks:
            current_idx = all_weeks.index(selected_year_week)

            start_idx = max(0, current_idx - 2)
            end_idx = min(len(all_weeks), current_idx + 3)
            nearby_weeks = all_weeks[start_idx:end_idx]

            # Create a tab for each nearby week with shorter format
            if nearby_weeks:
                # Create short format display for tabs
                short_format_tabs = []
                for w in nearby_weeks:
                    original_format = week_to_display.get(w, w)
                    if '_W' in original_format:
                        year_part = original_format.split(
                            '_W')[0].replace('Y', '')
                        week_part = original_format.split('_W')[1]
                        # Create the shorter format: N2023_T50
                        short_format = f"N{year_part}_T{int(week_part):02d}"
                        short_format_tabs.append(short_format)
                    else:
                        short_format_tabs.append(original_format)

                tabs = st.tabs(short_format_tabs)

                for i, week in enumerate(nearby_weeks):
                    with tabs[i]:
                        week_foods = unique_foods_by_week[week]
                        if week_foods:
                            # Show top 5 foods for each week in preview
                            for j, (food, count, percentage) in enumerate(week_foods[:5], 1):
                                st.markdown(
                                    f"**{j}. {proper_capitalize(food)}**"
                                )
                        else:
                            st.info("Không có món ăn nổi bật.")


# ================================================================
# *_______________________ [Basic setup] ________________________*
# ================================================================
# Set page configuration
st.set_page_config(
    page_title="Phân Tích Xu Hướng Ẩm Thực Việt Nam",
    page_icon="🍜",
    layout="wide",
    # initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 600;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.8rem;
        font-weight: 500;
        color: #2563EB;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .description {
        font-size: 1rem;
        margin-bottom: 1.5rem;
    }
    .highlight {
        color: #1E40AF;
        font-weight: 500;
    }
    .footer {
        text-align: center;
        margin-top: 3rem;
        color: #6B7280;
        font-size: 0.8rem;
    }
    .metric-container {
        background-color: #F3F4F6;
        border-radius: 5px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("<h1 class='main-header'>Phân Tích Xu Hướng Ẩm Thực Việt Nam</h1>",
            unsafe_allow_html=True)
st.markdown("<p class='description'>Phân tích dữ liệu xu hướng đề cập đến món ăn Việt Nam trên mạng xã hội dựa trên dữ liệu TikTok.</p>", unsafe_allow_html=True)


# ================================================================
# *________________________ [Read data] _________________________*
# ================================================================
# Load data
df = load_food_location_data()

# Application sections
st.divider()
display_data_overview(df)
st.divider()
analyze_weekly_trends(df)
st.divider()
analyze_geospatial_distribution(df)
st.divider()
analyze_food_categories(df)
st.divider()
analyze_unique_weekly_foods(df)
