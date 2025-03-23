from config import COLUMN_LABELS
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import ast
import plotly.express as px
import pandas as pd
import streamlit as st
from sklearn.preprocessing import MinMaxScaler
# from wordcloud import WordCloud


def generate_color_map(labels):
    palette = px.colors.qualitative.Plotly  # hoặc Plotly, Pastel, Bold...
    colors = palette * (len(labels) // len(palette) + 1)
    return {label: colors[i] for i, label in enumerate(labels)}


def plot_bar_chart(df, field, metric, stat_type, color_map=None):
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

    fig = px.bar(
        grouped,
        x=grouped.columns[1],
        y=field,
        color=field,
        color_discrete_map=color_map,
        orientation='h',
        title=f'{COLUMN_LABELS.get(field, field)} vs {grouped.columns[1]}',
        labels={
            grouped.columns[1]: grouped.columns[1],
            field: COLUMN_LABELS.get(field, field)
        },
        height=600
    )
    fig.update_layout(showlegend=False)
    return fig


# def scale_params_0_100(df, params):
#     df_scaled = df.copy()
#     scaler = MinMaxScaler(feature_range=(0, 100))
#     df_scaled[params] = scaler.fit_transform(df[params])
#     return df_scaled

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
                theta=metrics + [metrics[0]],
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
            theta=metrics + [metrics[0]],
            fill='toself',
            name="Tổng thể",
            opacity=0.6,
            # hoặc có thể random màu hoặc color_map['all'] nếu muốn
            line=dict(color="blue")
        ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                tickvals=[0, 25, 50, 75, 100],
                # range=[exploded.min(), exploded.max()],
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
        showlegend=True,
        template="plotly_white",
        height=550,
        title=" vs. ".join(selected_label) if selected_label else "Tổng thể"
    )
    return fig


def render_wordcloud(df, field):
    from itertools import chain
    if field not in df.columns:
        return
    all_keywords = list(chain.from_iterable(df[field].dropna()))
    all_keywords = [str(word) for word in all_keywords if pd.notnull(word)]
    if not all_keywords:
        st.warning(
            f"Không có dữ liệu để hiển thị WordCloud cho {COLUMN_LABELS.get(field, field)}.")
        return
    text = " ".join(all_keywords)
    wc = WordCloud(width=1000, height=600, background_color='white',
                   collocations=False).generate(text)
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.imshow(wc, interpolation='bilinear')
    ax.axis("off")
    st.pyplot(fig)


def render_duration_chart(df, metric='statsV2.playCount', stat_type='mean'):
    import numpy as np

    bins = [0, 10, 30, 60, 90, 120, 180, 300, 600, float("inf")]
    labels = ["<10s", "10-30s", "30-60s", "60-90s", "90-120s",
              "2 mins", "3-5 mins", "5-10 mins", ">10 mins"]

    if 'video.duration' not in df.columns or metric not in df.columns:
        st.warning("Thiếu cột 'video.duration' hoặc chỉ số để phân tích.")
        return

    df = df.dropna(subset=['video.duration', metric])
    df['duration_bin'] = pd.cut(
        df['video.duration'], bins=bins, labels=labels, right=False)

    if stat_type == 'mean':
        grouped = (
            df.groupby('duration_bin')[metric]
            .mean()
            .reset_index(name=f'{stat_type}_{metric}')
        )
    elif stat_type == 'median':
        grouped = (
            df.groupby('duration_bin')[metric]
            .median()
            .reset_index(name=f'{stat_type}_{metric}')
        )
    elif stat_type == 'count':
        grouped = (
            df.groupby('duration_bin')[metric]
            .count()
            .reset_index(name='Số lượng video')
        )
        metric = 'Số lượng video'
    else:
        st.warning("Loại thống kê không hợp lệ.")
        return

    y_col = grouped.columns[1]

    fig = px.bar(
        grouped,
        x='duration_bin',
        y=y_col,
        title=f'{y_col} theo độ dài video',
        labels={'duration_bin': 'Độ dài video', y_col: y_col},
        height=500
    )
    st.plotly_chart(fig, use_container_width=True)
