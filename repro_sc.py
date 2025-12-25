import asyncio
import sys
import os

# Ensure src is in path
sys.path.append(os.path.abspath(os.getcwd()))

from src.core import Downloader

async def main():
    dl = Downloader()
    # A public SoundCloud playlist (set)
    url = "https://soundcloud.com/soundcloud-scenes/sets/lo-fi-hip-hop"
    print(f"Fetching metadata for: {url}")
    
    try:
        tracks = await dl.get_metadata(url)
        print(f"Found {len(tracks)} tracks.")
        for i, t in enumerate(tracks[:5]):
            print(f"{i+1}. {t.title} - {t.artist} ({t.url})")
            
        if len(tracks) == 0:
            print("ERROR: No tracks found in playlist.")
            
    except Exception as e:
        print(f"EXCEPTION: {e}")

if __name__ == "__main__":
    asyncio.run(main())
