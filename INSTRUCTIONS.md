# Music Downloader - Setup & Run Instructions

## Prerequisites
1. **FFmpeg**: Required for audio conversion.
   - **Windows**: Download `ffmpeg.exe` and place it in this project folder, OR install it system-wide and add to PATH.
   - **Linux**: Install via package manager (e.g., `sudo pacman -S ffmpeg` or `sudo apt install ffmpeg`).
2. **Python 3.8+**: Ensure Python is installed.

## Windows Users

### Option 1: One-Click Run (Recommended)
1. Double-click **`run_windows.bat`**.
2. This script will automatically:
   - Check/Install Python dependencies.
   - Setup the virtual environment.
   - Launch the application.

### Option 2: Build Executable (.exe)
1. Double-click **`build_windows.bat`**.
2. Wait for the process to complete.
3. Your standalone app will be in the `dist` folder as `MusicDL.exe`.
4. **Important**: If you haven't installed FFmpeg system-wide, copy `ffmpeg.exe` into the `dist` folder next to `MusicDL.exe`.

## Linux Users

1. **Setup Environment**:
   Open a terminal in the project folder and run:
   ```bash
   python3 setup_env.py
   ```

2. **Run Application**:
   ```bash
   ./venv/bin/python src/main.py
   ```

## Troubleshooting
- **Crash on start?** Make sure `libmpv` is installed (Linux) or that you have a working audio device.
- **Download fails immediately?** Check your internet connection and ensure `ffmpeg` is accessible.
