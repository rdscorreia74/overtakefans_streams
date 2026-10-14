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

    # Find all elements that match 'Server X:'
    server_elements = soup.find_all(string=re.compile(r'Server\s+\d+:', re.IGNORECASE))

    for element in server_elements:
        title = element.strip()
        found_hash = None
        
        # Traverse parent container and local subtree to extract the precise hash for THIS server block
        curr = element.parent
        for _ in range(4):
            if curr:
                local_hashes = re.findall(r'([a-fA-F0-9]{40})', curr.get_text())
                if local_hashes:
                    found_hash = local_hashes[0]
                    break
                curr = curr.next_sibling or curr.parent
        
        if found_hash and (title, found_hash) not in streams:
            streams.append((title, found_hash))

    # Fallback line-by-line parsing if structural DOM search misses any elements
    if not streams:
        text_content = soup.get_text(separator="\n")
        lines = [line.strip() for line in text_content.splitlines() if line.strip()]
        
        for i, line in enumerate(lines):
            if re.match(r'^Server\s+\d+:', line, re.IGNORECASE):
                title = line
                for j in range(1, 6):
                    if i + j < len(lines):
                        match = re.search(r'([a-fA-F0-9]{40})', lines[i + j])
                        if match:
                            streams.append((title, match.group(1)))
                            break

    return streams

def generate_m3u(streams):
    m3u_content = "#EXTM3U\n"
    for title, stream_id in streams:
        stream_url = f"http://127.0.0.1:6878/ace/getstream?id={stream_id}"
        m3u_content += f'#EXTINF:-1 tvg-id="" tvg-name="{title}",{title}\n'
        m3u_content += f"{stream_url}\n"

    with open("playlist.m3u", "w", encoding="utf-8") as f:
        f.write(m3u_content)

def generate_json(streams):
    channels = []
    for title, stream_id in streams:
        channels.append({
            "name": title,
            "id": stream_id,
            "url": f"acestream://{stream_id}"
        })

    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(channels, f, indent=4, ensure_ascii=False)

def generate_txt(streams):
    txt_content = ""
    for title, stream_id in streams:
        # Include 'acestream://' prefix so Horus "Find links" regex parses all streams properly
        txt_content += f"{title}\nacestream://{stream_id}\n\n"

    with open("links.txt", "w", encoding="utf-8") as f:
        f.write(txt_content)
    
    print(f"Successfully generated files with {len(streams)} unique streams.")

if __name__ == "__main__":
    streams = get_streams()
    generate_m3u(streams)
    generate_json(streams)
    generate_txt(streams)
