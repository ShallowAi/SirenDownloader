import requests
import json
from tqdm import tqdm
import os
import re

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36'
}


def sanitize_filename(filename):
    # Remove invalid characters for Windows
    return re.sub(r'[<>:"/\\|?*]', '_', filename)

# Fetch JSON data
url = "https://monster-siren.hypergryph.com/api/songs"
response = requests.get(url, headers=headers)
data = response.json()

# Extract and print all 'cid' values
cids = [song['cid'] for song in data['data']['list']]

for cid in cids:
    # Fetch song data using cid
    song_url = f"https://monster-siren.hypergryph.com/api/song/{cid}"
    response = requests.get(song_url)
    song_data = response.json()

    # Extract sourceUrl
    source_url = song_data['data'].get('sourceUrl')
    if source_url:
        file_name = f"{song_data['data']['name']}.wav"
        
        file_name = sanitize_filename(file_name)
        
        # Skip if file already exists
        if os.path.exists(file_name):
            print(f"File {file_name} already exists, skipping download.")
            continue
        
        # Download the song file
        with requests.get(source_url, stream=True) as audio_response:
            total_size = int(audio_response.headers.get('content-length', 0))
            block_size = 1024  # 1 Kilobyte

            # Show download progress
            with open(file_name, 'wb') as audio_file, tqdm(
                desc=file_name,
                total=total_size,
                unit='iB',
                unit_scale=True,
                unit_divisor=1024,
            ) as bar:
                for data in audio_response.iter_content(block_size):
                    audio_file.write(data)
                    bar.update(len(data))

            print(f"Downloaded: {file_name}")
    else:
        print(f"No source URL found for CID {cid}")