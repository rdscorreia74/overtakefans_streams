import os
import re
import requests
from bs4 import BeautifulSoup

# Updated to the specific live stream page URL
TARGET_URL = "https://overtakefans.com/f1-live-stream/sky-sport-f1-live-stream-via-ace-player/"

def get_streams():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://overtakefans.com/"
    }
    
    try:
        response = requests.get(TARGET_URL, headers=headers, timeout=15)
        response.raise_for_status()
    except Exception as e:
        print(f"Error fetching the website: {e}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    streams = []

    # Parse boxes/servers containing the Acestream IDs shown on the page
    # Overtakefans stores hashes in input fields, text elements, or data attributes
    for code_block in soup.find_all(['div', 'span', 'p', 'code'], string=re.compile(r'([a-fA-F0-9]{40})')):
        match = re.search(r'([a-fA-F0-9]{40})', code_block.get_text())
        if match:
            stream_id = match.group(1)
            streams.append(("F1 Stream", stream_id))

    # Fallback: scan full page text for any 40-character hex hashes if specific elements weren't caught
    if not streams:
        hashes = re.findall(r'([a-fA-F0-9]{40})', response.text)
        unique_hashes = list(dict.fromkeys(hashes))
        for i, h in enumerate(unique_hashes):
            streams.append((f"F1 Stream {i+1}", h))

    # Deduplicate streams by ID
    seen = set()
    unique_streams = []
    for title, sid in streams:
        if sid not in seen:
            seen.add(sid)
            unique_streams.append((title, sid))

    return unique_streams

def generate_m3u(streams):
    m3u_content = "#EXTM3U\n"
    
    for i, (title, stream_id) in enumerate(streams):
        display_title = f"F1 Stream Server {i+1}"
        stream_url = f"http://127.0.0.1:6878/ace/getstream?id={stream_id}"
        
        m3u_content += f'#EXTINF:-1 tvg-id="" tvg-name="{display_title}",{display_title}\n'
        m3u_content += f"{stream_url}\n"

    with open("playlist.m3u", "w", encoding="utf-8") as f:
        f.write(m3u_content)
    
    print(f"Successfully generated playlist.m3u with {len(streams)} streams.")

if __name__ == "__main__":
    streams = get_streams()
    generate_m3u(streams)
