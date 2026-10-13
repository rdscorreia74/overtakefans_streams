import os
import re
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

    # Find all text blocks or containers that match the pattern in the HTML structure
    # Overtakefans typically wraps these in headings or text elements preceding the input/hash boxes
    text_content = soup.get_text(separator="\n")
    
    # Alternatively, parse elements directly by looking for 'Server' headings
    # Let's search the HTML elements for the specific headers and their nearby 40-char hashes
    for element in soup.find_all(string=re.compile(r'Server\s+\d+:', re.IGNORECASE)):
        title = element.strip()
        
        # Look around this element's parent container to find the 40-character hex hash
        parent = element.parent
        found_hash = None
        
        # Check parents/siblings for a hash
        for _ in range(3): # Go up a few levels to find the container box
            if parent:
                match = re.search(r'([a-fA-F0-9]{40})', parent.get_text())
                if match:
                    found_hash = match.group(1)
                    break
                parent = parent.parent
        
        if found_hash and (title, found_hash) not in streams:
            streams.append((title, found_hash))

    # Fallback method if structural parsing misses any: scan line by line
    if not streams:
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
    
    print(f"Successfully generated playlist.m3u with {len(streams)} streams with custom titles.")

if __name__ == "__main__":
    streams = get_streams()
    generate_m3u(streams)
