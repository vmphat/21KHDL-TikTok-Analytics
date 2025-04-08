import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
from types import NoneType
from video_analysis.utils.chart import plot_bar_chart, plot_radar_chart, generate_color_map, plot_duration_histogram, plot_duration_boxplot, plot_heatmap_day_hour, plot_hashtag_count_histogram, plot_word_per_second_histogram, plot_density_scatter
from video_analysis.utils.config import COLUMN_LABELS, COLUMN_METRICS, STAT_TYPES, CATEGORY_COLOR_MAP


@st.cache_data
def load_data():
    """Load data from parquet file and preprocess numpy arrays to lists"""

    def _parse_list(x):
        """Convert numpy arrays to Python lists, handle None values"""
        if isinstance(x, np.ndarray):
            return list(x)
        if isinstance(x, NoneType):
            return []
        return x

    features_df = pd.read_parquet(
        'data/content_analysis/content_analysis_data.parquet')

    # Convert numpy arrays to Python lists for better compatibility
    for col in features_df.columns:
        if features_df[col].apply(lambda x: isinstance(x, np.ndarray)).any():
            features_df[col] = features_df[col].apply(_parse_list)
    print(features_df.columns)
    return features_df


class TikTokContentAnalysis:
    """Class for TikTok content analysis dashboard"""

    def __init__(self):
        # Configure page layout
        st.set_page_config(layout="wide")

        # Load and prepare data
        self.df = load_data()
        self.df = self.df[self.df['categories'] != 'Không liên quan ẩm thực']

        # Set up fields to analyze
        self.fields_to_analyze = set(COLUMN_LABELS.keys()) - \
            set(['categories', 'has_cta', 'has_personal_story'])

        # Initialize state
        self.selected_category = None
        self.selected_field = None
        self.filtered_df = self.df
        self.color_map = {}

    def _calculate_statistics(self, df):
        """Calculate statistics from filtered dataframes"""
        duration_Q1 = df['video.duration'].quantile(0.25)
        duration_Q3 = df['video.duration'].quantile(0.75)
        duration_IQR = duration_Q3 - duration_Q1
        duration_lower_bound = duration_Q1 - 1.5 * duration_IQR
        duration_upper_bound = duration_Q3 + 1.5 * duration_IQR

        hashtag_count_Q1 = df['hashtag_count'].quantile(0.25)
        hashtag_count_Q3 = df['hashtag_count'].quantile(0.75)
        hashtag_count_IQR = hashtag_count_Q3 - hashtag_count_Q1
        hashtag_count_lower_bound = hashtag_count_Q1 - 1 * hashtag_count_IQR
        hashtag_count_upper_bound = hashtag_count_Q3 + 1 * hashtag_count_IQR

        stats = {
            # 'mean_word_count': int(df['transcript_word_count'].mean()),
            'mean_duration': (df['video.duration'].mean()),
            'duration_min_q': duration_Q1,
            'duration_max_q': duration_Q3,
            'mean_word_per_second': df['word_per_second'].mean(),
            'mean_hashtag_count': (df['hashtag_count'].mean()),
            'hashtag_count_min_q': hashtag_count_Q1,
            'hashtag_count_max_q': hashtag_count_Q3,
            'mean_view_count': df['statsV2.playCount'].mean(),
            'mean_like_count': df['statsV2.diggCount'].mean(),
            'mean_comment_count': df['statsV2.commentCount'].mean(),
            'mean_share_count': df['statsV2.shareCount'].mean(),
            'mean_collect_count': df['statsV2.collectCount'].mean(),
            'mean_engagement_rate': df['engagement_rate'].mean(),
        }

        # Get top hashtags
        # top_10_hashtags = df['hashtags'].explode(
        # ).value_counts().head(10).index
        # stats['top_10_hashtags_text'] = ', '.join(top_10_hashtags)

        # Get sample texts
        # stats['transcript_sample_text'], stats['desc_sample_text'] = format_transcript_desc_examples(
        #     df, min_count=20)

        return stats

    def personal_styles(self):
        st.markdown("""
            <style>
            h1, h2, h3 { color: #1f2a44; font-family: 'Helvetica', sans-serif; }
            .stMetric { border-radius: 8px; padding: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            </style>
        """, unsafe_allow_html=True)

    def setup_sidebar(self):
        """Configure sidebar filters"""
        st.sidebar.header("Tùy chọn phân tích")

        # Category filter
        category_options = ['Tất cả'] + self.df['categories'].dropna(
        ).unique().tolist()

        self.selected_category = st.sidebar.radio(
            "Chọn thể loại:",
            options=category_options,
            index=0
        )

        # Apply filters
        self.apply_filters()

    def apply_filters(self):
        """Apply selected filters to the dataframe"""
        self.filtered_df = self.df.copy()

        if self.selected_category == 'Tất cả':
            return

        if self.selected_category:
            self.filtered_df = self.filtered_df[self.filtered_df['categories']
                                                == self.selected_category]

    def setup_main_layout(self):
        """Setup main page layout and components"""
        self.personal_styles()
        stats = self._calculate_statistics(self.filtered_df)

        cat_text = self.selected_category if self.selected_category else "Tất cả"
        st.title(f"📊 Phân tích nội dung: {cat_text}")
        with st.container():
            st.subheader("Các chỉ sổ trung bình")
            col0, col01, col1, col2, col3 = st.columns(
                [1, 1, 1, 1, 1])
            # col0, col01, col02 = st.columns([1, 1, 1])
            with col0:
                st.metric(
                    ":material/movie: Số lượng video", f"{len(self.filtered_df):,}")
                st.metric(
                    ":material/visibility: Lượt xem", f"{int(stats['mean_view_count']):,}")
            with col01:
                st.metric(
                    ":material/person_pin_circle: Số lượng TikToker", f"{(self.filtered_df['author.uniqueId'].nunique()):,}")
                st.metric(
                    ":material/thumb_up: Lượt thích", f"{int(stats['mean_like_count']):,}")
            with col1:
                st.metric(
                    ":material/schedule: Thời lượng", f"{int(stats['mean_duration']//60)} phút {int(stats['mean_duration']%60)} giây")
                st.metric(
                    ":material/chat_bubble_outline: Lượt bình luận", f"{int(stats['mean_comment_count']):,}")
            with col2:
                st.metric(
                    ":material/tag: Số lượng hashtag", f"{int(stats['hashtag_count_min_q'])} - {int(stats['hashtag_count_max_q'])}")
                st.metric(
                    ":material/share: Lượt chia sẻ", f"{int(stats['mean_share_count']):,}")
            with col3:
                st.metric(":material/article: Mật độ từ ngữ",
                          f"{round(stats['mean_word_per_second'],1)} từ/giây")
                st.metric(
                    ":material/save: Lượt lưu", f"{int(stats['mean_collect_count']):,}")

        # st.header(header_text)
        st.subheader("Về cách xây dựng nội dung video")

        # Display performance metrics section
        self.display_performance_metrics()

        st.subheader("Về thời lượng video")
        col1, col2 = st.columns([5, 7])
        with col1:
            # Display duration histogram
            self.display_duration_histogram()
        with col2:
            # Display duration boxplot
            self.display_duration_boxplot()

        st.subheader("Về cách sử dụng hashtag trong video")
        col1, col2 = st.columns([6, 3.5])
        with col1:
            # Display hashtag count histogram
            self.display_hashtag_count_histogram()
        with col2:
            # Display top hashtags
            self.display_top_hashtags()

        st.subheader("Về mật độ từ ngữ trong video")
        col1, col2 = st.columns([6, 3.5])
        with col2:
            # Display word-per-second histogram
            self.display_word_per_second_histogram()
        with col1:
            # Display scatter plot
            self.display_scatter_plot()

        # st.subheader("Về thời điểm đăng video")
        # # Display heatmap
        # self.display_heatmap_day_hour()

    def display_performance_metrics(self):
        """Display performance metrics section with charts"""

        # Create two columns for charts

        self.selected_field = st.pills(
            "Chọn :red[**trường**] cần hiển thị trên biểu đồ:",
            options=self.fields_to_analyze,
            format_func=lambda x: COLUMN_LABELS.get(x, x),
            default='audience_target'
        )

        col1, col2 = st.columns([3, 2])

        with col1:
            self.display_bar_chart(col1)

        with col2:
            self.display_radar_chart()

    def display_bar_chart(self, container):
        """Display bar chart with controls"""
        # Performance metric selection
        with st.container(border=True, height=730):
            col11, col12 = st.columns([1, 1])
            with col12:
                # Generate color map for consistency across charts
                labels = self.filtered_df[self.selected_field].explode(
                ).dropna().unique().tolist()
                self.color_map = generate_color_map(labels)
                # st.markdown(
                #     f"#### Hiệu suất tương tác theo {COLUMN_LABELS.get(self.selected_field, self.selected_field)}")

                # Statistic type selection
                stat_type = st.radio(
                    "Loại :red[**thống kê**]:",
                    options=list(STAT_TYPES.keys()),
                    format_func=lambda x: STAT_TYPES.get(x, x),
                    horizontal=True, label_visibility="visible"
                )

            with col11:
                selected_metric = st.selectbox(
                    "Chỉ số :red[**hiệu suất**]:",
                    options=list(COLUMN_METRICS.keys()),
                    format_func=lambda x: COLUMN_METRICS.get(x, x)
                )

            # with st.container(border=True):
            fig = plot_bar_chart(
                self.filtered_df,
                self.selected_field,
                selected_metric,
                stat_type,
                color_map=self.color_map
            )

            if fig:
                st.plotly_chart(
                    fig, use_container_width=True, key="bar_chart")

    def display_radar_chart(self):
        """Display radar chart with controls"""
        # Prepare data for radar chart
        exploded = self.filtered_df.copy()
        exploded = exploded.explode(self.selected_field).dropna(
            subset=[self.selected_field])
        labels = exploded[self.selected_field].unique()

        # Label selection for radar chart
        with st.container(border=True, height=730):
            selected_labels = st.multiselect(
                f"Chọn kiểu :red[**{COLUMN_LABELS[self.selected_field]}**]:",
                labels,
                default=None
            )

            # Prepare metrics for radar chart (exclude engagement_rate)
            display_metrics = COLUMN_METRICS.copy()
            display_metrics.pop('engagement_rate', None)

            # Generate and display radar chart
            radar_fig = plot_radar_chart(
                self.filtered_df,
                self.selected_field,
                metrics=list(display_metrics.keys()),
                selected_label=selected_labels,
                color_map=self.color_map
            )

            if radar_fig:
                st.plotly_chart(radar_fig, use_container_width=True,
                                key="radar_chart")

    def display_duration_histogram(self):
        """Display a histogram of video durations."""
        st.markdown("#### Phân phối Thời lượng video")
        # st.write('')
        if 'video.duration' not in self.filtered_df.columns:
            st.warning("Dữ liệu không chứa cột 'video.duration'.")
            return

        # Call the plot_duration_histogram function
        plot_duration_histogram(
            self.filtered_df, duration_column='video.duration', bins=range(0, 600, 20))

    def display_duration_boxplot(self):
        """Display a boxplot of metrics grouped by video duration ranges."""
        st.markdown("#### Phân phối tương tác theo Thời lượng video")
        if 'video.duration' not in self.filtered_df.columns:
            st.warning("Dữ liệu không chứa cột 'video.duration'.")
            return

        # Select a metric to display

        selected_metric = st.segmented_control(
            "Chọn chỉ số để hiển thị boxplot:",
            options=list(COLUMN_METRICS.keys()),
            format_func=lambda x: COLUMN_METRICS.get(x, x), default='statsV2.playCount'
            # index=0
        )

        # Toggle to exclude outliers
        # exclude_outliers = st.checkbox("Loại bỏ outliers", value=True)

        # Call the plot_duration_boxplot function
        plot_duration_boxplot(
            self.filtered_df, metric_column=selected_metric, duration_column='video.duration')

    def display_heatmap_day_hour(self):
        """Display a heatmap of videos by day of the week and hour of the day."""
        st.subheader("Heatmap: Phân phối video theo ngày và giờ")
        if 'createTime' not in self.filtered_df.columns:
            st.warning("Dữ liệu không chứa cột 'video.created_time'.")
            return

        # Select a metric to display
        # selected_metric = st.segmented_control(
        #     "Chọn chỉ số để hiển thị heatmap:",
        #     options=[None] + list(COLUMN_METRICS.keys()),
        #     format_func=lambda x: "Số lượng video" if x is None else COLUMN_METRICS.get(
        #         x, x), default=None
        # )

        # Call the heatmap function
        plot_heatmap_day_hour(
            self.filtered_df, datetime_column='createTime')

    def display_hashtag_count_histogram(self):
        """Display a histogram of the number of hashtags in videos."""
        st.markdown("#### Phân phối số lượng hashtag trong video")
        if 'hashtag_count' not in self.filtered_df.columns:
            st.warning("Dữ liệu không chứa cột 'hashtag_count'.")
            return

        # Call the plot_hashtag_count_histogram function with a fixed x-axis range
        plot_hashtag_count_histogram(
            # Adjust range as needed
            self.filtered_df, hashtag_column='hashtag_count', xaxis_range=[-0.5, 22.5]
        )

    def display_word_per_second_histogram(self):
        """Display a histogram of the word-per-second metric."""
        st.markdown("#### Phân phối Mật độ từ ngữ (số từ/giây)")
        if 'word_per_second' not in self.filtered_df.columns:
            st.warning("Dữ liệu không chứa cột 'word_per_second'.")
            return

        # Call the plot_word_per_second_histogram function
        plot_word_per_second_histogram(
            self.filtered_df, column='word_per_second', xaxis_range=[-0.5, 18.5])

    def display_top_hashtags(self):
        """Display the top 10 most used hashtags as horizontal progress bars."""
        st.markdown("#### Top 10 Hashtags")
        if 'hashtags' not in self.filtered_df.columns or 'author.uniqueId' not in self.filtered_df.columns:
            st.warning(
                "Dữ liệu không chứa cột 'hashtags' hoặc 'author.uniqueId'.")
            return

        # Explode the hashtag column to count individual hashtags
        exploded = self.filtered_df[['hashtags', 'author.uniqueId']].copy()
        exploded = exploded.explode('hashtags').dropna()

        # Get all unique user IDs in lowercase for comparison
        unique_user_ids = set(
            self.filtered_df['author.uniqueId'].str.lower().unique())

        # Exclude hashtags that are similar to any user's unique ID
        exploded = exploded[~exploded['hashtags'].str.lower().isin(
            unique_user_ids)]

        # Count the occurrences of each hashtag
        hashtag_counts = exploded['hashtags'].value_counts().head(10)

        # Calculate the percentage of videos using each hashtag
        total_videos = len(self.filtered_df)
        hashtag_percentages = (hashtag_counts / total_videos) * 100
        # hashtag_percentages = hashtag_counts

        # Prepare data for display
        hashtags = [
            (hashtag, percentage, color)
            for hashtag, percentage, color in zip(
                hashtag_counts.index,
                hashtag_percentages,
                px.colors.qualitative.Plotly[:len(
                    hashtag_counts)]  # Use Plotly colors
            )
        ]

        # Display hashtags as horizontal progress bars
        for tag, percent, color in hashtags:
            st.markdown(
                f"""
                <div style="margin-bottom: 10px;">
                    <div style="display: flex; justify-content: space-between; font-weight: bold;">
                        <span>#{tag}</span>
                        <span>{percent:.1f}%</span>
                    </div>
                    <div style="height: 8px; background-color: #eee; border-radius: 6px;">
                        <div style="width: {percent}%; background-color: {color}; height: 100%; border-radius: 6px;"></div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

    def display_scatter_plot(self):
        """Display a scatter plot for transcript word count and video duration."""
        st.markdown("#### Phân bố: Số lượng từ và Thời lượng video")
        if 'transcript_word_count' not in self.filtered_df.columns or 'video.duration' not in self.filtered_df.columns:
            st.warning(
                "Dữ liệu không chứa cột 'transcript_word_count' hoặc 'video.duration'.")
            return

        # Call the plot_density_scatter function with selected_category
        plot_density_scatter(
            self.filtered_df,
            x_column='transcript_word_count',
            y_column='video.duration',
            selected_category=self.selected_category
        )

    def run(self):
        """Main application flow"""
        # Set up sidebar filters
        self.setup_sidebar()

        # Set up main layout
        self.setup_main_layout()


# Run the application when script is executed
# if __name__ == "__main__":
app = TikTokContentAnalysis()
app.run()
