# TikTok Analytics Dashboard

A Streamlit-based web application for analyzing TikTok user data, engagement metrics, and trends. This dashboard provides interactive visualizations and insights into follower distributions, top users, engagement levels, personal analytics, and hashtag/song usage patterns.

## Features

- **Correlation Analysis**: Explore relationships between followers, likes, and video counts with histograms, scatter matrices, and correlation heatmaps.
- **Top Users**: Identify influential TikTok users based on likes, video counts, followers, or engagement rates.
- **Engagement Insights**: Analyze how engagement varies across different follower and engagement levels.
- **Personal Analysis**: Dive into an individual TikToker's profile, video trends, music usage, and hashtag patterns.
- **Hashtag & Song Analysis**: Discover the most popular hashtags and songs within a selected date range.
- **Interactive Visualizations**: Built with Plotly for dynamic, customizable charts.
- **Downloadable Data**: Export chart data as CSV files for further analysis.

## Project Structure

```
tiktok_analytics/
│
├── *_app.py                     # Main entry point for the Streamlit app
├── pages/
│   ├── data_loader.py           # Data loading utilities
│   ├── footer.py                # Footer with last updated timestamp
│   └── styles.py                # Custom CSS and styling definitions
├── pages/
│   ├── correlation_analysis.py  # Correlation Analysis page with tabs
│   ├── personal_analysis.py     # Personal Analysis page
│   ├── hashtag_song_analysis.py # Hashtag & Song Analysis page
│   └── top_users.py             # Top user statistic page
└── README.md               # Project documentation (this file)
```

### File Descriptions

- **`*_app.py`**: The main script that initializes the app, sets up the sidebar navigation, and routes to different pages.
- **`styles.py`**: Contains custom CSS for consistent styling across the app, including global, personal, and hashtag/song-specific styles.
- **`data_loader.py`**: Loads the cleaned TikTok user and video datasets from CSV files.
- **`footer.py`**: Displays a timestamp in Vietnam time (UTC+7) at the bottom of the app.
- **`correlation_analysis.py`**: Implements the "Correlation Analysis" page with three tabs: Correlation Analysis, Top Users, and Engagement Insights.
- **`personal_analysis.py`**: Implements the "Personal Analysis" page for individual TikToker analytics.
- **`hashtag_song_analysis.py`**: Implements the "Hashtag & Song Analysis" page for trending hashtags and songs.

## Prerequisites

- Python 3.8+
- Required Python packages:
  - `streamlit`
  - `pandas`
  - `plotly`
  - `pytz`

## Installation

1. **Clone the Repository** (if hosted on a version control system):

   ```bash
   git clone <repository-url>
   cd tiktok_analytics
   ```

   Alternatively, manually create the directory structure and copy the files.

2. **Install Dependencies**:

   ```bash
   pip install streamlit pandas plotly pytz
   ```

3. **Prepare Data**:
   - Place your `cleaned_user_info.csv` and `cleaned_video_info.csv` files in the directory `/content/21KHDL-TikTok-Analytics/data/interim/`.
   - Update the file paths in `data_loader.py` if your data is stored elsewhere.

## Running the Application

1. Navigate to the project directory:
   ```bash
   cd tiktok_analytics
   ```
2. Run the Streamlit app:
   ```bash
   streamlit run app.py
   ```
3. Open your browser to `http://localhost:8501` to view the dashboard.

## Usage

- **Sidebar Navigation**: Use the radio buttons in the sidebar to switch between pages: "Correlation Analysis", "Personal Analysis", and "Hashtag & Song Analysis".
- **Interactive Controls**: Adjust sliders, dropdowns, and checkboxes to customize visualizations.
- **Download Data**: Click the "Download" buttons to export chart data as CSV files.
- **Date Range Filtering**: Available in "Personal Analysis" and "Hashtag & Song Analysis" pages to focus on specific time periods.

### Example Screenshots

_(You can add screenshots here by running the app and capturing outputs, then linking them in this section.)_

## Data Requirements

- **`cleaned_user_info.csv`**:
  - Expected columns: `stats.followerCount`, `stats.heart`, `stats.videoCount`, `user.uniqueId`, etc.
- **`cleaned_video_info.csv`**:
  - Expected columns: `createTime`, `author.uniqueId`, `authorStats.followerCount`, `authorStats.heartCount`, `authorStats.videoCount`, `author.verified`, `music.authorName`, `hashtags`, etc.
- Ensure the data is pre-cleaned and formatted correctly for the app to function as expected.

## Contributing

1. Fork the repository (if applicable).
2. Create a new branch for your feature or bug fix:
   ```bash
   git checkout -b feature-name
   ```
3. Make changes and test locally.
4. Commit and push your changes:
   ```bash
   git commit -m "Description of changes"
   git push origin feature-name
   ```
5. Submit a pull request with a detailed description of your changes.

## Notes

- The app assumes the data files are available at the specified paths. Adjust `data_loader.py` if your file locations differ.
- The "Last updated" timestamp reflects Vietnam time (Asia/Ho_Chi_Minh timezone).
- For large datasets, rendering times may increase; consider optimizing data loading or adding caching with `st.cache`.

## License

This project is open-source and available under the [MIT License](LICENSE). _(Add a LICENSE file if you choose to include one.)_

## Contact

For questions or feedback, feel free to reach out to the maintainers at [hddluc21@fitus.clc.edu.com].
