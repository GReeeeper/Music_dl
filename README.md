# 🎵 Future Music Downloader

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge&logo=python&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux-green?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-purple?style=for-the-badge)

A cutting-edge, cross-platform music downloader featuring a **futuristic "Cyberpunk" GUI**. Built with **Flet** and powered by **yt-dlp** and **SpotDL**, it lets you download high-quality audio from Spotify, YouTube, and SoundCloud seamlessly.

---

## ✨ Features

- **🎧 Multi-Platform Support**: Download tracks/playlists from **Spotify**, **YouTube**, and **SoundCloud**.
- **⏯️ Smart Controls**: 
  - **Pause/Resume**: Seamlessly pause downloads and resume later.
  - **Instant Stop**: Immediately kill the download process.
- **🎨 Futuristic UI**: Deep dark theme, glass-morphism effects, and neon accents.
- **📂 File Management**: 
  - Auto-convert to **WAV, MP3, FLAC, M4A**.
  - Built-in **"Empty Folder"** utility to clean up your workspace.
- **🚀 Portable & Fast**: No complex installation required.

---

## 📸 Screenshots
main app
<img width="1267" height="756" alt="image" src="https://github.com/user-attachments/assets/a5e62385-8b9b-413d-9834-5426afd7b961" />
all formats
<img width="1267" height="756" alt="image" src="https://github.com/user-attachments/assets/c3f355e6-e27e-4a52-a25f-4e48b3593cd9" />
the downloads folder
<img width="1268" height="590" alt="image" src="https://github.com/user-attachments/assets/c3ccb7a4-c5a6-4a50-aa9a-397c6d938499" />


---

## 🚀 Quick Start

### 🪟 Windows Users

**Option 1: One-Click Run (Recommended)**
1. Double-click `run_windows.bat`.
2. The app will self-install dependencies and launch!

**Option 2: Build Executable**
1. Double-click `build_windows.bat`.
2. Find your standalone `MusicDL.exe` in the `dist` folder.

### 🐧 Linux Users

1. **Setup**:
   ```bash
   python3 setup_env.py
   ```
2. **Run**:
   ```bash
   ./venv/bin/python src/main.py
   ```

---

## 🛠️ Tech Stack

- **GUI**: [Flet](https://flet.dev) (Flutter for Python)
- **Core**: [yt-dlp](https://github.com/yt-dlp/yt-dlp) & [spotDL](https://github.com/spotDL/spotify-downloader)
- **Audio Processing**: FFmpeg

## ⚠️ Disclaimer
This tool is intended for educational purposes and personal use only. Please check the Terms of Service of the source platforms and respect copyright laws.
