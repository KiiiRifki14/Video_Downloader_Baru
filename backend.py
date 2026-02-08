import yt_dlp
import instaloader
import os
import shutil
import uuid
from pathlib import Path

# --- INFO VIDEO ---
def get_video_info(url):
    try:
        if "instagram.com" in url:
            return {"title": "Instagram Post", "thumbnail": None, "duration_string": "Slide/Carousel", "ext": "mp4/jpg"}
        
        ydl_opts = {"quiet": True, "skip_download": True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return info
    except Exception as e:
        return None

# --- ENGINE DOWNLOAD (RETURN LIST FILE) ---
def download_video(url):
    # Buat folder unik
    unique_id = str(uuid.uuid4())
    base_folder = Path("temp_downloads")
    target_dir = base_folder / unique_id
    target_dir.mkdir(parents=True, exist_ok=True)

    found_files = [] # Kita akan menampung semua file disini

    try:
        # === KASUS 1: INSTAGRAM (Bisa Banyak File) ===
        if "instagram.com" in url:
            L = instaloader.Instaloader(
                save_metadata=False, 
                download_videos=True,
                download_video_thumbnails=False,
                download_geotags=False, 
                download_comments=False,
                compress_json=False
            )
            
            # Ambil shortcode
            if "/p/" in url: shortcode = url.split("/p/")[1].split("/")[0]
            elif "/reel/" in url: shortcode = url.split("/reel/")[1].split("/")[0]
            else: return []

            post = instaloader.Post.from_shortcode(L.context, shortcode)
            L.download_post(post, target=target_dir)

        # === KASUS 2: YOUTUBE/TIKTOK (Biasanya 1 File) ===
        else:
            outtmpl = str(target_dir / "%(title)s.%(ext)s")
            ydl_opts = {
                "outtmpl": outtmpl,
                "quiet": True,
                "noplaylist": True,
                "format": "best",
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
        
        # === SCAN FOLDER HASIL ===
        # Ambil semua file JPG dan MP4
        for f in os.listdir(target_dir):
            if f.endswith(('.jpg', '.png', '.jpeg', '.mp4', '.webm')):
                full_path = str(target_dir / f)
                found_files.append(full_path)
        
        # Urutkan file biar rapi (opsional)
        found_files.sort()
        
        return found_files # Mengembalikan LIST (Daftar file), bukan cuma 1 string

    except Exception as e:
        print(f"Error: {e}")
        return []