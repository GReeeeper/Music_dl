import asyncio
import click
import os
import sys
# Ensure src is in path if run directly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core import Downloader

def parse_items(items_str: str) -> list[int]:
    """Parse string like '1,2,5-10' into [1, 2, 5, 6, 7, 8, 9, 10]"""
    if not items_str:
        return None
    
    indices = set()
    parts = items_str.split(',')
    for part in parts:
        part = part.strip()
        if '-' in part:
            try:
                start, end = map(int, part.split('-'))
                indices.update(range(start, end + 1))
            except ValueError:
                click.echo(f"Warning: Invalid range format '{part}'")
        else:
            try:
                indices.add(int(part))
            except ValueError:
                click.echo(f"Warning: Invalid number '{part}'")
    return sorted(list(indices))

@click.command()
@click.option('--url', required=True, help='URL of the song or playlist (YouTube/Spotify/SoundCloud)')
@click.option('--format', default='wav', type=click.Choice(['mp3', 'wav', 'flac', 'm4a']), help='Output format (default: wav)')
@click.option('--output', '-o', default='downloads', help='Output directory (default: ./downloads)')
@click.option('--items', help='Specific playlist items to download (e.g. "1,3,5-10"). 1-based indices.')
def main(url, format, output, items):
    """
    Music Downloader CLI
    """
    click.echo(f"Processing URL: {url}")
    click.echo(f"Format: {format}")
    click.echo(f"Output: {output}")
    
    track_indices = parse_items(items)
    if track_indices:
        click.echo(f"Selecting tracks: {track_indices}")

    downloader = Downloader()

    async def run_download():
        await downloader.download(
            url=url, 
            output_dir=output, 
            format=format, 
            track_indices=track_indices,
            progress_callback=lambda msg: click.echo(f"[INFO] {msg}")
        )

    try:
        asyncio.run(run_download())
    except KeyboardInterrupt:
        click.echo("\nDownload cancelled by user.")
    except Exception as e:
        click.echo(f"\nError: {e}")

if __name__ == '__main__':
    main()
