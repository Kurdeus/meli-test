import argparse
import subprocess

def get_direct_download_url(video_url, output_txt="link.txt"):
    """استخراج لینک دانلود مستقیم از Pornhub"""
    
    cmd = [
        "yt-dlp",
        "--get-url",  # فقط لینک مستقیم رو بده
        "--format", "best[height<=1080]",  # کیفیت مناسب
        video_url,
        "--referer", "https://www.pornhub.com/"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0 and result.stdout.strip():
        direct_url = result.stdout.strip()
        
        # ذخیره در فایل txt
        with open(output_txt, "w", encoding="utf-8") as f:
            f.write(f"Original URL: {video_url}\n")
            f.write(f"Direct Download: {direct_url}\n")
        
        print(f"✅ لینک مستقیم ذخیره شد: {output_txt}")
        print(f"لینک: {direct_url}")
        return direct_url
    else:
        print("❌ خطا در استخراج لینک")
        print(result.stderr)
        return None



def main():
    parser = argparse.ArgumentParser(description="Download file from URL and split into two ZIPs")
    parser.add_argument("--url", required=True, help="Direct file download URL")
    
    args = parser.parse_args()
    get_direct_download_url(args.url)

if __name__ == "__main__":
    main()
