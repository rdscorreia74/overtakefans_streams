import os
import re
import json
import cloudscraper
from bs4 import BeautifulSoup

TARGET_URL = "https://overtakefans.com/f1-live-stream/sky-sport-f1-live-stream-via-ace-player/"

def get_streams():
    scraper = cloudscraper.create_scraper()
    
    try:
        response = scraper.get(TARGET_URL, timeout=15)
        response.raise_for_status()
    except Exception as e:
        print(f"Error fetching the website: {e}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    streams = []

    for element in soup.find_all(string=re.compile(r'Server\s+\d+:', re.IGNORECASE)):
        title = element.strip()
        parent = element.parent
        found_hash = None
        
        for _ in range(3):
            if parent:
                match = re.search(r'([a-fA-F0-9]{40})', parent.get_text())
                if match:
                    found_hash = match.group(1)
                    break
                parent = parent.parent
        
        if found_hash and (title, found_hash) not in streams:
            streams.append((title, found_hash))

    if not streams:
        text_content = soup.get_text(separator="\n")
        lines = text_content.splitlines()
        current_title = "F1 Stream"
        for line in lines:
            line = line.strip()
            if line.startswith("Server "):
                current_title = line
            else:
                match = re.search(r'^([a-fA-F0-9]{40})$', line)
                if match:
                    streams.append((current_title, match.group(1)))

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

def generate_json(streams):
    channels = []
    for title, stream_id in streams:
        channels.append({
            "title": title,
            "name": title,
            "id": stream_id,
            "url": f"acestream://{stream_id}",
            "proxy_url": f"http://127.0.0.1:6878/ace/getstream?id={stream_id}"
        })
    
    data = {
        "channels": channels
    }

    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    
    print(f"Successfully generated data.json with {len(streams)} streams.")

if __name__ == "__main__":
    streams = get_streams()
    generate_m3u(streams)
    generate_json(streams)
