# SDown Loader

[![GitHub Repo](https://img.shields.io/badge/GitHub-sdown--loader-blue)](https://github.com/zougar99/sdown-loader)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-blue)
![Python](https://img.shields.io/badge/Python-3.7%2B-green)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Version](https://img.shields.io/badge/Version-2.0.0-blue)

A powerful Spotify downloader for Windows, macOS, and Linux. Download playlists, albums, and single tracks with ease.

## Features

- 📋 Download complete playlists
- 🎵 Download single tracks
- 💿 Download full albums
- 🔍 Search and download
- 📚 Batch download multiple links
- 📂 Manage downloaded files
- 📜 Download history
- 📦 Multiple format support (MP3, FLAC, M4A, WAV, OGG)
- ⚙️ Advanced settings
- 📋 Clipboard support (paste link automatically)
- 🎨 GUI Version available

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/werlist99/SDown_Loader.git
cd SDown_Loader

# Install dependencies
pip install -r requirements.txt
```

### Usage - Command Line

```bash
# Run the app
python SDown_Loader.py
```

### Usage - GUI Version

```bash
# Run with graphical interface
python SDown_GUI.py
```

## Requirements

### Python
- Python 3.7 or higher

### Dependencies
```
spotdl>=4.0.0
pyperclip>=1.8.0
```

### FFmpeg (Required)
- **Windows**: Download from [ffmpeg.org](https://www.gyan.dev/ffmpeg/builds/) or use `winget install ffmpeg`
- **macOS**: `brew install ffmpeg`
- **Linux**: `sudo apt install ffmpeg` (Debian/Ubuntu) or `sudo pacman -S ffmpeg` (Arch)

## Menu Options

1. 📋 Download Playlist
2. 🎵 Download Single Track
3. 💿 Download Album
4. 🔍 Search and Download
5. 📚 Batch Download
6. 📂 Manage Downloads
7. 📜 Download History
8. ⚙️ Settings
0. 🚪 Exit

## Format Options

- MP3 (default)
- FLAC (high quality)
- M4A
- WAV
- OGG

## Files Structure

```
SDown_Loader/
├── SDown_Loader.py     # Main application (CLI)
├── SDown_GUI.py        # GUI version
├── SDown_Simple.py     # Simple version
├── requirements.txt    # Dependencies
└── README.md           # This file
```

## Troubleshooting

### FFmpeg Issues
- Make sure FFmpeg is added to PATH
- On Windows: Add ffmpeg/bin to environment variables

### Rate Limit Issues
- Wait 24 hours or use Spotify Authentication
- Visit: https://developer.spotify.com/dashboard

### Installation Issues
```bash
pip install --upgrade spotdl
```

## GitHub

🔗 **Repository**: https://github.com/zougar99/sdown-loader

## Contact

📞 **Telegram**: @werlist99

For support and inquiries, contact us on Telegram.

## Version

Current Version: 2.0.0

## Developer

👤 **zougar99** - GitHub: @zougar99 | Telegram: @werlist99

## License

MIT License

## Warning

This application is for personal use only. Please respect copyright laws.