import json
import csv
import pandas as pd
from datetime import datetime

def extract_tiktok_fields(nested_json):
    """Extract and flatten key fields for TikTok analysis."""
    extracted = {}

    # Core Metadata
    extracted["video_id"] = nested_json.get("id")
    extracted["create_time"] = datetime.fromtimestamp(nested_json.get("createTime", 0)).strftime('%Y-%m-%d %H:%M:%S')
    extracted["description"] = nested_json.get("desc", "")
    extracted["text_language"] = nested_json.get("textLanguage", "")
    
    # Author Details
    author = nested_json.get("author", {})
    extracted["author_id"] = author.get("id")
    extracted["author_name"] = author.get("nickname")
    extracted["author_followers"] = nested_json.get("authorStats", {}).get("followerCount", 0)
    
    # Engagement Metrics
    stats = nested_json.get("stats", {})
    extracted["views"] = stats.get("playCount", 0)
    extracted["likes"] = stats.get("diggCount", 0)
    extracted["comments"] = stats.get("commentCount", 0)
    extracted["shares"] = stats.get("shareCount", 0)
    
    # Content Details
    music = nested_json.get("music", {})
    extracted["music_title"] = music.get("title", "")
    extracted["video_duration"] = nested_json.get("video", {}).get("duration", 0)
    
    # Hashtags & Challenges
    challenges = [challenge.get("title", "") for challenge in nested_json.get("challenges", [])]
    extracted["challenges"] = ", ".join(challenges)
    
    text_extra = [tag.get("hashtagName", "") for tag in nested_json.get("textExtra", [])]
    extracted["hashtags"] = ", ".join(text_extra)

    # Ad/Technical Metadata
    extracted["is_ad"] = nested_json.get("isAd", False)
    extracted["video_bitrate"] = nested_json.get("video", {}).get("bitrate", 0)
    
    return extracted

def json_to_csv_filtered(json_data, output_file):
    """Convert JSON data to CSV with filtered TikTok fields."""
    # Handle single dictionary or list of dictionaries
    if isinstance(json_data, dict):
        json_data = [json_data]
    
    # Extract key TikTok fields
    filtered_data = [extract_tiktok_fields(x) for x in json_data]
    
    # Write to CSV
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=filtered_data[0].keys())
        writer.writeheader()
        writer.writerows(filtered_data)
        print(f"CSV file '{output_file}' created with TikTok-specific fields!")

# File paths (update these)
input_file = 'C:/Users/nguye/OneDrive/Tài liệu/GitHub/21KHDL-TikTok-Analytics/data/raw/videos/banphimco/videos_info.json'
output_file = 'tiktok_analysis_cleaned.csv'

try:
    # Read JSON data
    with open(input_file, 'r', encoding='utf-8') as f:
        json_data = json.load(f)
    
    # Convert to CSV (filtered fields)
    json_to_csv_filtered(json_data, output_file)
    
    # Load CSV and display stats
    df = pd.read_csv(output_file)
    
    print("\nDataset Info:")
    print(df.info())
    
    print("\nFirst 5 rows:")
    print(df.head())
    
    print("\nBasic Statistics:")
    print(df.describe())

except FileNotFoundError:
    print(f"Error: File '{input_file}' not found!")
except json.JSONDecodeError:
    print("Error: Invalid JSON format!")
except Exception as e:
    print(f"Unexpected error: {str(e)}")