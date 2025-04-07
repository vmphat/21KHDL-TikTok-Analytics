import pandas as pd
import numpy as np
import streamlit as st
from itertools import chain
from types import NoneType
from video_analysis.utils.chart import plot_bar_chart, plot_radar_chart, generate_color_map
from video_analysis.utils.config import COLUMN_LABELS, COLUMN_METRICS, STAT_TYPES


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
        stats = {
            # 'mean_word_count': int(df['transcript_word_count'].mean()),
            'mean_duration': (df['video.duration'].mean()),
            'duration_min_q': df['video.duration'].quantile(0.25),
            'duration_max_q': df['video.duration'].quantile(0.75),
            'mean_word_per_second': df['word_per_second'].mean(),
            'mean_hashtag_count': (df['hashtag_count'].mean()),
            'hashtag_count_min_q': df['hashtag_count'].quantile(0.25),
            'hashtag_count_max_q': df['hashtag_count'].quantile(0.75),

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
        category_options = ['Tổng quan'] + self.df['categories'].dropna(
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

        if self.selected_category == 'Tổng quan':
            return

        if self.selected_category:
            self.filtered_df = self.filtered_df[self.filtered_df['categories']
                                                == self.selected_category]

    def setup_main_layout(self):
        """Setup main page layout and components"""
        self.personal_styles()
        stats = self._calculate_statistics(self.filtered_df)

        cat_text = self.selected_category if self.selected_category else "Tổng quan"
        st.title(f"📊 Phân tích nội dung: {cat_text}")
        with st.container():
            st.subheader("Các chỉ sổ trung bình")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(
                    "Thời lượng", f"{int(stats['mean_duration']//60)} phút {int(stats['mean_duration']%60)} giây")
                # st.metric(
                #     "Followers", f"{user_info['authorStats.followerCount']:,}")
            with col2:
                st.metric(
                    "Số lượng hashtag", f"{int(stats['hashtag_count_min_q'])} - {int(stats['hashtag_count_max_q'])}")
                # st.metric("Total Likes",
                #           f"{user_info['authorStats.heartCount']:,}")
            with col3:
                st.metric("Tốc độ nói",
                          f"{round(stats['mean_word_per_second'],1)} từ/giây")
                # st.metric("Total Videos",
                #           f"{user_info['authorStats.videoCount']:,}")

        # st.header(header_text)
        st.subheader("Về nội dung video")

        # Field selection
        self.selected_field = st.selectbox(
            "Chọn trường cần hiển thị biểu đồ:",
            options=self.fields_to_analyze,
            format_func=lambda x: COLUMN_LABELS.get(x, x),
        )

        # Generate color map for consistency across charts
        labels = self.filtered_df[self.selected_field].explode(
        ).dropna().unique().tolist()
        self.color_map = generate_color_map(labels)

        # Display performance metrics section
        self.display_performance_metrics()

    def display_performance_metrics(self):
        """Display performance metrics section with charts"""
        st.subheader(
            f"Hiệu suất tương tác theo {COLUMN_LABELS.get(self.selected_field, self.selected_field)}")

        # Create two columns for charts
        col1, col2 = st.columns(2)

        with col1:
            self.display_bar_chart(col1)

        with col2:
            self.display_radar_chart(col2)

    def display_bar_chart(self, container):
        """Display bar chart with controls"""
        # Performance metric selection
        selected_metric = st.selectbox(
            "Chỉ số hiệu suất:",
            options=list(COLUMN_METRICS.keys()),
            format_func=lambda x: COLUMN_METRICS.get(x, x)
        )

        # Statistic type selection
        stat_type = st.radio(
            "Loại thống kê:",
            options=list(STAT_TYPES.keys()),
            format_func=lambda x: STAT_TYPES.get(x, x),
            horizontal=True
        )

        # Generate and display bar chart
        fig = plot_bar_chart(
            self.filtered_df,
            self.selected_field,
            selected_metric,
            stat_type,
            color_map=self.color_map
        )

        if fig:
            st.plotly_chart(fig, use_container_width=True, key="bar_chart")

    def display_radar_chart(self, container):
        """Display radar chart with controls"""
        # Prepare data for radar chart
        exploded = self.filtered_df.copy()
        exploded = exploded.explode(self.selected_field).dropna(
            subset=[self.selected_field])
        labels = exploded[self.selected_field].unique()

        # Label selection for radar chart
        selected_labels = st.multiselect(
            "Chọn label để hiển thị radar chart:",
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
