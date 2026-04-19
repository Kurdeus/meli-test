#!/usr/bin/env python3
"""
Manga Chapter Downloader + Zipper
Usage:
    python download_chapter.py --url "https://example.com/manga/chapter-1" --title "my_manga" --chapter "ch_001"
"""

import os
import re
import sys
import zipfile
import argparse
import requests
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

        # 2. Find the image container (adjust class if needed)
        container = soup.find("div", class_="read-container")
        if not container:
            raise ValueError(f"No <div class='read-container'> found at {chapter_url}")

        img_tags = container.find_all("img")
        if not img_tags:
            raise ValueError("No images found inside the container")

        # 3. Prepare temp directory
        temp_dir = f"./temp/{title}/{chapter_name}"
        os.makedirs(temp_dir, exist_ok=True)

        # 4. Download each image with zero‑padded numbering
        image_paths = []
        for img in img_tags:
            src = img.get("src")
            if not src:
                continue
            src = src.strip()
            # Extract number from filename (e.g., '5.jpg' -> '5')
            filename = src.split("/")[-1]
            base = filename.split(".")[0]
            if len(base) == 1:
                padded = base.zfill(2)
            else:
                padded = base
            out_name = f"{padded}.jpg"
            out_path = os.path.join(temp_dir, out_name)

            # Download and save
            img_data = requests.get(src, headers=self.headers).content
            with open(out_path, "wb") as f:
                f.write(img_data)
            image_paths.append(out_path)
            print(f"Downloaded: {out_name}")

        # 5. Create ZIP file
        zip_path = f"./{title}_{chapter_name}.zip"
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for img_path in image_paths:
                zipf.write(img_path, arcname=os.path.basename(img_path))

        # 6. Clean up temp folder (optional)
        # import shutil; shutil.rmtree(temp_dir)

        print(f"\n✅ ZIP created: {zip_path} (contains {len(image_paths)} images)")
        return zip_path


URLS = [

"https://omegascans.org/series/pickup/chapter-{}".format(i) for i in range(21, 36)

]
downloader = MangaChapterDownloader()
for url in URLS:
    zip_file = downloader.download_images(url, "pickup", url.split("/")[-1])
