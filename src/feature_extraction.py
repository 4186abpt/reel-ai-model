import cv2
import os
import shutil # Import shutil for moving files
import pandas as pd
from moviepy.editor import VideoFileClip # Not used in extract_video_features, but kept for context
from tqdm import tqdm
from pathlib import Path
from multiprocessing import Pool
import sys
sys.path.append(str(Path(__file__).resolve().parent.parent))
import config

def extract_video_features(video_path: Path):
    """Extracts basic visual and motion features from a video file."""
    # Ensure video_path is a string for cv2.VideoCapture
    cap = cv2.VideoCapture(str(video_path)) 
    
    # Check if the video opened successfully
    if not cap.isOpened():
        print(f"Error opening video file: {video_path}")
        return None

    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    duration = frame_count / fps if fps > 0 else 0

    brightness_vals = []
    motion_vals = []

    ret, prev_frame = cap.read()
    while ret:
        # Brightness (mean of grayscale frame)
        gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
        brightness_vals.append(gray.mean())

        ret, next_frame = cap.read()
        if not ret:
            break
            
        # Motion (mean difference between frames)
        diff = cv2.absdiff(prev_frame, next_frame)
        motion_vals.append(diff.mean())
        
        prev_frame = next_frame

    cap.release()

    if not brightness_vals:
        return None # Handle case where video was empty

    return {
        "file": video_path.name,
        "duration": duration,
        "avg_brightness": sum(brightness_vals)/len(brightness_vals),
        "avg_motion": sum(motion_vals)/len(motion_vals),
        "label": 0  # Placeholder label
    }

def process_all_videos():
    """
    Processes videos from raw/pending and moves them to raw/completed upon success.
    """
    # Define project root and directories using pathlib
    # PROJECT_ROOT = Path(__file__).resolve().parent.parent
    # RAW_DIR = PROJECT_ROOT / raw_dir_name
    
    PENDING_DIR = config.RAW_PENDING_DIR
    COMPLETED_DIR = config.RAW_COMPLETED_DIR
    OUT_PATH = config.FEATURES_CSV
    
    # Create necessary directories
    PENDING_DIR.mkdir(parents=True, exist_ok=True)
    COMPLETED_DIR.mkdir(parents=True, exist_ok=True)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    # List video files in the pending directory
    video_extensions = ('.mp4', '.mov', '.avi', '.webm')
    videos_to_process = [f for f in PENDING_DIR.iterdir() if f.suffix in video_extensions]
    
    if not videos_to_process:
        print(f"No videos found in {PENDING_DIR} to process.")
        return
    
    # Use half of the available CPU cores for the Pool OR 1 if only one core is available
    num_processes = os.cpu_count() // 2
    if num_processes == 0: num_processes = 1

    successful_features = []
    processed_paths = []
    
    # Use a Pool to distribute the work
    with Pool(processes=num_processes) as pool:
        # Use imap for results to come back in order, and wrap with tqdm for a progress bar
        results = list(tqdm(
            pool.imap(extract_video_features, videos_to_process),
            total=len(videos_to_process),
            desc=f"Extracting Features with {num_processes} processes"
        ))

    # Consolidate Results and Move Files
    for features, video_path in zip(results, videos_to_process):
        if features:
            successful_features.append(features)
            processed_paths.append(video_path)

    print(f"\nSuccessfully extracted features for {len(successful_features)} videos.")

    # Move all successfully processed files
    for video_path in processed_paths:
        new_path = COMPLETED_DIR / video_path.name
        try:
            shutil.move(str(video_path), str(new_path))
        except Exception as e:
            print(f"Error moving {video_path.name}: {e}")    

    # Save features to CSV
    if successful_features:
        if OUT_PATH.exists() and OUT_PATH.stat().st_size > 0:
            # Use Python's built-in file handling to ensure a newline is present
            try:
                with open(OUT_PATH, 'a') as f:
                    # Explicitly write a newline character
                    f.write('\n')
            except Exception as e:
                print(f"Warning: Could not ensure newline in CSV file: {e}")

        df = pd.DataFrame(successful_features)
        df.to_csv(OUT_PATH, mode='a', header=not OUT_PATH.exists(), index=False, lineterminator='\n')
        print(f"\nSaved features for {len(df)} videos → {OUT_PATH}")
    else:
        print("\nNo features were successfully extracted and saved.")

if __name__ == "__main__":
    process_all_videos()
