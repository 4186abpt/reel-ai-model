import cv2
import os
import pandas as pd
from moviepy.editor import VideoFileClip
from tqdm import tqdm

def extract_video_features(video_path):
    cap = cv2.VideoCapture(video_path)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    duration = frame_count / fps if fps > 0 else 0

    brightness_vals = []
    motion_vals = []

    ret, prev_frame = cap.read()
    while ret:
        gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
        brightness_vals.append(gray.mean())

        ret, next_frame = cap.read()
        if not ret:
            break
        diff = cv2.absdiff(prev_frame, next_frame)
        motion_vals.append(diff.mean())
        prev_frame = next_frame

    cap.release()

    return {
        "file": os.path.basename(video_path),
        "duration": duration,
        "avg_brightness": sum(brightness_vals)/len(brightness_vals),
        "avg_motion": sum(motion_vals)/len(motion_vals)
    }

def process_all_videos(raw_dir="data/raw", out_path="data/processed/features.csv"):
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    videos = [os.path.join(raw_dir, f) for f in os.listdir(raw_dir) if f.endswith(('.mp4', '.mov'))]

    all_features = [extract_video_features(v) for v in tqdm(videos)]
    df = pd.DataFrame(all_features)
    df.to_csv(out_path, index=False)
    print(f"Saved features for {len(df)} videos → {out_path}")

if __name__ == "__main__":
    process_all_videos()

