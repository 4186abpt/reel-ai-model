import instaloader
import pathlib
import sys

# Add project root to sys.path to find config.py
sys.path.append(str(pathlib.Path(__file__).resolve().parent.parent))
import config

REEL_URLS = ["https://www.instagram.com/reel/CghLb3zKvzJ/",
             "https://www.instagram.com/reel/CgGcQCDo0tm/"]

# Ensure the target directory exists
config.RAW_PENDING_DIR.mkdir(parents=True, exist_ok=True)
for url in REEL_URLS:
    L = instaloader.Instaloader(download_video_thumbnails=False, save_metadata=False)
    L.download_post(instaloader.Post.from_shortcode(L.context, url.split("/")[-2]), target=config.RAW_PENDING_DIR)
