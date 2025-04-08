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
import warnings
warnings.filterwarnings('ignore')


# ================================================================
# *_____________________ [Define constants] _____________________*
# ================================================================
DARK_GRAY: str = "#444444"
CLEANED_FOOD_LOCATION_DATA_FILE: str = "src/app/trend_analysis/final.parquet"


# ================================================================
# *____________________ [Utility functions] _____________________*
# ================================================================
# Function to properly capitalize names for visualization
def proper_capitalize(text: str) -> str:
    """ Capitalize the first letter of each word in a string """

    if not isinstance(text, str):
        return text
    # Split by spaces and capitalize each word, then rejoin
    return ' '.join(word.capitalize() for word in text.split())


# Function to load and cache data
@st.cache_data(ttl=3600)
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
        st.metric(label="Tổng số bản ghi",
                  value=f"{int(overview_info['total_records']):,}")
    with col2:
        st.metric(label="Thời gian bắt đầu",
                  value=overview_info['min_year_week_display'])
    with col3:
        st.metric(label="Thời gian kết thúc",
                  value=overview_info['max_year_week_display'])
    with col4:
        st.metric(label="Số tuần dữ liệu",
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
            y=0.95,  # Adjust vertical position
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

# ----------------------------------------------


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
            font=dict(size=26, color=DARK_GRAY),
            x=0,     # Adjust horizontal position
            y=0.95,  # Adjust vertical position
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
                font=dict(size=26, color=DARK_GRAY),
                x=0,     # Adjust horizontal position
                y=0.95,  # Adjust vertical position
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
def get_location_data(df, city_list=None):
    """Process location data for visualization with optional city filtering"""
    # Define default city list if none provided
    city_list = [
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


def analyze_geospatial_distribution(df):
    """Analyze and visualize geographical distribution of food mentions with predefined cities"""
    st.markdown("<h2 class='sub-header'>Phân Bố Địa Lý</h2>",
                unsafe_allow_html=True)

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

    if city_data.empty:
        st.warning("Không tìm thấy dữ liệu cho các thành phố đã chọn!")
        return

    # * Barchart thể hiện số lượng món ăn theo thành phố/tỉnh
    # Display city-based visualization - LIMIT TO TOP 10

    # Sort by count (descending) then take only top 10
    sorted_city_data = city_data.sort_values('count', ascending=False).head(10)
    # Re-sort for display (ascending for horizontal bar chart)
    sorted_city_data = sorted_city_data.sort_values('count', ascending=True)

    # Create visualization
    fig = px.bar(
        sorted_city_data,
        x='count',
        y='city',
        orientation='h',
        labels={'count': 'Số lượng đề cập', 'city': 'Thành phố/Tỉnh'},
    )
    fig.update_layout(
        xaxis_title="",
        yaxis_title="",
        height=400,  # Fixed height for top 10
        # Đặt tiêu đề cho biểu đồ
        title=dict(
            text='Top 10 tỉnh/thành phố có nhiều đề cập nhất',
            font=dict(size=26, color=DARK_GRAY),
            x=0,     # Adjust horizontal position
            y=0.95,  # Adjust vertical position
        ),
    )
    st.plotly_chart(fig, use_container_width=True)

    # * Treemap hiển thị phân bố địa điểm theo thành phố và quận/huyện
    # Create enhanced treemap with city and district hierarchy (also limit to top 10 cities)
    # st.markdown(
    #     "##### Bản đồ phân bố các địa điểm được nhắc đến(Top 10 thành phố và Quận/Huyện)")
    # Prepare data for hierarchical treemap
    if not district_data_with_city.empty:
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

        # Create treemap with city -> district hierarchy
        fig = px.treemap(
            filtered_district_data,
            path=['city_std', 'district_std'],  # Hierarchical path
            values='count',
            # title='Phân bố địa điểm theo Top 10 thành phố và quận/huyện',
            color='count',
            color_continuous_scale=[[0, 'rgb(0,68,137)'], [0.5, 'rgb(0,142,171)'], [
                1, 'rgb(0,204,150)']]
        )
        # Improve treemap appearance
        fig.update_traces(
            hovertemplate='<b>%{label}</b><br>Số lượng: %{value}<extra></extra>',
            textinfo="label+value"
        )
        fig.update_layout(
            height=700,  # Larger height for better visibility
            margin=dict(t=75, l=25, r=25, b=25),
            # Đặt tiêu đề cho biểu đồ
            title=dict(
                text='Phân bố địa điểm theo Top 10 thành phố và quận/huyện',
                font=dict(size=26, color=DARK_GRAY),
                x=0,     # Adjust horizontal position
                y=0.95,  # Adjust vertical position
            ),
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Không có dữ liệu quận/huyện cho các thành phố đã chọn.")


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
analyze_food_categories(df)
st.divider()
analyze_geospatial_distribution(df)
st.divider()
analyze_unique_weekly_foods(df)
