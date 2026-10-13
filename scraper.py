import os
import re
import requests
from bs4 import BeautifulSoup

# URL of the overtakefans page containing the streams
TARGET_URL = "https://overtakefans.com/"

def get_streams():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(TARGET_URL, headers=headers, timeout=15)
        response.raise_for_status()
    except Exception as e:
        print(f"Error fetching the website: {e}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    streams = []

    # Method 1: Search for <a> tags containing 'acestream://'
    for a in soup.find_all('a', href=True):
        href = a['href']
        if 'acestream://' in href:
            stream_id = href.split('acestream://')[-1]
            title = a.get_text(strip=True) or "F1 Stream"
            streams.append((title, stream_id))

    # Method 2: Fallback regex search for 40-character hexadecimal hashes
    if not streams:
        content = response.text
        hashes = re.findall(r'([a-fA-F0-9]{40})', content)
        unique_hashes = list(dict.fromkeys(hashes))
        for i, h in enumerate(unique_hashes):
            streams.append((f"F1 Stream {i+1}", h))

    return streams

def generate_m3u(streams):
    # Standard M3U header for IPTV / Kodi
    m3u_content = "#EXTM3U\n"
    
    for title, stream_id in streams:
        # Format for local Ace Stream engine proxy URL
        stream_url = f"http://127.0.0.1:6878/ace/getstream?id={stream_id}"
        
        m3u_content += f'#EXTINF:-1 tvg-id="" tvg-name="{title}",{title}\n'
        m3u_content += f"{stream_url}\n"

    with open("playlist.m3u", "w", encoding="utf-8") as f:
        f.write(m3u_content)
    
    print(f"Successfully generated playlist.m3u with {len(streams)} streams.")

if __name__ == "__main__":
    streams = get_streams()
    generate_m3u(streams)
