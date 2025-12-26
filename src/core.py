import asyncio
import os
import subprocess
from typing import List, Dict, Optional, Callable

# Try importing yt_dlp, handle if not installed (though it should be)
try:
    import yt_dlp
except ImportError:
    yt_dlp = None

# We will use subprocess for spotdl to avoid complex async/loop issues 
# and credential management within the python process for now, 
# or we can try to use it as a lib if feasible. 
# For stability in this initial pass, let's use subprocess for spotdl commands 
# if the library API is too heavy. 
# However, let's try to see if we can use basic spotdl detection.

class TrackInfo:
    def __init__(self, title: str, artist: str, duration: int, url: str, index: int):
        self.title = title
        self.artist = artist
        self.duration = duration # in seconds
        self.url = url
        self.index = index

    def __repr__(self):
        return f"{self.index}. {self.artist} - {self.title} ({self.duration}s)"

class Downloader:
    def __init__(self):
        self.ffmpeg_path = self._check_ffmpeg()
        self.is_cancelled = False
        self.current_process = None # For spotdl subprocess

    def _check_ffmpeg(self):
        # ... (unchanged)
        # Check current dir first (for portable Windows usage)
        cwd_ffmpeg = os.path.join(os.getcwd(), "ffmpeg.exe")
        if os.path.exists(cwd_ffmpeg):
            return cwd_ffmpeg
        
        # Check .spotdl (common download location)
        spotdl_ffmpeg = os.path.join(os.path.expanduser("~"), ".spotdl", "ffmpeg.exe")
        if os.path.exists(spotdl_ffmpeg):
            return spotdl_ffmpeg

        # Check PATH
        import shutil
        if shutil.which("ffmpeg"):
            return "ffmpeg"
            
        print("[WARNING] FFmpeg not found! Conversions may fail.")
        return "ffmpeg" # Default and hope for the best

    def cancel(self):
        self.is_cancelled = True
        if self.current_process:
            try:
                self.current_process.terminate()
            except:
                pass

    def _get_yt_metadata(self, url: str) -> List[TrackInfo]:
        """
        Fetch metadata using yt-dlp for YouTube/SoundCloud/etc.
        """
        ydl_opts = {
            'extract_flat': 'in_playlist', # Don't download, just list
            'dump_single_json': True,
            'quiet': True,
            'ignoreerrors': True,
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        }
        
        tracks = []
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(url, download=False)
            except Exception as e:
                print(f"Error extracting info: {e}")
                info = None
            
            if not info:
                # Could not fetch metadata
                return []

            if 'entries' in info:
                # It's a playlist
                for idx, entry in enumerate(info['entries']):
                    if entry:
                        title = entry.get('title', 'Unknown')
                        artist = entry.get('uploader', 'Unknown')
                        duration = entry.get('duration', 0)
                        entry_url = entry.get('url', url)
                        # playlist indices are 1-based usually
                        tracks.append(TrackInfo(title, artist, duration, entry_url, idx + 1))
            else:
                # It's a single video
                title = info.get('title', 'Unknown')
                artist = info.get('uploader', 'Unknown')
                duration = info.get('duration', 0)
                tracks.append(TrackInfo(title, artist, duration, url, 1))
                
        return tracks

    def _get_spotify_metadata(self, url: str) -> List[TrackInfo]:
        """
        Fetch metadata using spotdl.
        Since spotdl library is heavy, we'll shell out to `spotdl --print-errors save ...` 
        or just assume we download everything if precise metadata is hard.
        Actually, let's try to use `spotdl` to fetch songs if possible.
        
        For now, implementing a simplified version that might just return a generic 
        "Playlist detected" if we can't easily parse without downloading.
        
        However, `spotdl` save file format is distinct. 
        Let's try to just run a quick check or return a placeholder for Spotify 
        implementation until we verify spotdl library usage.
        """
        # Placeholder for now, handling spotify metadata is complex without credentials 
        # or properly initialized Spotdl client.
        # We will implement the actual download logic which handles it automatically.
        # For the UI list, we might just say "Spotify Playlist (Metadata fetch deferred)"
        return [TrackInfo("Spotify URL (Metadata pending)", "Spotify", 0, url, 1)]

    async def get_metadata(self, url: str) -> List[TrackInfo]:
        """
        Detects source and fetches metadata.
        """
        if "spotify.com" in url:
            # Run in executor to avoid blocking
            return await asyncio.to_thread(self._get_spotify_metadata, url)
        else:
            return await asyncio.to_thread(self._get_yt_metadata, url)

    async def download(self, 
                       url: str, 
                       output_dir: str, 
                       format: str = 'wav', 
                       track_indices: Optional[List[int]] = None,
                       progress_callback: Optional[Callable[[str], None]] = None):
        """
        Download logic.
        """
        self.is_cancelled = False
        
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        if "spotify.com" in url:
            await self._download_spotify(url, output_dir, format, track_indices, progress_callback)
        else:
            await self._download_yt(url, output_dir, format, track_indices, progress_callback)

    async def _download_yt(self, url, output_dir, format, track_indices, progress_callback):
        # Build yt-dlp command
        # We use subprocess to allow immediate killing
        import sys
        
        # Base command: python -m yt_dlp [url] ...
        cmd = [sys.executable, "-m", "yt_dlp", url]
        
        # Output template
        cmd.extend(["-o", os.path.join(output_dir, '%(title)s.%(ext)s')])
        
        # Audio extraction options
        cmd.extend([
            "-x", # Extract audio
            "--audio-format", format,
            "--audio-quality", "192K",
            "--ffmpeg-location", self.ffmpeg_path,
        ])
        
        # Playlist items
        if track_indices:
            items_str = ",".join(map(str, track_indices))
            cmd.extend(["--playlist-items", items_str])
        
        # Other opts
        cmd.extend([
            "--newline", # Important for regex parsing
            "--no-colors",
            "--user-agent", 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        ])
        
        if progress_callback:
            progress_callback(f"Starting download process...")

        self.current_process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        # Monitor output
        import re
        # Regex to capture progress: [download]  45.0% of 10.00MiB at 2.00MiB/s
        progress_re = re.compile(r'\[download\]\s+(\d+\.\d+)%')
        
        while True:
            if self.is_cancelled:
                self.current_process.kill() # Hard kill for immediate stop
                raise Exception("Download Cancelled by User")
                
            try:
                line = await asyncio.wait_for(self.current_process.stdout.readline(), timeout=0.1)
            except asyncio.TimeoutError:
                 if self.current_process.returncode is not None:
                     break
                 continue

            if not line:
                break
                
            line_str = line.decode('utf-8', errors='replace').strip()
            
            # Parse progress
            if line_str:
                match = progress_re.search(line_str)
                if match and progress_callback:
                    p = match.group(1)
                    progress_callback(f"Downloading: {p}%")
                elif "[ExtractAudio]" in line_str and progress_callback:
                    progress_callback("Converting audio...")
                elif progress_callback:
                    # Optional: verbose logging? 
                    # progress_callback(f"yt-dlp: {line_str}")
                    pass

        await self.current_process.wait()
        self.current_process = None
        
        if self.is_cancelled:
            raise Exception("Download Cancelled by User")
            
        if self.current_process and self.current_process.returncode != 0:
            # Check stderr?
            # stderr = await self.current_process.stderr.read()
            # print(stderr.decode())
            pass

        if progress_callback:
            progress_callback("All done!")

    # Removed _run_yt_dlp as it is no longer used

    async def _download_spotify(self, url, output_dir, format, track_indices, progress_callback):
        if progress_callback:
            progress_callback("Starting Spotify download (this may take a while)...")
            
        # Use python -m spotdl to ensure we use the venv version
        import sys
        cmd = [sys.executable, "-m", "spotdl", url, "--output", output_dir, "--format", format]
        
        self.current_process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        # Monitor output for progress
        while True:
            if self.is_cancelled:
                self.current_process.terminate()
                raise Exception("Download Cancelled by User")
                
            try:
                line = await asyncio.wait_for(self.current_process.stdout.readline(), timeout=0.5)
            except asyncio.TimeoutError:
                if self.current_process.returncode is not None:
                    break
                continue
                
            if not line:
                break
            line_str = line.decode().strip()
            if line_str and progress_callback:
                progress_callback(f"SpotDL: {line_str}")
                
        await self.current_process.wait()
        self.current_process = None
        
        if self.is_cancelled:
             raise Exception("Download Cancelled by User")
             
        if progress_callback:
            progress_callback("Spotify download finished.")
