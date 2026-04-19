#!/usr/bin/env python3
"""
Download a single URL as an HTML file and pack it into a ZIP.
Usage:
    python download_html.py --url "https://example.com/page" --output "my_page"
"""

import os
import argparse
import zipfile
import requests

def download_and_zip(url, output_name):
    """
    Fetch the HTML content from `url`, save it as `{output_name}.html`,
    then create `{output_name}.zip` containing that file.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    # Download the page
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    resp.encoding = resp.apparent_encoding  # preserve correct encoding

    # Save HTML file
    html_filename = f"{output_name}.html"
    with open(html_filename, "w", encoding="utf-8") as f:
        f.write(resp.text)
    print(f"Saved: {html_filename}")

    # Create ZIP
    zip_filename = f"{output_name}.zip"
    with zipfile.ZipFile(zip_filename, 'w') as zipf:
        zipf.write(html_filename)
    print(f"Zipped: {zip_filename}")

    # Remove the loose HTML file
    os.remove(html_filename)
    return zip_filename

def main():
    parser = argparse.ArgumentParser(description="Download an HTML page and zip it.")
    parser.add_argument("--url", required=True, help="Full URL to download")
    parser.add_argument("--output", required=True, help="Base name for output files (no extension)")
    args = parser.parse_args()

    zip_file = download_and_zip(args.url, args.output)
    print(f"✅ Created: {zip_file}")

if __name__ == "__main__":
    main()
