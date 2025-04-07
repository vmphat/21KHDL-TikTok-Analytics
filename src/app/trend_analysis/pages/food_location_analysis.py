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
import warnings
warnings.filterwarnings('ignore')


# Set page configuration
st.set_page_config(
    page_title="Phân Tích Xu Hướng Ẩm Thực Việt Nam",
    page_icon="🍜",
    layout="wide",
    initial_sidebar_state="expanded"
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
# Helper function to safely format week labels


def format_tick_label(w):
    w_str = str(w)
    try:
        if '-' in w_str:
            parts = w_str.split('-')
            if len(parts) == 2:
                year = parts[0]
                week = parts[1]
                # Use last two digits of year for more compact display
                short_year = year[-2:] if len(year) >= 2 else year
                return f"T{week}_{short_year}"
        # Fallback for other formats
        return f"T{w_str}"
    except Exception:
        return f"T{w_str}"


# Function to load and cache data
@st.cache_data(ttl=3600)
def load_data():
    """
    Load and prepare the dataset with caching for performance
    """
    file_path = "src/app/trend_analysis/final.parquet"
    df = pd.read_parquet(file_path)

    # Ensure datetime format for createTime
    df['date'] = pd.to_datetime(df['createTime'], unit='s')
    df['year_week'] = df['date'].dt.strftime('%Y-%U')

    # Extract year and week separately for filtering
    df['year'] = df['date'].dt.year
    df['week'] = df['date'].dt.isocalendar().week

    return df


# Load data
try:
    df = load_data()
    data_loaded = True
except Exception as e:
    st.error(f"Lỗi khi tải dữ liệu: {e}")
    data_loaded = False


# Define functions for each section
@st.cache_data
def get_data_overview_info(df):
    """Prepare data overview information without widgets"""
    # Calculate time range and metrics
    min_date = df['date'].min().strftime('%d/%m/%Y')
    max_date = df['date'].max().strftime('%d/%m/%Y')
    total_records = len(df)
    unique_weeks = df['year_week'].nunique()

    # Create year-week range description
    min_year_week = df['year_week'].min()
    max_year_week = df['year_week'].max()
    min_year, min_week = min_year_week.split('-')
    max_year, max_week = max_year_week.split('-')

    # Count records by week
    weekly_counts = df.groupby('year_week').size().reset_index(name='count')
    weekly_counts['year_week_label'] = weekly_counts['year_week'].apply(
        lambda x: f"Tuần {x.split('-')[1]}, {x.split('-')[0]}"
    )

    # Column descriptions for data features
    col_descriptions = {
        'foods': 'Danh sách các món ăn được nhắc đến',
        'city_std': 'Tên thành phố/tỉnh đã được chuẩn hóa',
        'district_std': 'Tên quận/huyện đã được chuẩn hóa',
        'date': 'Thời gian tạo nội dung',
        'year_week': 'Năm và tuần của nội dung'
    }

    return {
        'min_date': min_date,
        'max_date': max_date,
        'total_records': total_records,
        'unique_weeks': unique_weeks,
        'min_year_week': min_year_week,
        'max_year_week': max_year_week,
        'min_year': min_year,
        'min_week': min_week,
        'max_year': max_year,
        'max_week': max_week,
        'weekly_counts': weekly_counts,
        'col_descriptions': col_descriptions
    }


def display_data_overview(df):
    """Display general overview and statistics about the dataset"""
    st.markdown("<h2 class='sub-header'>Tổng Quan Dữ Liệu</h2>",
                unsafe_allow_html=True)

    # Get cached overview information
    overview_info = get_data_overview_info(df)

    # Metrics row
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Tổng số bản ghi", f"{overview_info['total_records']:,}")
    with col2:
        st.metric("Thời gian bắt đầu",
                  f"Tuần {overview_info['min_week']}, {overview_info['min_year']}")
    with col3:
        st.metric("Thời gian kết thúc",
                  f"Tuần {overview_info['max_week']}, {overview_info['max_year']}")

    # Data distribution over time
    st.markdown("##### Phân bố dữ liệu theo thời gian")

    # Create interactive chart
    fig = px.bar(
        overview_info['weekly_counts'],
        x='year_week',
        y='count',
        labels={'year_week': 'Tuần', 'count': 'Số lượng bản ghi'},
        title='Số lượng bản ghi theo tuần'
    )

    fig.update_layout(
        xaxis_title="Tuần",
        yaxis_title="Số lượng",
        height=400,
        hovermode="x unified"
    )

    # Add custom hover template
    fig.update_traces(
        hovertemplate='Tuần %{x}<br>Số lượng: %{y:,.0f}<extra></extra>'
    )

    st.plotly_chart(fig, use_container_width=True)

    # Show data features
    with st.expander("Xem thêm thông tin về cấu trúc dữ liệu"):
        st.markdown("##### Thông tin cột dữ liệu")

        for col, desc in overview_info['col_descriptions'].items():
            st.markdown(f"**{col}**: {desc}")


@st.cache_data
def get_food_category_data(df):
    """
    Process food category data for visualization
    Returns dictionary with food categories and their variants
    """
    # Function to extract all food items and count occurrences
    all_foods = df['foods'].explode().dropna()
    food_counts = all_foods.value_counts()

    # Group foods by common words
    def identify_food_groups(food_counts):
        # First, tokenize all food names into words
        food_tokens = {}
        for food in food_counts.index:
            tokens = food.lower().split()
            food_tokens[food] = tokens

        # Create a mapping of foods to their group
        food_to_group = {}
        food_groups = defaultdict(list)
        processed_foods = set()

        # Process foods in order of popularity
        for food in food_counts.index:
            if food in processed_foods:
                continue

            # This food starts a new group
            base_tokens = food_tokens[food]
            current_group = []

            # Find all foods that share at least 2 words with this food
            for other_food in food_counts.index:
                if other_food in processed_foods:
                    continue

                other_tokens = food_tokens[other_food]

                # Count common words
                common_words = set(base_tokens) & set(other_tokens)

                # If there are at least 2 common words, add to group
                if len(common_words) >= 2:
                    current_group.append(other_food)
                    processed_foods.add(other_food)

            # If we found a group, create a group name from common words
            if current_group:
                # Find most common words across the group
                all_words = []
                for group_food in current_group:
                    all_words.extend(food_tokens[group_food])

                word_counts = pd.Series(all_words).value_counts()
                top_words = word_counts.head(2).index.tolist()

                # Create group name from top words
                group_name = " ".join(top_words)

                # Associate each food with this group
                for group_food in current_group:
                    food_to_group[group_food] = group_name
                    food_groups[group_name].append(group_food)

        return food_groups, food_to_group

    # Get food groups and mappings
    food_groups, food_to_group = identify_food_groups(food_counts)

    # Calculate total counts for each group
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
def prepare_category_details(category_name, category_data, food_counts):
    """Prepare detailed data for a specific category without widgets"""
    # Get variants sorted by count
    variants = sorted(
        category_data['variant_counts'].items(),
        key=lambda x: x[1],
        reverse=True
    )

    # Prepare data for visualization
    variant_df = pd.DataFrame(variants, columns=['variant', 'count'])
    total = variant_df['count'].sum()
    variant_df['percentage'] = variant_df['count'] / total * 100

    # Keep variants with >= 10% share, group others
    main_variants = variant_df[variant_df['percentage'] >= 5]
    other_variants = variant_df[variant_df['percentage'] < 5]

    # If too many main variants, limit to top 10
    if len(main_variants) > 10:
        main_variants = main_variants.head(10)
        other_variants = pd.concat([
            variant_df.iloc[10:],
            other_variants
        ])

    # Prepare final data
    plot_data = main_variants.copy()

    if not other_variants.empty:
        other_sum = other_variants['count'].sum()
        other_row = pd.DataFrame({
            'variant': ['Khác'],
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


def analyze_food_categories(df):
    """Analyze and visualize food categories and their variants"""
    st.markdown("<h2 class='sub-header'>Phân Tích Món Ăn Theo Danh Mục</h2>",
                unsafe_allow_html=True)

    # Get processed food category data
    category_data = get_food_category_data(df)
    sorted_groups = category_data['sorted_groups']

    # Let user select how many top categories to view
    top_k = st.slider(
        "Chọn số lượng danh mục món ăn hàng đầu để hiển thị:",
        min_value=5,
        max_value=min(20, len(sorted_groups)),
        value=10
    )

    # Get top K categories
    top_categories = sorted_groups[:top_k]

    # Create overview bar chart of categories
    category_names = [group[0].upper() for group in top_categories]
    category_values = [group[1]['total_count'] for group in top_categories]

    fig = px.bar(
        x=category_values,
        y=category_names,
        orientation='h',
        labels={'x': 'Số lượng đề cập', 'y': 'Danh mục món ăn'},
        title=f'Top {top_k} Danh Mục Món Ăn Được Đề Cập Nhiều Nhất'
    )

    fig.update_layout(yaxis={'categoryorder': 'total ascending'})
    st.plotly_chart(fig, use_container_width=True)

    # Create detailed view for selected category
    st.markdown("##### Chi tiết danh mục món ăn")
    st.write("Chọn một danh mục để xem chi tiết các biến thể món ăn:")

    # Convert category names to a more readable format for the selectbox
    readable_categories = [
        f"{cat[0].upper()} ({cat[1]['total_count']} đề cập)" for cat in top_categories]
    selected_category_index = st.selectbox(
        "Danh mục món ăn:",
        range(len(readable_categories)),
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

    # Display category information
    st.markdown(f"**Danh mục: {category_details['category_name'].upper()}**")
    st.markdown(f"Tổng số đề cập: {category_details['total_count']}")
    st.markdown(f"Số lượng biến thể: {category_details['num_variants']}")

    # Create pie chart
    fig = px.pie(
        category_details['plot_data'],
        values='count',
        names='variant',
        title=f'Phân bố các biến thể trong danh mục {category_details["category_name"].upper()}',
        hover_data=['percentage']
    )

    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hovertemplate='<b>%{label}</b><br>Số lượng: %{value}<br>Tỉ lệ: %{percent}<extra></extra>'
    )

    st.plotly_chart(fig, use_container_width=True)

    # Show table of all variants
    with st.expander("Xem chi tiết tất cả các biến thể"):
        st.dataframe(
            category_details['all_variants_df'], use_container_width=True)


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


def display_temporal_trends(df):
    """Visualize food category trends over time"""
    st.markdown("<h2 class='sub-header'>Xu Hướng Theo Thời Gian</h2>",
                unsafe_allow_html=True)

    # Get food category data
    category_data = get_food_category_data(df)
    food_to_group = category_data['food_to_group']

    # Get trend data (cached)
    trend_df = prepare_weekly_trend_data(df, food_to_group)

    # Check if we have valid data to display
    if trend_df.empty or 'category' not in trend_df.columns:
        st.warning("Không có đủ dữ liệu để hiển thị xu hướng theo thời gian.")
        return

    # Widget controls for visualization options
    col1, col2 = st.columns(2)

    with col1:
        top_n = st.slider(
            "Số lượng danh mục hàng đầu hiển thị:",
            min_value=3,
            max_value=10,
            value=5
        )

    with col2:
        view_type = st.radio(
            "Chọn kiểu hiển thị:",
            ["Số lượng tuyệt đối", "Tỉ lệ phần trăm"]
        )

    rolling_window = st.slider(
        "Khoảng trung bình di động (tuần):",
        min_value=1,
        max_value=8,
        value=2,
        help="Điều chỉnh để làm mịn biểu đồ. Giá trị 1 sẽ hiển thị dữ liệu gốc."
    )

    # Get top categories by total mentions
    top_categories = trend_df.groupby('category')['count'].sum().nlargest(
        min(top_n, len(trend_df['category'].unique()))).index.tolist()

    # If no top categories found, show a warning message
    if not top_categories:
        st.warning("Không tìm thấy dữ liệu danh mục món ăn theo thời gian.")
        return

    # Filter data to top categories
    filtered_df = trend_df[trend_df['category'].isin(top_categories)]

    # Create pivot table for visualization
    pivot_df = filtered_df.pivot_table(
        index='week',
        columns='category',
        values='count',
        aggfunc='sum',
        fill_value=0
    ).reset_index()

    # Sort by week
    pivot_df = pivot_df.sort_values('week')

    # Apply rolling average if selected
    if rolling_window > 1:
        for col in pivot_df.columns:
            if col != 'week':
                pivot_df[col] = pivot_df[col].rolling(
                    window=rolling_window, min_periods=1).mean()

    # For percentage view, calculate percentages
    if view_type == "Tỉ lệ phần trăm":
        # Calculate row sums excluding 'week' column
        row_sums = pivot_df.drop(columns=['week']).sum(axis=1)
        # Avoid division by zero
        for col in pivot_df.columns:
            if col != 'week':
                pivot_df[col] = pivot_df[col].div(
                    row_sums.where(row_sums > 0, 1)) * 100

    # Create visualization
    fig = px.line(
        pivot_df,
        x='week',
        y=top_categories,
        labels={'value': 'Số lượng đề cập' if view_type ==
                "Số lượng tuyệt đối" else 'Phần trăm (%)', 'week': 'Tuần'},
        title=f'Xu hướng danh mục món ăn theo thời gian (Top {len(top_categories)})'
    )

    # Update layout for better visibility
    fig.update_layout(
        xaxis_title="Tuần",
        yaxis_title="Số lượng đề cập" if view_type == "Số lượng tuyệt đối" else "Phần trăm (%)",
        legend_title="Danh mục món ăn",
        hovermode="x unified",
        height=500
    )

    # Customize hover info
    for trace in fig.data:
        trace.hovertemplate = '%{y:.1f}' + (' đề cập' if view_type ==
                                            "Số lượng tuyệt đối" else '%') + '<extra>%{fullData.name}</extra>'

    st.plotly_chart(fig, use_container_width=True)

    # Area chart visualization (stacked)
    st.markdown("##### Biểu đồ diện tích xu hướng món ăn")

    # Create area chart
    fig = px.area(
        pivot_df,
        x='week',
        y=top_categories,
        labels={'value': 'Số lượng đề cập' if view_type ==
                "Số lượng tuyệt đối" else 'Phần trăm (%)', 'week': 'Tuần'},
        title=f'Xu hướng danh mục món ăn theo thời gian - Biểu đồ diện tích (Top {len(top_categories)})'
    )

    # Update layout for better visibility
    fig.update_layout(
        xaxis_title="Tuần",
        yaxis_title="Số lượng đề cập" if view_type == "Số lượng tuyệt đối" else "Phần trăm (%)",
        legend_title="Danh mục món ăn",
        hovermode="x unified",
        height=500
    )

    st.plotly_chart(fig, use_container_width=True)


@st.cache_data
def get_location_data(df):
    """Process location data for visualization without widgets"""
    # Standardize city data
    city_data = df['city_std'].explode().dropna().value_counts().reset_index()
    city_data.columns = ['city', 'count']

    # Standardize district data
    district_data = df['district_std'].explode(
    ).dropna().value_counts().reset_index()
    district_data.columns = ['district', 'count']

    return {
        'city_data': city_data,
        'district_data': district_data
    }


def analyze_geospatial_distribution(df):
    """Analyze and visualize geographical distribution of food mentions"""
    st.markdown("<h2 class='sub-header'>Phân Bố Địa Lý</h2>",
                unsafe_allow_html=True)

    # Get location data (cached)
    location_data = get_location_data(df)
    city_data = location_data['city_data']
    district_data = location_data['district_data']

    # Display city-based visualization
    st.markdown("##### Phân bố đề cập theo thành phố/tỉnh")

    # Filter to top cities
    top_cities = 10
    top_city_data = city_data.head(top_cities)

    # Create visualization
    fig = px.bar(
        top_city_data,
        x='count',
        y='city',
        orientation='h',
        labels={'count': 'Số lượng đề cập', 'city': 'Thành phố/Tỉnh'},
        title=f'Top {top_cities} thành phố/tỉnh có nhiều đề cập nhất'
    )

    fig.update_layout(
        yaxis={'categoryorder': 'total ascending'},
        xaxis_title="Số lượng đề cập",
        yaxis_title="Thành phố/Tỉnh",
        height=500
    )

    st.plotly_chart(fig, use_container_width=True)

    # Display district visualization with city filter
    st.markdown("##### Phân bố đề cập theo quận/huyện")

    # Let user filter by city - MOVED OUTSIDE THE CACHED FUNCTION
    top_cities_list = city_data.head(10)['city'].tolist()
    selected_city = st.selectbox(
        "Chọn thành phố/tỉnh để xem chi tiết quận/huyện:",
        ["Tất cả"] + top_cities_list
    )

    # Filter district data based on selected city
    if selected_city != "Tất cả":
        # Here we would need to join district with city information
        # For simplicity in this implementation, let's assume district names are unique
        # In a real implementation, you would filter based on a city-district relationship
        # Simplified - replace with actual filter
        filtered_districts = district_data.head(15)
    else:
        filtered_districts = district_data.head(15)

    # Create visualization
    fig = px.bar(
        filtered_districts,
        x='count',
        y='district',
        orientation='h',
        labels={'count': 'Số lượng đề cập', 'district': 'Quận/Huyện'},
        title=f'Top quận/huyện có nhiều đề cập nhất{" ở " + selected_city if selected_city != "Tất cả" else ""}'
    )

    fig.update_layout(
        yaxis={'categoryorder': 'total ascending'},
        xaxis_title="Số lượng đề cập",
        yaxis_title="Quận/Huyện",
        height=500
    )

    st.plotly_chart(fig, use_container_width=True)

    # Create choropleth map visualization
    st.markdown("##### Bản đồ phân bố")
    st.write("Hiển thị thông qua biểu đồ treemap để tối ưu hiệu suất:")

    # Create treemap visualization (more resource-efficient than actual map)
    fig = px.treemap(
        city_data.head(20),
        path=['city'],
        values='count',
        title='Treemap phân bố theo thành phố/tỉnh',
        color='count',
        color_continuous_scale='YlOrRd'
    )

    fig.update_traces(
        hovertemplate='<b>%{label}</b><br>Số lượng: %{value}<extra></extra>'
    )

    st.plotly_chart(fig, use_container_width=True)


@st.cache_data
def find_unique_weekly_foods(df, threshold_pct=60, min_mentions=3, comparison_weeks=3):
    """
    Identifies foods that are uniquely trending in specific weeks.
    Without widget commands.
    """
    # Ensure we have a date column with proper week formatting
    if 'date' not in df.columns and 'createTime' in df.columns:
        df['date'] = pd.to_datetime(df['createTime'], unit='s')

    if 'week' not in df.columns and 'date' in df.columns:
        df['week'] = df['date'].dt.strftime('%Y-%U')

    # Explode foods list to get individual food items
    exploded_df = df.explode('foods')[['week', 'foods']].dropna()

    # Get all weeks in chronological order
    all_weeks = sorted(exploded_df['week'].unique())

    # Calculate food counts for all weeks
    all_food_counts = exploded_df.groupby(
        ['week', 'foods']).size().reset_index(name='count')

    # Get a list of consistently popular foods (appear in most weeks)
    # Foods that appear in 70% or more of all weeks
    popular_threshold = len(all_weeks) * 0.7
    common_foods = exploded_df.groupby('foods')['week'].nunique()
    consistently_popular = common_foods[common_foods >=
                                        popular_threshold].index.tolist()

    # Dictionary to store unique foods by week
    unique_weekly_foods = {}

    # Process each week
    for i, current_week in enumerate(all_weeks):
        # Skip the first weeks since we need previous weeks for comparison
        if i < comparison_weeks:
            unique_weekly_foods[current_week] = []
            continue

        # Get previous weeks for comparison
        previous_weeks = all_weeks[max(0, i-comparison_weeks):i]

        # Get foods for current week
        current_week_foods = all_food_counts[all_food_counts['week']
                                             == current_week]

        # Filter out foods that don't meet minimum mention threshold
        current_week_foods = current_week_foods[current_week_foods['count']
                                                >= min_mentions]

        # Skip consistently popular foods
        current_week_foods = current_week_foods[~current_week_foods['foods'].isin(
            consistently_popular)]

        # If no foods meet the criteria, continue to next week
        if current_week_foods.empty:
            unique_weekly_foods[current_week] = []
            continue

        # For each food in current week, check if it's unique to this week
        unique_foods = []
        for _, row in current_week_foods.iterrows():
            food = row['foods']
            current_count = row['count']

            # Get counts for this food in previous weeks
            previous_counts = all_food_counts[
                (all_food_counts['foods'] == food) &
                (all_food_counts['week'].isin(previous_weeks))
            ]['count'].sum()

            # Calculate what percentage of mentions are in current week vs previous weeks
            total_mentions = current_count + previous_counts
            current_percentage = (current_count / total_mentions) * 100

            # If current week accounts for at least threshold_pct% of mentions, consider it uniquely trending
            if current_percentage >= threshold_pct:
                unique_foods.append((food, current_count, current_percentage))

        # Sort unique foods by count and store in dictionary
        unique_foods.sort(key=lambda x: x[1], reverse=True)
        unique_weekly_foods[current_week] = unique_foods

    return unique_weekly_foods


@st.cache_data
def prepare_unique_food_visualization_data(unique_foods_by_week, top_n=5):
    """Prepare visualization data for unique foods without widgets"""
    viz_data = []
    for week, foods in unique_foods_by_week.items():
        for i, (food, count, percentage) in enumerate(foods[:top_n]):
            viz_data.append({
                'week': week,
                'food': food,
                'count': count,
                'percentage': percentage,
                'rank': i + 1
            })

    if not viz_data:
        return None

    viz_df = pd.DataFrame(viz_data)

    # Prepare weeks with data
    weeks_with_data = [week for week,
                       foods in unique_foods_by_week.items() if foods]

    return {
        'viz_df': viz_df,
        'weeks_with_data': weeks_with_data
    }


def analyze_unique_weekly_foods(df):
    """Visualize uniquely trending foods by week"""
    st.markdown("<h2 class='sub-header'>Các Món Ăn Nổi Bật Theo Tuần</h2>",
                unsafe_allow_html=True)

    # Let user adjust parameters - MOVED OUTSIDE THE CACHED FUNCTION
    col1, col2, col3 = st.columns(3)

    with col1:
        threshold_pct = st.slider(
            "Ngưỡng phần trăm (%):",
            min_value=50,
            max_value=80,
            value=70,
            help="Phần trăm tối thiểu của đề cập xuất hiện trong tuần hiện tại so với các tuần trước đó"
        )

    with col2:
        min_mentions = st.slider(
            "Số lượng đề cập tối thiểu:",
            min_value=1,
            max_value=10,
            value=3,
            help="Số lượng đề cập tối thiểu để được xem xét"
        )

    with col3:
        comparison_weeks = st.slider(
            "Số tuần so sánh:",
            min_value=1,
            max_value=8,
            value=3,
            help="Số tuần trước đó để so sánh"
        )

    # Run analysis with selected parameters
    with st.spinner("Đang phân tích dữ liệu..."):
        # Get cached unique foods data
        unique_foods_by_week = find_unique_weekly_foods(
            df,
            threshold_pct=threshold_pct,
            min_mentions=min_mentions,
            comparison_weeks=comparison_weeks
        )

        # Prepare visualization data
        viz_data_container = prepare_unique_food_visualization_data(
            unique_foods_by_week, top_n=5)

        if viz_data_container is None or viz_data_container['viz_df'].empty:
            st.warning(
                "Không có đủ dữ liệu để hiển thị món ăn nổi bật với các tham số đã chọn.")
            return

        viz_df = viz_data_container['viz_df']
        weeks_with_data = viz_data_container['weeks_with_data']

    # Show week selector
    if not weeks_with_data:
        st.warning(
            "Không tìm thấy tuần nào có món ăn nổi bật với các tham số đã chọn.")
        return

    # Convert all weeks to strings to ensure .split() works safely
    weeks_with_data_str = [str(week) for week in weeks_with_data]

    # Create a function to format the week for display
    def format_week(week_str):
        try:
            if '-' in week_str:
                parts = week_str.split('-')
                if len(parts) == 2:
                    year = parts[0]
                    week = parts[1]
                    return f"Tuần {week}, năm {year}"
            # Fallback for weeks that don't follow the expected format
            return f"Tuần {week_str}"
        except Exception:
            return f"Tuần {week_str}"

    # Let user select a specific week
    selected_week_index = st.selectbox(
        "Chọn tuần để xem chi tiết:",
        range(len(weeks_with_data_str)),
        format_func=lambda i: format_week(weeks_with_data_str[i])
    )

    # Get the selected week using the index
    selected_week = weeks_with_data[selected_week_index]
    selected_week_str = str(selected_week)

    # Format header based on week format
    if '-' in selected_week_str:
        try:
            parts = selected_week_str.split('-')
            week_header = f"Món ăn nổi bật trong Tuần {parts[1]}, {parts[0]}"
        except Exception:
            week_header = f"Món ăn nổi bật trong Tuần {selected_week_str}"
    else:
        week_header = f"Món ăn nổi bật trong Tuần {selected_week_str}"

    # Display foods for selected week
    st.markdown(f"##### {week_header}")

    # Get foods for selected week
    week_foods = unique_foods_by_week[selected_week]

    if not week_foods:
        st.info("Không có món ăn nổi bật nào trong tuần này với các tham số đã chọn.")
    else:
        # Create a bar chart for selected week
        week_df = pd.DataFrame(week_foods, columns=[
                               'food', 'count', 'percentage'])
        week_df = week_df.head(10)  # Top 10

        # Create horizontal bar chart
        fig = px.bar(
            week_df,
            y='food',
            x='count',
            orientation='h',
            text='percentage',
            labels={'food': 'Món ăn', 'count': 'Số lượng đề cập',
                    'percentage': '% đề cập trong tuần này'},
            title=f'Top món ăn nổi bật trong {week_header}'
        )

        fig.update_traces(
            texttemplate='%{text:.1f}%',
            textposition='outside'
        )

        fig.update_layout(
            yaxis={'categoryorder': 'total ascending'},
            xaxis_title="Số lượng đề cập",
            yaxis_title="Món ăn",
            height=max(400, len(week_df) * 40)
        )

        st.plotly_chart(fig, use_container_width=True)

    # Create heatmap visualization for all weeks - FOLLOWING THE ORIGINAL IMPLEMENTATION
    st.markdown("##### Món ăn nổi bật theo tuần")

    # Create heatmap data
    if not viz_df.empty:
        # Pivot for heatmap - EXACTLY AS ORIGINAL
        heatmap_data = viz_df.pivot_table(
            index='food',
            columns='week',
            values='count',
            aggfunc='sum',
            fill_value=0
        )

        # Get top foods overall for better visualization - EXACTLY AS ORIGINAL
        top_foods = viz_df.groupby('food')['count'].sum().nlargest(20).index
        if len(top_foods) > 0:
            heatmap_data = heatmap_data.loc[heatmap_data.index.isin(top_foods)]

            # Create heatmap visualization using plotly
            fig = px.imshow(
                heatmap_data,
                labels=dict(x="Tuần", y="Món ăn", color="Số lượng đề cập"),
                title="Heatmap món ăn nổi bật theo tuần",
                color_continuous_scale="YlOrRd"
            )

            fig.update_xaxes(
                title="Tuần",
                tickangle=90,
                tickmode='array',
                tickvals=list(range(len(heatmap_data.columns))),
                ticktext=[format_tick_label(w) for w in heatmap_data.columns]
            )

            fig.update_layout(height=600)

            st.plotly_chart(fig, use_container_width=True)

            # Line chart for selected top foods - FOLLOWING THE ORIGINAL IMPLEMENTATION
            st.markdown("##### Xu hướng món ăn nổi bật theo thời gian")

            # Get top foods overall by total count - EXACTLY AS ORIGINAL
            top_foods_overall = viz_df.groupby(
                'food')['count'].sum().nlargest(7).index.tolist()

            # Let user select which foods to view from top foods
            selected_foods = st.multiselect(
                "Chọn món ăn để xem xu hướng:",
                top_foods_overall,
                default=top_foods_overall[:3] if len(
                    top_foods_overall) >= 3 else top_foods_overall
            )

            if selected_foods:
                # Filter data for selected foods - EXACTLY AS ORIGINAL
                selected_food_data = viz_df[viz_df['food'].isin(
                    selected_foods)]

                # Create line chart
                fig = px.line(
                    selected_food_data,
                    x='week',
                    y='count',
                    color='food',
                    markers=True,
                    labels={'count': 'Số lượng đề cập',
                            'week': 'Tuần', 'food': 'Món ăn'},
                    title='Xu hướng món ăn nổi bật theo thời gian'
                )

                fig.update_layout(
                    xaxis_title="Tuần",
                    yaxis_title="Số lượng đề cập",
                    legend_title="Món ăn",
                    hovermode="x unified"
                )

                # Format x-axis for week display
                fig.update_xaxes(
                    tickangle=90,
                    tickmode='array',
                    tickvals=sorted(selected_food_data['week'].unique()),
                    ticktext=[format_tick_label(w) for w in sorted(
                        selected_food_data['week'].unique())]
                )

                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Vui lòng chọn ít nhất một món ăn để xem xu hướng.")
        else:
            st.warning("Không đủ dữ liệu để tạo biểu đồ heatmap.")
    else:
        st.warning("Không có đủ dữ liệu để tạo biểu đồ với các tham số đã chọn.")


# Main application
# Header
st.markdown("<h1 class='main-header'>Phân Tích Xu Hướng Ẩm Thực Việt Nam</h1>",
            unsafe_allow_html=True)
st.markdown("<p class='description'>Phân tích dữ liệu xu hướng đề cập đến món ăn Việt Nam trên mạng xã hội dựa trên dữ liệu TikTok.</p>", unsafe_allow_html=True)

# Check if data loaded successfully
if not data_loaded:
    st.warning("Không thể tiếp tục vì dữ liệu không được tải thành công.")
    st.stop()

# Application sections
display_data_overview(df)
analyze_food_categories(df)
display_temporal_trends(df)
analyze_geospatial_distribution(df)
analyze_unique_weekly_foods(df)

# Footer
st.markdown("<div class='footer'>© 2025 - Dự án Phân Tích Xu Hướng Ẩm Thực Việt Nam</div>",
            unsafe_allow_html=True)
