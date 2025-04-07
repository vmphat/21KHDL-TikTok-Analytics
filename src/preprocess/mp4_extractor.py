import ffmpeg
import pytesseract
import cv2
import os
import pandas as pd
import argparse
from glob import glob

# Configure Tesseract OCR path (Windows only)
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def find_mp4_files(base_path):
    """Find all MP4 files recursively."""
    return glob(os.path.join(base_path, "**", "*.mp4"), recursive=True)

def extract_subtitles(mp4_file, output_srt):
    """Extracts subtitles from an MP4 file if they exist."""
    try:
        ffmpeg.input(mp4_file).output(output_srt, format='srt').run(overwrite_output=True, quiet=True)
        if os.path.exists(output_srt):
            print(f"[✔] Extracted subtitles from {mp4_file}")
            with open(output_srt, "r", encoding="utf-8") as f:
                return f.read()
    except Exception:
        pass
    return "No subtitles found" 

def extract_frames(mp4_file, output_folder, fps=1):
    """Extracts frames from a video for OCR subtitle detection."""
    os.makedirs(output_folder, exist_ok=True)
    frame_pattern = os.path.join(output_folder, "frame_%04d.png")
    try:
        ffmpeg.input(mp4_file).output(frame_pattern, vf=f"fps={fps}").run(overwrite_output=True, quiet=True)
        return sorted(glob(os.path.join(output_folder, "*.png")))  # Return list of frame paths
    except Exception as e:
        print(f"[✘] Error extracting frames from {mp4_file}: {e}")
        return ["Error extracting frames"]
        
        
def get_video_duration(mp4_file):
    """Get video duration in seconds using ffmpeg."""
    try:
        probe = ffmpeg.probe(mp4_file)
        duration = float(probe['format']['duration'])
        return duration
    except Exception as e:
        print(f"[✘] Error getting duration for {mp4_file}: {e}")
        return 0

def ocr_subtitles(frame_paths):
    """Uses Tesseract OCR to extract subtitles from frames."""
    subtitle_texts = []
    for img_path in frame_paths:
        img = cv2.imread(img_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        text = pytesseract.image_to_string(gray, lang="eng+vie")  # Supports English & Vietnamese
        if text.strip():
            subtitle_texts.append(text)
    
    return "\n".join(subtitle_texts) if subtitle_texts else "No subtitles found" 


def process_videos(raw_video_path, processed_path):
    """Finds all MP4 files, extracts subtitles, and saves results to CSV."""
    os.makedirs(processed_path, exist_ok=True)
    csv_output = os.path.join(processed_path, "subtitles.csv")

    video_files = find_mp4_files(raw_video_path)
    results = []

    for video in video_files:
        print(f"Processing: {video}")

        base_name = os.path.splitext(os.path.basename(video))[0]
        subtitle_file = os.path.join(processed_path, f"{base_name}.srt")
        frame_folder = os.path.join(processed_path, f"{base_name}_frames")
        duration = get_video_duration(video)
        # Step 1: Try extracting soft subtitles
        subtitles = extract_subtitles(video, subtitle_file)

        # Step 2: If no subtitles found, try OCR, video duration
        if not subtitles:
            frame_paths = extract_frames(video, frame_folder, fps=1)
            subtitles = ocr_subtitles(frame_paths)

        # Step 3: Store results
        if subtitles:
            results.append({"video_path": video, "duration_seconds": duration, "subtitle_text": subtitles})
        else:
            results.append({"video_path": 'video', "duration_seconds": '0', "subtitle_text": "None"})

    # Step 4: Save to CSV
    df = pd.DataFrame(results)
    df.head(10)
    df.to_csv(csv_output, index=False, encoding="utf-8")
    print(f"[✔] Subtitles saved to {csv_output}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract subtitles from MP4 files.")
    parser.add_argument("raw_video_path", type=str, help="Path to the folder containing MP4 files.")
    parser.add_argument("processed_path", type=str, help="Path to the folder where results will be saved.")

    args = parser.parse_args()
    process_videos(args.raw_video_path, args.processed_path)
