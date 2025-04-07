import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
from wordcloud import WordCloud

# Mapping raw column names to user-friendly labels
METRIC_LABELS = {
    "statsV2.playCount": "Views",
    "statsV2.diggCount": "Likes",
    "statsV2.commentCount": "Comments",
    "statsV2.shareCount": "Shares"
}


@st.cache_data
# 📌 Hashtag Engagement Analysis
def analyze_hashtag_engagement(df, top_n=5, metric_col="statsV2.playCount"):
    hashtag_counts = df.explode("hashtags")

    # Remove empty or NaN hashtags
    hashtag_counts = hashtag_counts[hashtag_counts["hashtags"].notna() & (
        hashtag_counts["hashtags"] != "")]

    hashtag_counts = hashtag_counts.groupby(
        "hashtags")[metric_col].sum().reset_index()
    top_hashtags = hashtag_counts.nlargest(top_n, metric_col)
    return top_hashtags


# 💊 Plot Top Hashtags
def plot_improved_top_hashtags(top_hashtags):
    metric_name = METRIC_LABELS.get(
        top_hashtags.columns[1], top_hashtags.columns[1])
    fig = px.bar(top_hashtags, x="hashtags", y=top_hashtags.columns[1],
                 title=f"Top Hashtags by {metric_name}",
                 labels={"hashtags": "Hashtags",
                         top_hashtags.columns[1]: f"{metric_name}"},
                 color=top_hashtags.columns[1], color_continuous_scale="blues")
    return fig


def plot_hashtag_trends(df, time_agg="Weekly", top_n=5, metric_col="statsV2.playCount"):
    df["date"] = pd.to_datetime(df["createTime"])

    # Group by Weekly or Monthly
    if time_agg == "Daily":
        df["time_group"] = df["date"].dt.strftime(
            "%Y-%m-%d")  # Ensure daily grouping as string
    elif time_agg == "Weekly":
        df["time_group"] = df["date"].dt.to_period("W").astype(str)
    else:  # Monthly
        df["time_group"] = df["date"].dt.to_period("M").astype(str)

    # Convert Period to String for Plotly
    df["time_group"] = df["time_group"].astype(str)

    # Explode Hashtags
    exploded = df.explode("hashtags")

    # Group by Time and Hashtags, Summing the Selected Metric
    grouped = exploded.groupby(["time_group", "hashtags"])[
        metric_col].sum().reset_index()

    # Get Top Hashtags Based on Metric
    top_hashtags = analyze_hashtag_engagement(df, top_n, metric_col)[
        "hashtags"].tolist()

    # Filter Only Top Hashtags
    filtered = grouped[grouped["hashtags"].isin(top_hashtags)]

    metric_name = METRIC_LABELS.get(metric_col, metric_col)

    # Plot Hashtag Trends Over Time
    fig = px.line(filtered, x="time_group", y=metric_col, color="hashtags",
                  title=f"Hashtag Trends Over Time ({time_agg})",
                  labels={"time_group": "{time_agg}",
                          metric_col: f"{metric_name}"}
                  )

    return fig


@st.cache_data
# 📌 Hashtag Count Effect
def analyze_hashtag_count_effect(df, metric_col="statsV2.playCount"):
    agg_df = df.groupby("hashtag_count")[metric_col].mean().reset_index()
    return agg_df

# 💊 Get Top Hashtags by Group


def get_top_hashtags_by_group(df, metric_col="statsV2.playCount"):
    exploded = df.explode("hashtags")
    grouped = exploded.groupby("hashtags")[metric_col].sum().reset_index()
    top_hashtags = grouped.nlargest(10, metric_col)
    return top_hashtags

# 📈 Interactive Hashtag Analysis


def plot_interactive_hashtag_analysis(hashtag_effect_df, top_hashtags_df, metric_col="statsV2.playCount"):
    metric_name = METRIC_LABELS.get(metric_col, metric_col)
    fig = px.scatter(hashtag_effect_df, x="hashtag_count", y=metric_col,
                     title=f"Hashtag Count vs. {metric_name}",
                     labels={"hashtag_count": "Hashtag Count",
                             metric_col: f"{metric_name}"},
                     color=metric_col)
    return fig


@st.cache_data
# Video Duration Analysis - Load & Categorize
def categorize_video_duration(df):
    bins = [0, 10, 30, 60, 90, 120, 180, 300, 600, float("inf")]
    labels = ["<10s", "10-30s", "30-60s", "60-90s", "90-120s",
              "2 mins", "3-5 mins", "5-10 mins", ">10 mins"]
    df["video_duration_category"] = pd.cut(
        df["video.duration"], bins=bins, labels=labels, right=False)
    return df

# 💊 Video Duration vs. Views (Bar + Line Chart)


def plot_video_duration_vs_views(df, metric="Views"):
    df = categorize_video_duration(df)

    # Aggregate based on the selected metric
    duration_summary = df.groupby("video_duration_category", observed=False).agg(
        num_videos=("id", "count"),
        total_metric=(metric, "sum")
    ).reset_index()

    # Plot
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Bar(x=duration_summary["video_duration_category"], y=duration_summary["num_videos"],
                         name="Number of Videos", marker_color="blue"), secondary_y=False)
    fig.add_trace(go.Scatter(x=duration_summary["video_duration_category"], y=duration_summary["total_metric"],
                             name=f"Total {metric}", mode="lines+markers", marker_color="red"), secondary_y=True)

    metric_name = METRIC_LABELS.get(metric, metric)
    # Layout
    fig.update_layout(title_text=f"Video Duration vs. {metric_name}",
                      xaxis_title="Video Duration Category",
                      yaxis_title="Number of Videos",
                      yaxis2_title=f"Total {metric_name}")

    return fig


def plot_posting_day_vs_engagement(df, metric="Views"):
    df["day_of_week"] = df["createTime"].dt.day_name()

    weekday_order = ["Monday", "Tuesday", "Wednesday",
                     "Thursday", "Friday", "Saturday", "Sunday"]
    weekly_metric = df.groupby("day_of_week", observed=False)[
        metric].sum().reset_index()
    weekly_metric["day_of_week"] = pd.Categorical(
        weekly_metric["day_of_week"], categories=weekday_order, ordered=True)
    weekly_metric = weekly_metric.sort_values("day_of_week")

    metric_name = METRIC_LABELS.get(metric, metric)

    fig = px.bar(weekly_metric, x="day_of_week", y=metric,
                 title=f"Total {metric_name} by Day of the Week",
                 labels={"day_of_week": "Day of the Week",
                         metric: f"Total {metric_name}"},
                 text_auto=True)
    fig.add_vrect(x0=3.5, x1=6.5, fillcolor="orange", opacity=0.2, layer="below",
                  annotation_text="Weekend (Fri-Sun)", annotation_position="top left")

    return fig


def plot_posting_time_vs_views(df, metric="statsV2.playCount"):
    df['hour'] = df['createTime'].dt.hour  # Extract hour from timestamp
    metric_name = METRIC_LABELS.get(metric, metric)  # Use mapping

    # Aggregate based on the selected metric
    hourly_metric = df.groupby("hour", observed=False)[
        metric].sum().reset_index()

    # Plot
    fig = px.line(hourly_metric, x="hour", y=metric,
                  markers=True, title=f"Total {metric_name} by Posting Hour (0-23h)",
                  labels={"hour": "Hour of the Day", metric: f"Total {metric_name}"})

    # Highlight 19h-22h with a shaded region
    fig.add_vrect(x0=19, x1=22, fillcolor="orange", opacity=0.2, layer="below",
                  annotation_text="19h-22h", annotation_position="top left")

    return fig


# 📊 Video Duration vs. Engagement (Scatter Plot)
def plot_video_duration_vs_engagement(df, metric="Views"):
    df = categorize_video_duration(df)

    # Filter only the selected metric
    engagement_df = df[["video_duration_category", metric]]
    engagement_df.rename(columns={metric: "Count"}, inplace=True)

    metric_name = METRIC_LABELS.get(metric, metric)

    # Scatter plot
    fig = px.scatter(
        engagement_df,
        x="video_duration_category",
        y="Count",
        title=f"Video Duration vs. {metric_name}",
        labels={"video_duration_category": "Video Duration Category",
                "Count": f"Total {metric_name}"},
        category_orders={"video_duration_category": [
            "<10s", "10-30s", "30-60s", "60-90s", "90-120s", "2 mins", "3-5 mins", "5-10 mins", ">10 mins"]}
    )

    return fig


def plot_hashtag_count_vs_engagement(df, metric_col="statsV2.playCount"):
    metric_name = METRIC_LABELS.get(metric_col, metric_col)
    fig = px.scatter(df, x="hashtag_count", y=metric_col,
                     title=f"Hashtag Count vs. {metric_col}",
                     labels={"hashtag_count": "Number of Hashtags",
                             metric_col: f"{metric_name}"},
                     color=metric_col, color_continuous_scale="viridis",
                     trendline="ols")  # Adds a trendline for correlation
    return fig


def plot_hashtag_count_boxplot(df, metric_col="statsV2.playCount"):
    fig = px.box(df, x="hashtag_count", y=metric_col,
                 title=f"Distribution of {metric_col} by Hashtag Count",
                 labels={"hashtag_count": "Number of Hashtags",
                         metric_col: "Engagement"},
                 color="hashtag_count")
    return fig


@st.cache_data
def generate_hashtag_wordcloud(df, metric_col="statsV2.playCount"):
    """Generate a word cloud of hashtags based on their impact (views, likes, engagement)."""

    # Explode hashtags and filter non-empty values
    hashtags = df.explode("hashtags")
    hashtags = hashtags[hashtags["hashtags"].notna() & (
        hashtags["hashtags"] != "")]

    # Aggregate hashtag impact (sum of the selected metric)
    hashtag_counts = hashtags.groupby("hashtags")[metric_col].sum().to_dict()

    # Generate WordCloud
    wordcloud = WordCloud(width=800, height=400,
                          background_color="white", colormap="coolwarm")
    wordcloud.generate_from_frequencies(hashtag_counts)

    return wordcloud


def show_hashtag_wordcloud(df, metric_col):
    """Display the hashtag word cloud in Streamlit."""
    st.subheader("🔥 Hashtag Word Cloud")

    wordcloud = generate_hashtag_wordcloud(df, metric_col=metric_col)

    # Display in Streamlit using Matplotlib
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.imshow(wordcloud, interpolation="bilinear")
    ax.axis("off")
    st.pyplot(fig)
