import re
import subprocess
import argparse
from pathlib import Path

# ======================
# Configuration
# ======================
DOWNLOADS_FOLDER = Path("downloads")

def download_video(url):
    """Download single video with metadata"""
    DOWNLOADS_FOLDER.mkdir(parents=True, exist_ok=True)
    
    print(f"Downloading to: {DOWNLOADS_FOLDER}")
    
    subprocess.run([
        "yt-dlp",
        "--ignore-errors",
        "--no-warnings",
        "--referer", "https://www.pornhub.com/",
        "-o", "%(id)s.%(ext)s",
        "--embed-metadata",
        "--embed-thumbnail",
        "--no-overwrites",
        url
    ], cwd=DOWNLOADS_FOLDER)

def main():
    parser = argparse.ArgumentParser(description="Pornhub Downloader")
    parser.add_argument("--url", "-u", required=True, help="Video URL")
    
    args = parser.parse_args()
    
    try:
        download_video(args.url)
    except KeyboardInterrupt:
        pass
    finally:
        print("Download complete!")

if __name__ == "__main__":
    main()
