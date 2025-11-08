import instaloader

L = instaloader.Instaloader(download_video_thumbnails=False, save_metadata=False)
reel_url = "https://www.instagram.com/reel/C7kvv14gAbw/"
L.download_post(instaloader.Post.from_shortcode(L.context, reel_url.split("/")[-2]), target="./data/raw")
