

import os
import re
import sys
import zipfile
import argparse
import requests
import shutil
from bs4 import BeautifulSoup
from io import BytesIO
from PIL import Image
import time, requests


from typing import Optional, Dict, Any, Union

class RequestSession(requests.Session):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        pass

    def force_get(self, url, headers=None, max_retries=5, delay=2) -> requests.Response | None:
        for retries in range(max_retries):
            try:
                response = self.get(url, timeout=10, headers=headers if headers else self.headers)  # Reduced timeout
                if response.status_code == 404:
                    return None
                response.raise_for_status()
                return response
            
            except requests.RequestException as e:
                if retries == max_retries - 1:
                    raise Exception(f"Failed to retrieve {url} after {max_retries} attempts: {str(e)}")
                time.sleep(delay * (retries + 1))  # Exponential backoff
        return None


 
    

def imread_from_bytes(content):
    img = Image.open(BytesIO(content))
    return img

class MangaChapterDownloader:
    def __init__(self, headers=None):
        self.session = RequestSession()
        self.session.headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36"
   
   
   
    def download_chapter_images(self, chapter_url, title, chapter_name):
        """Download images for one chapter, return list of (local_path, original_filename)"""
        response = self.session.force_get(chapter_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        img_tags = soup.find_all("img")
        # Keep only images from the manga host
        img_tags = [img for img in img_tags if img.get("src") and "media.omegascans.org" in img.get("src")]
        if not img_tags:
            raise ValueError(f"No manga images found at {chapter_url}")

        # Temp dir for this chapter
        temp_dir = f"./temp/{title}/{chapter_name}"
        os.makedirs(temp_dir, exist_ok=True)

        paths = []
        for img in img_tags:
            src = img["src"].strip()
            filename = src.split("/")[-1].split(".")[0] + ".webp"
            out_path = os.path.join(temp_dir, filename)
            img_data = self.session.force_get(src).content
            img = imread_from_bytes(img_data)
            img.save(out_path)
            paths.append(out_path)
            print(f"Downloaded: {chapter_name}/{filename}")
        return paths, temp_dir

    def download_batch(self, title, start_ch, end_ch, base_url_template="https://omegascans.org/series/{}/chapter-{}"):
        """
        Download all chapters from start_ch to end_ch (inclusive).
        Returns path to final ZIP containing all images.
        """
        all_image_paths = []
        temp_dirs = []

        for ch_num in range(start_ch, end_ch + 1):
            chapter_url = base_url_template.format(title, ch_num)
            chapter_name = f"chapter-{ch_num}"
            print(f"\nProcessing {chapter_url}")
            try:
                paths, tmp_dir = self.download_chapter_images(chapter_url, title, chapter_name)
                all_image_paths.extend(paths)
                temp_dirs.append(tmp_dir)
            except Exception as e:
                print(f"⚠️  Skipping {chapter_name}: {e}")

        if not all_image_paths:
            raise RuntimeError("No images downloaded from any chapter.")

        # Create final ZIP
        zip_path = f"{title}.zip"
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for img_path in all_image_paths:
                # Preserve chapter subfolders inside the zip
                rel_path = os.path.relpath(img_path, f"./temp/{title}")
                zipf.write(img_path, arcname=rel_path)



        # Clean up all temp folders
        for tmp_dir in temp_dirs:
            shutil.rmtree(tmp_dir, ignore_errors=True)

        print(f"\n✅ All chapters zipped into {zip_path} (total {len(all_image_paths)} images)")
        return zip_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--title", required=True, help="Manga title (e.g., pickup)")
    parser.add_argument("--start", type=int, required=True, help="First chapter number")
    parser.add_argument("--end", type=int, required=True, help="Last chapter number")
    parser.add_argument("--url-template", default="https://omegascans.org/series/{}/chapter-{}",
                        help="URL template with {} for title and chapter number")
    args = parser.parse_args()

    downloader = MangaChapterDownloader()
    zip_file = downloader.download_batch(args.title, args.start, args.end, args.url_template)
    print(f"Created: {zip_file}")
