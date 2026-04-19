#!/usr/bin/env python3
"""
Manga Chapter Downloader + Zipper (generic image finder)
Usage:
    python download_chapter.py --url "https://example.com/manga/chapter-1" --title "my_manga" --chapter "ch_001"
"""

import os
import re
import sys
import zipfile
import argparse
import requests
import shutil
from bs4 import BeautifulSoup

class MangaChapterDownloader:
    def __init__(self, headers=None):
        self.headers = headers or {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36"
        }

    def download_images(self, chapter_url, title, chapter_name):
        """
        Download all images from the chapter page and return the path of the created ZIP file.
        """
        # 1. Fetch the chapter page
        response = requests.get(chapter_url, headers=self.headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        # 2. Find all img tags (no specific container needed)
        # Optionally filter by domain to avoid ads/logo
        img_tags = soup.find_all("img")
        if not img_tags:
            raise ValueError(f"No <img> tags found at {chapter_url}")

        # Optionally keep only images from the manga host (e.g., omegascans)
        img_tags = [img for img in img_tags if img.get("src") and "media.omegascans.org" in img.get("src")]
        if not img_tags:
            raise ValueError("No manga images found (filtered by domain 'media.omegascans.org')")

        # 3. Prepare temp directory
        temp_dir = f"./temp/{title}/{chapter_name}"
        os.makedirs(temp_dir, exist_ok=True)

        # 4. Download each image preserving original filename (order = appearance)
        image_paths = []
        for img in img_tags:
            src = img.get("src").strip()
            # Extract filename from URL (e.g., PU19-01.jpg)
            filename = src.split("/")[-1]
            out_path = os.path.join(temp_dir, filename)

            # Download and save
            img_data = requests.get(src, headers=self.headers).content
            with open(out_path, "wb") as f:
                f.write(img_data)
            image_paths.append(out_path)
            print(f"Downloaded: {filename}")

        # 5. Create ZIP file
        zip_path = f"./{title}_{chapter_name}.zip"
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for img_path in image_paths:
                zipf.write(img_path, arcname=os.path.basename(img_path))

        # 6. Clean up temp folder
        shutil.rmtree(temp_dir)

        print(f"\n✅ ZIP created: {zip_path} (contains {len(image_paths)} images)")
        return zip_path



URLS = [

"https://omegascans.org/series/pickup/chapter-{}".format(i) for i in range(21, 36)

]
downloader = MangaChapterDownloader()
for url in URLS:
    print(url)
    zip_file = downloader.download_images(url, "pickup", url.split("/")[-1])
