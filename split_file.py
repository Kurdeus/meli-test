import argparse
import zipfile
import os
import requests
from urllib.parse import urlparse

def download_and_split(url, output_folder="output", size_mb1=90):
    """
    Downloads file from URL and splits into two zip files.
    """
    os.makedirs(output_folder, exist_ok=True)
    
    # Download file
    filename = os.path.basename(urlparse(url).path) or "downloaded_file"
    filepath = os.path.join(output_folder, filename)
    
    print(f"Downloading {url}...")
    response = requests.get(url, stream=True)
    response.raise_for_status()
    
    file_size = int(response.headers.get('content-length', 0)) / (1024 * 1024)
    print(f"File size: {file_size:.1f} MB")
    
    # Save original file temporarily
    with open(filepath, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    
    # Split into zips
    size1_bytes = size_mb1 * 1024 * 1024
    output_zip1 = os.path.join(output_folder, f"part1_{size_mb1}mb.zip")
    output_zip2 = os.path.join(output_folder, "part2_remainder.zip")
    
    print(f"First zip: {size_mb1} MB, Second zip: {file_size-size_mb1:.1f} MB")
    
    with open(filepath, 'rb') as f:
        # First zip
        with zipfile.ZipFile(output_zip1, 'w', zipfile.ZIP_DEFLATED) as z1:
            data1 = f.read(size1_bytes)
            z1.writestr('part1.bin', data1)
        
        # Second zip (remainder)
        f.seek(size1_bytes)  # Reset to split point
        data2 = f.read()
        with zipfile.ZipFile(output_zip2, 'w', zipfile.ZIP_DEFLATED) as z2:
            z2.writestr('part2.bin', data2)
    
    # Cleanup original file
    os.remove(filepath)
    
    print(f"Created: {output_zip1} ({os.path.getsize(output_zip1)/(1024*1024):.1f} MB)")
    print(f"Created: {output_zip2} ({os.path.getsize(output_zip2)/(1024*1024):.1f} MB)")

def main():
    parser = argparse.ArgumentParser(description="Download file from URL and split into two ZIPs")
    parser.add_argument("--url", required=True, help="Direct file download URL")
    parser.add_argument("--output-folder", default="output", help="Output folder name")
    parser.add_argument("--size-mb1", type=int, default=90, help="Size of first zip (MB)")
    
    args = parser.parse_args()
    download_and_split(args.url, args.output_folder, args.size_mb1)

if __name__ == "__main__":
    main()
