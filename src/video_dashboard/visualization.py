import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots



# Hashtag Engagement
# Function to analyze hashtag engagement
def analyze_hashtag_engagement(df, top_n=5):
    hashtag_dict = {}

    for _, row in df.iterrows():
        for hashtag in row['hashtags']:
            if hashtag not in hashtag_dict:
                hashtag_dict[hashtag] = {'count': 0, 'total_comments': 0, 'total_shares': 0, 'total_likes': 0, 'total_views': 0}

            hashtag_dict[hashtag]['count'] += 1
            hashtag_dict[hashtag]['total_comments'] += row['statsV2.commentCount']
            hashtag_dict[hashtag]['total_shares'] += row['statsV2.shareCount']
            hashtag_dict[hashtag]['total_likes'] += row['statsV2.diggCount']
            hashtag_dict[hashtag]['total_views'] += row['statsV2.playCount']

    hashtag_df = pd.DataFrame.from_dict(hashtag_dict, orient='index').reset_index()
    hashtag_df.rename(columns={'index': 'hashtag'}, inplace=True)

    hashtag_df['avg_comments'] = hashtag_df['total_comments'] / hashtag_df['count']
    hashtag_df['avg_shares'] = hashtag_df['total_shares'] / hashtag_df['count']
    hashtag_df['avg_likes'] = hashtag_df['total_likes'] / hashtag_df['count']
    hashtag_df['avg_views'] = hashtag_df['total_views'] / hashtag_df['count']

    top_hashtags = {
        "Views": hashtag_df.nlargest(top_n, 'avg_views')[['hashtag', 'avg_views']],
        "Likes": hashtag_df.nlargest(top_n, 'avg_likes')[['hashtag', 'avg_likes']],
        "Shares": hashtag_df.nlargest(top_n, 'avg_shares')[['hashtag', 'avg_shares']],
        "Comments": hashtag_df.nlargest(top_n, 'avg_comments')[['hashtag', 'avg_comments']]
    }

    return top_hashtags

# Hashtag Trends Overtime
# Function to plot top hashtags
def plot_improved_top_hashtags(top_hashtags):
    all_data = []
    for metric, df in top_hashtags.items():
        df = df.copy()
        df.rename(columns={df.columns[1]: 'Engagement'}, inplace=True)
        df['Metric'] = metric
        all_data.append(df)

    final_df = pd.concat(all_data)

    fig = px.bar(final_df, 
                 x='hashtag', 
                 y='Engagement', 
                 color='Metric', 
                 barmode='group',
                 title="Top Hashtags by Views, Likes, Shares, and Comments",
                 labels={'hashtag': 'Hashtag', 'Engagement': 'Average Engagement'},
                 text_auto=True)

    fig.update_layout(xaxis_tickangle=-45)
    return fig

def plot_hashtag_trends(df, time_agg="Daily", top_n=5):
    """
    Plots hashtag trends over time, allowing aggregation by day, week, or month.

    Parameters:
    df (DataFrame): TikTok video dataset.
    time_agg (str): Time aggregation level ("Daily", "Weekly", "Monthly").
    top_n (int): Number of top hashtags to display.
    """
    df["createTime"] = pd.to_datetime(df["createTime"])
    
    if time_agg == "Weekly":
        df["time_group"] = df["createTime"].dt.to_period("W").astype(str)
    elif time_agg == "Monthly":
        df["time_group"] = df["createTime"].dt.to_period("M").astype(str)
    else:  # Default to Daily
        df["time_group"] = df["createTime"].dt.date.astype(str)
    
    hashtag_trends = {}
    for _, row in df.iterrows():
        for hashtag in row["hashtags"]:
            if hashtag not in hashtag_trends:
                hashtag_trends[hashtag] = {}
            if row["time_group"] not in hashtag_trends[hashtag]:
                hashtag_trends[hashtag][row["time_group"]] = 0
            hashtag_trends[hashtag][row["time_group"]] += row["statsV2.playCount"]  # Change to other metrics if needed

    # Convert to DataFrame
    trend_data = []
    for hashtag, trends in hashtag_trends.items():
        for time, value in trends.items():
            trend_data.append({"hashtag": hashtag, "time": time, "engagement": value})

    trend_df = pd.DataFrame(trend_data)
    
    # Get top trending hashtags
    top_hashtags = trend_df.groupby("hashtag", observed=False)["engagement"].sum().nlargest(top_n).index
    trend_df = trend_df[trend_df["hashtag"].isin(top_hashtags)]

    # Plot line chart
    fig = px.line(trend_df, x="time", y="engagement", color="hashtag",
                  title=f"Top {top_n} Hashtag Trends ({time_agg})",
                  labels={"time": time_agg, "engagement": "Total Engagement"})
    
    return fig

# Hashtag Count Group
# Function to analyze hashtag count effect
def analyze_hashtag_count_effect(df):
    df['num_hashtags'] = df['hashtags'].apply(len)
    bins = [0, 2, 5, 8, 12, 15, 20, 30, float('inf')]
    labels = ['1-2', '3-5', '6-8', '9-12', '13-15', '16-20', '21-30', '30+']
    df['hashtag_group'] = pd.cut(df['num_hashtags'], bins=bins, labels=labels, right=False)

    hashtag_effect = df.groupby(['hashtag_group'], observed=False).agg(
        total_views=('statsV2.playCount', 'sum'),
        total_likes=('statsV2.diggCount', 'sum'),
        total_shares=('statsV2.shareCount', 'sum'),
        total_comments=('statsV2.commentCount', 'sum'),
        count=('hashtag_group', 'size')
    ).reset_index()
    
    return hashtag_effect

# Function to get top hashtags by group
def get_top_hashtags_by_group(df, top_n=5):
    hashtag_groups = df.groupby('hashtag_group', observed=False)
    top_hashtags_list = []
    
    for group, group_df in hashtag_groups:
        hashtag_counts = {}
        for _, row in group_df.iterrows():
            for hashtag in row['hashtags']:
                if hashtag not in hashtag_counts:
                    hashtag_counts[hashtag] = {'total_views': 0, 'total_likes': 0, 'total_shares': 0, 'total_comments': 0}
                hashtag_counts[hashtag]['total_views'] += row['statsV2.playCount']
                hashtag_counts[hashtag]['total_likes'] += row['statsV2.diggCount']
                hashtag_counts[hashtag]['total_shares'] += row['statsV2.shareCount']
                hashtag_counts[hashtag]['total_comments'] += row['statsV2.commentCount']
        
        hashtag_df = pd.DataFrame.from_dict(hashtag_counts, orient='index').reset_index()
        hashtag_df.rename(columns={'index': 'hashtag'}, inplace=True)
        hashtag_df['hashtag_group'] = group

        top_hashtags_list.append(hashtag_df.nlargest(top_n, 'total_views'))
    
    return pd.concat(top_hashtags_list, ignore_index=True)

def plot_interactive_hashtag_analysis(hashtag_effect_df, top_hashtags_df):
    fig = make_subplots(
        rows=1, cols=2, 
        subplot_titles=["Total Engagement by Hashtag Count Group", "Top Hashtags by Engagement Type"],
        shared_yaxes=False
    )

    # Engagement metrics and colors
    engagement_metrics = ['total_views', 'total_likes', 'total_shares', 'total_comments']
    colors = ['blue', 'red', 'green', 'orange']

    # 📌 First subplot: Total Engagement by Hashtag Count Group
    for metric, color in zip(engagement_metrics, colors):
        fig.add_trace(
            go.Bar(
                x=hashtag_effect_df['hashtag_group'],
                y=hashtag_effect_df[metric],
                name=metric.replace("total_", "Total ").title(),
                marker=dict(color=color),
                showlegend=True
            ),
            row=1, col=1
        )

    # 📌 Second subplot: Top Hashtags by Engagement Type (Sorted)
    for metric, color in zip(engagement_metrics, colors):
        sorted_df = top_hashtags_df.sort_values(by=metric, ascending=False)  # ✅ Sorting FIXED
        fig.add_trace(
            go.Bar(
                x=sorted_df['hashtag'],
                y=sorted_df[metric],
                name=metric.replace("total_", "Total ").title(),
                marker=dict(color=color),
                showlegend=True
            ),
            row=1, col=2
        )

    # ✅ Ensure sorting updates dynamically when filtering
    fig.update_layout(
        title_text="Hashtag Count vs Top Hashtags Engagement",
        barmode='group',
        legend_title="Engagement Type",
        xaxis_title="Hashtag Count Group",
        xaxis2_title="Top Hashtags",
        xaxis2=dict(categoryorder="total descending"),  # ✅ Dynamic sorting applied
        legend=dict(itemclick="toggle", itemdoubleclick="toggleothers")  # 🔥 Fully interactive legend
    )

    return fig

# Video Duration Analysis - Load & Categorize
def categorize_video_duration(df):
    bins = [0, 10, 30, 60, 90, 120, 180, 300, 600, float("inf")]
    labels = ["<10s", "10-30s", "30-60s", "60-90s", "90-120s", "2 mins", "3-5 mins", "5-10 mins", ">10 mins"]
    df["video_duration_category"] = pd.cut(df["video.duration"], bins=bins, labels=labels, right=False)
    return df

# 📊 Video Duration vs. Views (Bar + Line Chart)
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

    # Layout
    fig.update_layout(title_text=f"Video Duration vs. {metric}",
                      xaxis_title="Video Duration Category",
                      yaxis_title="Number of Videos",
                      yaxis2_title=f"Total {metric}")
    
    return fig


# 📊 Video Duration vs. Engagement (Scatter Plot)
def plot_video_duration_vs_engagement(df, metric="Views"):
    df = categorize_video_duration(df)

    # Filter only the selected metric
    engagement_df = df[["video_duration_category", metric]]
    engagement_df.rename(columns={metric: "Count"}, inplace=True)

    # Scatter plot
    fig = px.scatter(
        engagement_df,
        x="video_duration_category",
        y="Count",
        title=f"Video Duration vs. {metric}",
        labels={"video_duration_category": "Video Duration Category", "Count": f"Total {metric}"},
        category_orders={"video_duration_category": ["<10s", "10-30s", "30-60s", "60-90s", "90-120s", "2 mins", "3-5 mins", "5-10 mins", ">10 mins"]}
    )

    return fig


def plot_posting_time_vs_views(df, metric="Views"):
    df['hour'] = df['createTime'].dt.hour  # Extract hour from timestamp

    # Aggregate based on the selected metric
    hourly_metric = df.groupby("hour", observed=False)[metric].sum().reset_index()

    # Plot
    fig = px.line(hourly_metric, x="hour", y=metric,
                  markers=True, title=f"Total {metric} by Posting Hour (0-23h)",
                  labels={"hour": "Hour of the Day", metric: f"Total {metric}"})

    # Highlight 19h-22h with a shaded region
    fig.add_vrect(x0=19, x1=22, fillcolor="red", opacity=0.2, layer="below", 
                  annotation_text="19h-22h", annotation_position="top left")

    return fig


def plot_posting_day_vs_engagement(df, metric="Views"):
    df["day_of_week"] = df["createTime"].dt.day_name()  # Extract weekday name

    # Define weekday order (so the chart is in order)
    weekday_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    # Aggregate based on the selected metric
    weekly_metric = df.groupby("day_of_week", observed=False)[metric].sum().reset_index()

    # Ensure correct weekday order
    weekly_metric["day_of_week"] = pd.Categorical(weekly_metric["day_of_week"], categories=weekday_order, ordered=True)
    weekly_metric = weekly_metric.sort_values("day_of_week")

    # Plot
    fig = px.bar(weekly_metric, x="day_of_week", y=metric,
                 title=f"Total {metric} by Day of the Week",
                 labels={"day_of_week": "Day of the Week", metric: f"Total {metric}"},
                 text_auto=True)

    # Highlight Friday-Sunday
    fig.add_vrect(x0=3.5, x1=6.5, fillcolor="orange", opacity=0.2, layer="below", 
                  annotation_text="Weekend (Fri-Sun)", annotation_position="top left")

    return fig


