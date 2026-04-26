import argparse
import subprocess
import os
from pathlib import Path

def download_video(url, output_dir="ph-dl"):
    """دانلود ویدیو در پوشه ph-dl"""
    
    # ساخت پوشه
    Path(output_dir).mkdir(exist_ok=True)
    
    cmd = [
        "yt-dlp",
        url,
        "-o", f"{output_dir}/%(uploader)s - %(title)s.%(ext)s",  # نام فایل بهتر
        "--referer", "https://www.pornhub.com/",
        "--format", "best[height<=1080]/best"
    ]
    
    print(f"⬇️ دانلود شروع شد...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"✅ دانلود تمام شد: {output_dir}/")
        return True
    else:
        print("❌ خطا در دانلود")
        print(result.stderr)
        return False

def get_direct_url(url, output_txt="link.txt"):
    """استخراج لینک مستقیم"""
    cmd = [
        "yt-dlp", "--get-url",
        "--format", "best[height<=1080]",
        url, "--referer", "https://www.pornhub.com/"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0 and result.stdout.strip():
        direct_url = result.stdout.strip()
        with open(output_txt, "w", encoding="utf-8") as f:
            f.write(f"Direct URL: {direct_url}\n")
        print(f"🔗 لینک مستقیم: {output_txt}")
        return direct_url
    return None

def main():
    parser = argparse.ArgumentParser(description="Pornhub Downloader")
    parser.add_argument("--url", "-u", required=True, help="Video URL")
    
    args = parser.parse_args()
    
    download_video(args.url)

if __name__ == "__main__":
    main()
