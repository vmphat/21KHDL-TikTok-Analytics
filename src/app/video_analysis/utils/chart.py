import plotly.graph_objects as go
import matplotlib.pyplot as plt
import plotly.express as px
import pandas as pd
import streamlit as st
from video_analysis.utils.config import COLUMN_LABELS, COLUMN_METRICS, STAT_TYPES, CATEGORY_COLOR_MAP
import numpy as np


def generate_color_map(labels):
    palette = px.colors.qualitative.Plotly  # hoặc Plotly, Pastel, Bold...
    colors = palette * (len(labels) // len(palette) + 1)
    return {label: colors[i] for i, label in enumerate(labels)}


def plot_bar_chart(df, field, metric, stat_type, color_map=None):
    # stat_type = list(STAT_TYPES.keys())[
    #     0] if stat_type is None else stat_type

    if metric not in df.columns or field not in df.columns:
        return None

    exploded = df[[metric, field]].copy()
    exploded = exploded.explode(field)
    exploded = exploded.dropna(subset=[field])

    if stat_type == 'mean':
        grouped = (
            exploded.groupby(field)[metric]
            .mean()
            .reset_index(name=f'{stat_type}_{metric}')
            .sort_values(by=f'{stat_type}_{metric}', ascending=False)
        )
    elif stat_type == 'median':
        grouped = (
            exploded.groupby(field)[metric]
            .median()
            .reset_index(name=f'{stat_type}_{metric}')
            .sort_values(by=f'{stat_type}_{metric}', ascending=False)
        )
    elif stat_type == 'count':
        grouped = (
            exploded.groupby(field)[metric]
            .count()
            .reset_index(name='Số lượng video')
            .sort_values(by='Số lượng video', ascending=False)
        )
        metric = 'Số lượng video'
    else:
        return None

    # Nếu không truyền color_map, tự tạo (ít khi dùng)
    if color_map is None:
        color_map = generate_color_map(grouped[field].tolist())

    stats_text = COLUMN_METRICS.get(
        grouped.columns[1].split("_", 1)[1], grouped.columns[1]) if stat_type != 'count' else ''
    metric_text = STAT_TYPES.get(grouped.columns[1].split("_", 1)[
                                 0], grouped.columns[1])
    field_text = COLUMN_LABELS.get(field, field)

    fig = px.bar(
        grouped,
        x=grouped.columns[1],
        y=field,
        color=field,
        color_discrete_map=color_map,
        orientation='h',
        title=f'{stats_text} {metric_text} của các {field_text}',
        labels={
            grouped.columns[1]: stats_text,
            field: field_text
        },
        height=600
    )
    fig.update_layout(showlegend=False, margin=dict(l=0, r=0, t=80, b=0),)
    return fig


def scale_params_0_100(df, params):
    df_scaled = df.copy()
    for col in params:
        min_val = df[col].min()
        max_val = df[col].max()
        if max_val == min_val:
            # Trường hợp toàn 1 giá trị, gán luôn là 0 hoặc 100 tuỳ ý
            df_scaled[col] = 0
        else:
            df_scaled[col] = (df[col] - min_val) / (max_val - min_val) * 100
    return df_scaled


def plot_radar_chart(df, field, metrics, selected_label=None, color_map=None):
    exploded = df[metrics + [field]].copy()
    exploded = exploded.explode(field)
    exploded = exploded.dropna(subset=[field])
    exploded = scale_params_0_100(exploded, metrics)
    fig = go.Figure()

    if selected_label and len(selected_label) > 0:
        # Nếu có selected_label, vẽ từng label
        if color_map is None:
            color_map = generate_color_map(selected_label)

        for label in selected_label:
            subset = exploded[exploded[field] == label][metrics].mean()
            fig.add_trace(go.Scatterpolar(
                r=subset.tolist() + [subset.tolist()[0]],
                theta=[COLUMN_METRICS.get(
                    m, m) for m in metrics] + [COLUMN_METRICS.get(metrics[0], metrics[0])],
                fill='toself',
                name=str(label),
                opacity=0.5,
                line=dict(color=color_map.get(label))
            ))
    else:
        # Nếu không có selected_label, vẽ median của toàn bộ
        subset = exploded[metrics].mean()
        # st.write(subset)

        fig.add_trace(go.Scatterpolar(
            r=subset.tolist() + [subset.tolist()[0]],
            theta=[COLUMN_METRICS.get(m, m) for m in metrics] +
            [COLUMN_METRICS.get(metrics[0], metrics[0])],
            fill='toself',
            name="Tổng thể",
            opacity=0.6,
            # hoặc có thể random màu hoặc color_map['all'] nếu muốn
            line=dict(color="blue")
        ))
    fig.update_layout(
        height=600,  # Ghim chiều cao cố định

        margin=dict(
            l=40, r=40,
            t=80,
            b=100  # Đủ chỗ cho legend khi nhiều label
        ),

        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.25,  # Nếu bị tràn thì giảm xuống -0.3 hoặc -0.4
            xanchor="center",
            x=0.5,
            font=dict(size=12)
        ),

        polar=dict(
            radialaxis=dict(
                tickvals=[0, 25, 50, 75, 100],
                tickangle=45,
                tickfont=dict(size=10),
                showline=True,
                gridcolor="rgba(0,0,0,0.1)",
                gridwidth=0.5,
            ),
            angularaxis=dict(
                tickfont=dict(size=12),
            )
        ),

        template="plotly_white",
        showlegend=True,
        title="Hiệu suất tương tác của " +
        (COLUMN_LABELS[field] if field else "Tổng thể")
    )

    return fig


def plot_duration_histogram(df, duration_column='video.duration', categories='Tất cả', bins=None):
    """
    Plots a histogram of video durations.

    Args:
        df (pd.DataFrame): The DataFrame containing video data.
        duration_column (str): The column name for video durations.
        bins (list): Custom bins for the histogram. If None, default bins will be used.

    Returns:
        fig: A Plotly figure object for the histogram.
    """
    if duration_column not in df.columns:
        st.warning(f"Column '{duration_column}' not found in the DataFrame.")
        return None

    # Drop rows with missing duration values
    df = df.dropna(subset=[duration_column])

    # Default bins if none are provided
    # if bins is None:
    #     bins = [0, 10, 30, 60, 90, 120, 180, 300, 600, float("inf")]

    # # Create labels for bins
    # labels = ["<10s", "10-30s", "30-60s", "60-90s", "90-120s",
    #           "2 phút", "3-5 phút", "5-10 phút", ">10 phút"]

    # # Bin the durations
    # df['duration_bin'] = pd.cut(
    #     df[duration_column], bins=bins, labels=labels, right=False)

    # # Count the number of videos in each bin
    # grouped = df['duration_bin'].value_counts().reset_index()
    # grouped.columns = ['Duration Range', 'Count']
    # grouped = grouped.sort_values(by='Duration Range')

    # # Create the histogram using Plotly
    # fig = px.bar(
    #     grouped,
    #     x='Duration Range',
    #     y='Count',
    #     # title='Phân phối Số lượng video theo thời lượng',
    #     labels={'Duration Range': 'Thời lượng',
    #             'Count': 'Số lượng video'},
    #     # color_continuous_scale="teal",
    #     height=560
    # )

    # Calculate the median
    median_value = df[duration_column].median()
    q1 = df[duration_column].quantile(0.25)
    q3 = df[duration_column].quantile(0.75)

    counts, bins = np.histogram(df['video.duration'], bins=bins)
    bins = 0.5 * (bins[:-1] + bins[1:])
    fig = px.bar(x=bins, y=counts, labels={
                 'x': 'Thời lượng', 'y': 'Số lượng video'}, height=560)

    # Add a median line
    # fig.add_vline(
    #     x=median_value,
    #     line=dict(color="black", width=1.5, dash="longdash"),
    #     annotation_text=f"Trung vị: {median_value:.1f}s",
    #     annotation_position="top right"
    # )
    # Highlight the Q1-Q3 range
    fig.add_shape(
        type="rect",
        x0=q1,
        x1=q3,
        y0=0,
        y1=max(counts),
        fillcolor="rgba(255,255,0,0.2)",  # Light blue with transparency
        line=dict(width=0)
    )
    # Add annotations for Q1 and Q3
    fig.add_annotation(
        x=q1,
        y=max(counts) * 0.95,
        text=f"Q1: {q1:.1f}s",
        showarrow=True,
        arrowhead=2,
        ax=0,
        ay=-40
    )
    fig.add_annotation(
        x=q3,
        y=max(counts) * 0.95,
        text=f"Q3: {q3:.1f}s",
        showarrow=True,
        arrowhead=2,
        ax=0,
        ay=-40
    )

    fig.update_traces(marker_color=CATEGORY_COLOR_MAP.get(
        categories, '#60B5FF'))  # Default color if not found in the map
    fig.update_layout(yaxis_title_text='Số lượng video',
                      xaxis=dict(range=[-0.5, 600]),
                      #   yaxis=dict(range=[-0.5, 370]),
                      )

    # Display the chart in Streamlit
    st.plotly_chart(fig, use_container_width=True)
    return fig


def plot_duration_boxplot(df, metric_column, duration_column='video.duration', bins=None, exclude_outliers=True):
    """
    Plots a boxplot of a specified metric grouped by video duration ranges.

    Args:
        df (pd.DataFrame): The DataFrame containing video data.
        metric_column (str): The column name for the metric to plot.
        duration_column (str): The column name for video durations.
        bins (list): Custom bins for the duration ranges. If None, default bins will be used.

    Returns:
        fig: A Plotly figure object for the boxplot.
    """
    metric_column = list(COLUMN_METRICS.keys())[
        0] if metric_column is None else metric_column

    if duration_column not in df.columns or metric_column not in df.columns:
        st.warning(
            f"Columns '{duration_column}' or '{metric_column}' not found in the DataFrame.")
        return None

    # Drop rows with missing values in the relevant columns
    df = df.dropna(subset=[duration_column, metric_column])

    # Default bins if none are provided
    if bins is None:
        bins = [0, 10, 30, 60, 90, 120, 180, 300, 600, float("inf")]

    # Create labels for bins
    labels = ["<10s", "10-30s", "30-60s", "60-90s", "90-120s",
              "2 phút", "3-5 phút", "5-10 phút", ">10 phút"]

    # Bin the durations
    df['duration_bin'] = pd.cut(
        df[duration_column], bins=bins, labels=labels, right=False)

    df = df.sort_values(by='duration_bin')

    # Calculate the overall mean
    overall_mean = df[metric_column].median()

    # Exclude outliers if specified
    if exclude_outliers:
        Q1 = df[metric_column].quantile(0.25)
        Q3 = df[metric_column].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        df = df[(df[metric_column] >= lower_bound) &
                (df[metric_column] <= upper_bound)]

    # Create the boxplot using Plotly
    fig = px.box(
        df,
        x='duration_bin',
        y=metric_column,
        # title=f"Phân phối {COLUMN_METRICS.get(metric_column, metric_column)} theo Thời lượng",
        labels={'duration_bin': 'Thời lượng', metric_column: COLUMN_METRICS.get(
            metric_column, metric_column)},
        color='duration_bin',
        height=500,
        # vertical=True,
    )

    fig.add_shape(
        type="line",
        x0=-0.5,  # Start at the left of the plot
        x1=len(labels) - 0.5,  # End at the right of the plot
        y0=overall_mean,
        y1=overall_mean,
        line=dict(color="black", width=1.5, dash="longdash"),
    )

    fig.add_trace(
        go.Scatter(
            x=[None],  # No data points, just for the legend
            y=[None],
            mode="lines",
            line=dict(color="black", width=1.5, dash="longdash"),
            name="Trung vị Tổng thể"  # Legend label
        )
    )
    # Display the chart in Streamlit
    st.plotly_chart(fig, use_container_width=True)
    return fig


def plot_heatmap_day_hour(df, datetime_column='createTime', metric_column=None):
    """
    Plots a heatmap showing the distribution of videos by day of the week and hour of the day.

    Args:
        df (pd.DataFrame): The DataFrame containing video data.
        datetime_column (str): The column name for video creation timestamps.
        metric_column (str): The column name for the metric to aggregate. If None, counts are used.

    Returns:
        fig: A Plotly figure object for the heatmap.
    """
    if datetime_column not in df.columns:
        st.warning(f"Cột '{datetime_column}' không tồn tại trong dữ liệu.")
        return None

    # Ensure the datetime column is in datetime format
    df[datetime_column] = pd.to_datetime(df[datetime_column], errors='coerce')

    # Drop rows with invalid or missing datetime values
    df = df.dropna(subset=[datetime_column])

    # Extract day of the week and hour of the day
    df['day_of_week'] = df[datetime_column].dt.day_name()
    df['hour_of_day'] = df[datetime_column].dt.hour

    # Reorder days of the week
    days_order = ['Monday', 'Tuesday', 'Wednesday',
                  'Thursday', 'Friday', 'Saturday', 'Sunday']
    days_order_vn = ['Thứ Hai', 'Thứ Ba', 'Thứ Tư',
                     'Thứ Năm', 'Thứ Sáu', 'Thứ Bảy', 'Chủ Nhật']
    df['day_of_week'] = pd.Categorical(
        df['day_of_week'], categories=days_order, ordered=True)
    df['day_of_week_vn'] = df['day_of_week'].cat.rename_categories(
        days_order_vn)

    # Aggregate data for the heatmap
    if metric_column and metric_column in df.columns:
        heatmap_data = df.pivot_table(
            index='day_of_week_vn',
            columns='hour_of_day',
            values=metric_column,
            aggfunc='mean',
            fill_value=0
        )
        colorbar_title = f"Trung bình {COLUMN_METRICS.get(metric_column, metric_column)}"
    else:
        heatmap_data = df.pivot_table(
            index='day_of_week_vn',
            columns='hour_of_day',
            values=datetime_column,
            aggfunc='count',
            fill_value=0
        )
        colorbar_title = "Số lượng video"

    # Ensure all hours (0–23) are included in the columns
    all_hours = list(range(24))
    heatmap_data = heatmap_data.reindex(columns=all_hours, fill_value=0)

    # Create the heatmap using Plotly
    fig = px.imshow(
        heatmap_data,
        labels=dict(x="Giờ trong ngày", y="Ngày trong tuần",
                    color=colorbar_title),
        x=heatmap_data.columns,
        y=heatmap_data.index,
        color_continuous_scale="Blues",
        # title="Heatmap: Phân phối video theo ngày và giờ",
        height=500
    )

    # Update layout to ensure all hours and days are shown
    fig.update_layout(
        xaxis=dict(
            title="Giờ trong ngày",
            tickmode="array",
            tickvals=all_hours,
            ticktext=[str(hour) for hour in all_hours]
        ),
        yaxis=dict(
            title="Ngày trong tuần",
            tickmode="array",
            tickvals=days_order_vn,
            ticktext=days_order_vn
        ),
        coloraxis_colorbar=dict(title=colorbar_title), margin=dict(l=40, r=40, t=40, b=40),
    )

    # Display the chart in Streamlit
    st.plotly_chart(fig, use_container_width=True)
    return fig


def plot_hashtag_count_histogram(df, hashtag_column='hashtag_count', bins=None, xaxis_range=None, selected_category='Tất cả'):
    """
    Plots a histogram of the number of hashtags in videos with a fixed x-axis range
    and vertical lines for Q1 and Q3.

    Args:
        df (pd.DataFrame): The DataFrame containing video data.
        hashtag_column (str): The column name for the number of hashtags.
        bins (list): Custom bins for the histogram. If None, default bins will be used.
        xaxis_range (list): Fixed range for the x-axis [min, max].

    Returns:
        fig: A Plotly figure object for the histogram.
    """
    if hashtag_column not in df.columns:
        st.warning(f"Cột '{hashtag_column}' không tồn tại trong dữ liệu.")
        return None

    # Drop rows with missing hashtag values
    df = df.dropna(subset=[hashtag_column])

    # Default bins if none are provided
    if bins is None:
        # 0 to max + 1
        bins = list(range(0, int(df[hashtag_column].max()) + 2))

    # Calculate Q1 and Q3
    q1 = df[hashtag_column].quantile(0.25)
    q3 = df[hashtag_column].quantile(0.75)

    # Create the histogram using Plotly
    fig = px.histogram(
        df,
        x=hashtag_column,
        nbins=len(bins) - 1,
        # title="Phân phối số lượng hashtag trong video",
        labels={hashtag_column: "Số lượng hashtag", "count": "Số lượng video"},
        color_discrete_sequence=[CATEGORY_COLOR_MAP.get(
            selected_category, "#FFA07A")],  # Default color if not found in the map
        height=500
    )

    # Add vertical lines for Q1 and Q3
    # fig.add_vline(x=q1, line_dash="dash", line_color="red",
    #               annotation_text="Q1", annotation_position="top left")
    # fig.add_vline(x=q3, line_dash="dash", line_color="green",
    #               annotation_text="Q3", annotation_position="top right")

    # Update layout for better readability and fixed x-axis range
    fig.update_layout(
        xaxis=dict(title="Số lượng hashtag", range=xaxis_range),
        yaxis=dict(title="Số lượng video"),
        bargap=0.2
    )

    # Display the chart in Streamlit
    st.plotly_chart(fig, use_container_width=True)
    return fig


def plot_word_per_second_histogram(df, column='word_per_second', bins=None, xaxis_range=None, selected_category='Tất cả'):
    """
    Plots a histogram of the word-per-second metric with a fixed x-axis range.

    Args:
        df (pd.DataFrame): The DataFrame containing video data.
        column (str): The column name for the word-per-second metric.
        bins (list): Custom bins for the histogram. If None, default bins will be used.
        xaxis_range (list): Fixed range for the x-axis [min, max].

    Returns:
        fig: A Plotly figure object for the histogram.
    """
    if column not in df.columns:
        st.warning(f"Cột '{column}' không tồn tại trong dữ liệu.")
        return None

    # Drop rows with missing values
    df = df.dropna(subset=[column])

    # Default bins if none are provided
    if bins is None:
        bins = list(range(0, int(df[column].max()) + 2))  # 0 to max + 1

    # Create the histogram using Plotly
    fig = px.histogram(
        df,
        x=column,
        nbins=len(bins) - 1,
        # title="Phân phối Mật độ từ ngữ nói (số từ/giây)",
        labels={
            column: "Mật độ từ ngữ nói (từ/giây)", "count": "Số lượng video"},
        color_discrete_sequence=[CATEGORY_COLOR_MAP.get(
            selected_category, "#FFA07A")],  # Default color if not found in the map,
        height=500
    )

    # Update layout for better readability and fixed x-axis range
    fig.update_layout(
        xaxis=dict(title="Mật độ từ ngữ nói (từ/giây)", range=xaxis_range),
        yaxis=dict(title="Số lượng video"),
        bargap=0.2, margin=dict(l=40, r=40, t=40, b=40),

    )

    # Display the chart in Streamlit
    st.plotly_chart(fig, use_container_width=True)
    return fig


def plot_density_scatter(df, x_column='transcript_word_count', y_column='video.duration', selected_category=None):
    """
    Plots a scatter plot for two numerical columns, with optional coloring by categories.

    Args:
        df (pd.DataFrame): The DataFrame containing video data.
        x_column (str): The column name for the x-axis (e.g., transcript word count).
        y_column (str): The column name for the y-axis (e.g., video duration).
        selected_category (str or None): The selected category. If 'Tất cả', color by categories.

    Returns:
        fig: A Plotly figure object for the scatter plot.
    """
    if x_column not in df.columns or y_column not in df.columns:
        st.warning(
            f"Cột '{x_column}' hoặc '{y_column}' không tồn tại trong dữ liệu.")
        return None

    # Drop rows with missing values in the relevant columns
    df = df.dropna(subset=[x_column, y_column])

    # Determine color column and color map
    if selected_category == 'Tất cả' and 'categories' in df.columns:
        color_column = 'categories'
        color_map = CATEGORY_COLOR_MAP
    elif selected_category in CATEGORY_COLOR_MAP:
        color_column = None
        # Use the selected category's color
        color_map = {selected_category: CATEGORY_COLOR_MAP[selected_category]}
    else:
        color_column = None
        color_map = None
    # print(color_map)
    # Create the scatter plot using Plotly
    fig = px.scatter(
        df,
        x=x_column,
        y=y_column,
        # title="Phân bố: Số lượng từ và Thời lượng video",
        labels={x_column: "Số lượng từ trong transcript",
                y_column: "Thời lượng video (giây)"},
        color=color_column,  # Color by categories if 'Tất cả' is selected
        color_discrete_map=color_map,  # Use CATEGORY_COLOR_MAP or selected category's color
        height=500
    )

    # Update layout for better readability
    fig.update_layout(
        xaxis=dict(title="Số lượng từ trong transcript", range=[-100, 2500]),
        yaxis=dict(title="Thời lượng video (giây)", range=[-20, 620]),
        coloraxis_colorbar=dict(
            title="Thời lượng (giây)" if color_column is None else "Danh mục"
        ),
        margin=dict(l=40, r=40, t=40, b=40),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.25,  # Position below the chart
            xanchor="center",
            x=0.5,
        ),
    )
    fig.update_traces(marker=dict(
        color=CATEGORY_COLOR_MAP[selected_category])) if selected_category != 'Tất cả' else None
    # Display the chart in Streamlit
    st.plotly_chart(fig, use_container_width=True)
    return fig
