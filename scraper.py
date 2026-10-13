import os
import re
import cloudscraper
from bs4 import BeautifulSoup

TARGET_URL = "https://overtakefans.com/f1-live-stream/sky-sport-f1-live-stream-via-ace-player/"

def get_streams():
    # Initialize cloudscraper to bypass Cloudflare protection
    scraper = cloudscraper.create_scraper()
    
    try:
        response = scraper.get(TARGET_URL, timeout=15)
        response.raise_for_status()
    except Exception as e:
        print(f"Error fetching the website: {e}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    streams = []

    # Find 40-character hexadecimal Acestream hashes in the page content
    hashes = re.findall(r'([a-fA-F0-9]{40})', response.text)
    unique_hashes = list(dict.fromkeys(hashes))
    
    for i, h in enumerate(unique_hashes):
        streams.append((f"F1 Stream Server {i+1}", h))

    return streams

def generate_m3u(streams):
    m3u_content = "#EXTM3U\n"
    
    for title, stream_id in streams:
        stream_url = f"http://127.0.0.1:6878/ace/getstream?id={stream_id}"
        m3u_content += f'#EXTINF:-1 tvg-id="" tvg-name="{title}",{title}\n'
        m3u_content += f"{stream_url}\n"

    with open("playlist.m3u", "w", encoding="utf-8") as f:
        f.write(m3u_content)
    
    print(f"Successfully generated playlist.m3u with {len(streams)} streams.")

if __name__ == "__main__":
    streams = get_streams()
    generate_m3u(streams)
