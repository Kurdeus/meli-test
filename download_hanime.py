import os
import sys
import re
import httpx
import m3u8
from Crypto.Cipher import AES

def get_video_info(slug: str):
    url = f"https://hanime.tv/api/v8/video?id={slug}"
    resp = httpx.get(url, timeout=30)
    resp.raise_for_status()
    return resp.json()

def select_stream(streams):
    """Pick best stream: 720p if available, else 480p, else highest available."""
    # Map height to priority
    priority = {"720": 2, "480": 1}
    best = None
    best_priority = -1
    for stream in streams:
        height = str(stream.get('height', '0'))
        prio = priority.get(height, 0)
        if prio > best_priority:
            best_priority = prio
            best = stream
    if best is None:
        raise RuntimeError("No suitable stream found")
    return best

def download_video(stream_url, output_path):
    """Download and decrypt HLS stream into MP4 file."""
    # Get master playlist
    master = m3u8.loads(httpx.get(stream_url).text)
    # Use the first (and usually only) variant
    if master.playlists:
        playlist_url = master.playlists[0].uri
        if not playlist_url.startswith('http'):
            # Resolve relative URL
            base = stream_url.rsplit('/', 1)[0]
            playlist_url = f"{base}/{playlist_url}"
        playlist = m3u8.loads(httpx.get(playlist_url).text)
    else:
        playlist = master

    # Get decryption key
    if playlist.keys and playlist.keys[0]:
        key_uri = playlist.keys[0].uri
        if not key_uri.startswith('http'):
            base = stream_url.rsplit('/', 1)[0]
            key_uri = f"{base}/{key_uri}"
        key_data = httpx.get(key_uri).content
        cipher = AES.new(key_data, AES.MODE_CBC)
    else:
        cipher = None  # No encryption

    # Download segments sequentially
    total = len(playlist.segments)
    with open(output_path, "wb") as out:
        for idx, segment in enumerate(playlist.segments, 1):
            seg_url = segment.uri
            if not seg_url.startswith('http'):
                base = stream_url.rsplit('/', 1)[0]
                seg_url = f"{base}/{seg_url}"
            seg_data = httpx.get(seg_url).content
            if cipher:
                seg_data = cipher.decrypt(seg_data)
            out.write(seg_data)
            print(f"\rDownloading: {idx}/{total} segments", end="")
    print()  # newline

def main():
    if len(sys.argv) < 2:
        print("Usage: python hanime_downloader.py <URL>")
        sys.exit(1)

    url = sys.argv[1]
    match = re.match(r"https://hanime\.tv/videos/hentai/([A-Za-z0-9]+(?:-[A-Za-z0-9]+)+)", url, re.I)
    if not match:
        print("Invalid URL format")
        sys.exit(1)

    slug = match.group(1)
    print(f"Fetching info for {slug}...")
    data = get_video_info(slug)
    hentai = data['hentai_video']
    print(f"Title: {hentai['name']}")
    print(f"Censored: {hentai['is_censored']}")

    streams = data['videos_manifest']['servers'][0]['streams']
    stream = select_stream(streams)
    resolution = stream['height']
    print(f"Selected resolution: {resolution}p")

    # Create download directory
    os.makedirs("download", exist_ok=True)
    filename = f"{slug}-{resolution}p.mp4"
    output_path = os.path.join("download", filename)

    print(f"Downloading to {output_path} ...")
    download_video(stream['url'], output_path)
    print("Done!")

if __name__ == "__main__":
    main()
