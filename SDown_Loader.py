#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SDown Loader - Spotify Downloader
A complete application for downloading songs from Spotify
"""

import os
import sys
import subprocess
import re
import json
from pathlib import Path

try:
    import pyperclip
    HAS_CLIPBOARD = True
except ImportError:
    HAS_CLIPBOARD = False

if sys.version_info < (3, 7):
    print("Error: Python 3.7 or higher required")
    sys.exit(1)

def check_dependencies():
    try:
        import spotdl
        return True
    except ImportError:
        return False

def check_ffmpeg():
    import shutil
    ffmpeg_cmd = shutil.which("ffmpeg")
    if ffmpeg_cmd:
        try:
            result = subprocess.run([ffmpeg_cmd, '-version'], 
                                  capture_output=True, 
                                  text=True,
                                  timeout=5)
            return result.returncode == 0
        except:
            return False
    return False

def get_ffmpeg_install_instructions():
    system = sys.platform
    if system == 'win32':
        return """
To install FFmpeg on Windows:
  1. Download from: https://www.gyan.dev/ffmpeg/builds/
  2. Extract and add the bin folder to PATH
  3. Or use: winget install ffmpeg
"""
    elif system == 'darwin':
        return """
To install FFmpeg on macOS:
  brew install ffmpeg
"""
    else:
        return """
To install FFmpeg on Linux:
  Ubuntu/Debian: sudo apt install ffmpeg
  Arch: sudo pacman -S ffmpeg
  Fedora: sudo dnf install ffmpeg
"""

def sanitize_filename(name):
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        name = name.replace(char, '_')
    name = name.strip('. ')
    if len(name) > 100:
        name = name[:100]
    return name

HISTORY_FILE = Path("download_history.json")
CONFIG_FILE = Path("config.json")

def load_config():
    default_config = {
        "download_dir": "downloads",
        "format": "mp3",
        "quality": "normal",
        "use_auth": False,
        "skip_existing": False,
        "generate_json": False,
        "embed_lyrics": True,
        "output_template": "{artist} - {title}",
        "max_retries": 3,
        "show_progress": True
    }
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return {**default_config, **config}
        except:
            return default_config
    return default_config

def save_config(config):
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
    except:
        pass

def load_history():
    if HISTORY_FILE.exists():
        try:
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []

def save_history(entry):
    history = load_history()
    history.insert(0, entry)
    if len(history) > 50:
        history = history[:50]
    try:
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    except:
        pass

def get_download_stats():
    downloads_dir = Path(load_config().get("download_dir", "downloads"))
    if not downloads_dir.exists():
        return {"total_files": 0, "total_size": 0}
    
    files = list_downloaded_files(downloads_dir)
    total_size = sum(f.stat().st_size for f in files)
    return {"total_files": len(files), "total_size": total_size}

def list_downloaded_files(downloads_dir):
    if not downloads_dir.exists():
        return []
    files = []
    for item in downloads_dir.rglob("*"):
        if item.is_file() and item.suffix.lower() in ['.mp3', '.flac', '.m4a', '.wav', '.ogg']:
            files.append(item)
    return sorted(files, key=lambda x: x.stat().st_mtime, reverse=True)

def format_size(size_bytes):
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"

def get_python_cmd():
    if sys.platform == 'win32':
        return [sys.executable, "-m"]
    else:
        return [sys.executable, "-m"]

def download_single_track(url, output_dir, output_format="mp3"):
    url = url.split('?')[0].split('#')[0].strip()
    
    print(f"\n{'='*60}")
    print(f"Downloading single track...")
    print(f"URL: {url}")
    print(f"Folder: {output_dir}")
    print(f"Format: {output_format}")
    print(f"{'='*60}")
    
    cmd = get_python_cmd() + [
        "spotdl",
        url,
        "--output", str(output_dir),
        "--output-format", output_format,
        "--lyrics"
    ]
    
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
    
    for line in process.stdout:
        print(line, end='', flush=True)
    
    process.wait()
    success = process.returncode == 0
    if success:
        save_history({"type": "track", "url": url, "format": output_format})
    return success

def download_album(url, output_dir, output_format="mp3"):
    url = url.split('?')[0].split('#')[0].strip()
    
    if not re.match(r'https://(open\.)?spotify\.com/album/[a-zA-Z0-9]+', url):
        print("Invalid album URL")
        return False
    
    album_id = re.search(r'album/([a-zA-Z0-9]+)', url)
    album_name = f"Album_{album_id.group(1)}" if album_id else "Album"
    
    output_dir = output_dir / sanitize_filename(album_name)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\n{'='*60}")
    print(f"Downloading album: {album_name}")
    print(f"URL: {url}")
    print(f"Folder: {output_dir}")
    print(f"Format: {output_format}")
    print(f"{'='*60}")
    
    cmd = get_python_cmd() + [
        "spotdl",
        url,
        "--output", str(output_dir),
        "--output-format", output_format
    ]
    
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
    
    for line in process.stdout:
        print(line, end='', flush=True)
    
    process.wait()
    success = process.returncode == 0
    if success:
        save_history({"type": "album", "name": album_name, "url": url, "format": output_format})
    return success

def download_playlist(url, output_dir, use_auth=False, output_format="mp3"):
    url = url.split('?')[0].split('#')[0].strip()
    
    if not re.match(r'https://(open\.)?spotify\.com/playlist/[a-zA-Z0-9]+', url):
        print("Invalid playlist URL")
        return False
    
    playlist_id = re.search(r'playlist/([a-zA-Z0-9]+)', url)
    playlist_name = f"Playlist_{playlist_id.group(1)}" if playlist_id else "Playlist"
    
    output_dir = output_dir / sanitize_filename(playlist_name)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\n{'='*60}")
    print(f"Downloading Playlist...")
    print(f"URL: {url}")
    print(f"Folder: {output_dir}")
    print(f"Format: {output_format}")
    print(f"{'='*60}")
    
    cmd = get_python_cmd() + [
        "spotdl",
        url,
        "--output", str(output_dir),
        "--output-format", output_format
    ]
    
    if use_auth:
        cmd.append("--user-auth")
    
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
    
    for line in process.stdout:
        print(line, end='', flush=True)
    
    process.wait()
    
    if process.returncode == 0:
        print(f"\nPlaylist downloaded successfully!")
        print(f"Files saved to: {os.path.abspath(output_dir)}")
        save_history({"type": "playlist", "name": playlist_name, "url": url, "format": output_format})
        return True
    return False

def batch_download(urls, output_dir, output_format="mp3"):
    print(f"\n{'='*60}")
    print(f"Downloading {len(urls)} items...")
    print(f"{'='*60}")
    
    success_count = 0
    for i, url in enumerate(urls, 1):
        print(f"\nDownloading {i}/{len(urls)}")
        try:
            if "playlist" in url:
                if download_playlist(url, output_dir, False, output_format):
                    success_count += 1
            elif "album" in url:
                if download_album(url, output_dir, output_format):
                    success_count += 1
            else:
                if download_single_track(url, output_dir / "Singles", output_format):
                    success_count += 1
        except Exception as e:
            print(f"Error with {url}: {e}")
    
    print(f"\n{'='*60}")
    print(f"Downloaded {success_count}/{len(urls)} successfully")
    print(f"{'='*60}")
    return success_count

def manage_downloaded_files(downloads_dir):
    files = list_downloaded_files(downloads_dir)
    
    if not files:
        print("\nNo downloaded files")
        return
    
    print(f"\n{'='*60}")
    print(f"Downloaded Files ({len(files)} files)")
    print(f"{'='*60}")
    
    total_size = 0
    for i, f in enumerate(files, 1):
        size = f.stat().st_size
        total_size += size
        size_str = format_size(size)
        print(f"{i:3}. {f.name[:50]:50} {size_str:>10}")
    
    print(f"\nTotal Size: {format_size(total_size)}")
    print(f"\nChoose:")
    print("  [D] Delete file")
    print("  [O] Open folder")
    print("  [C] Delete all")
    print("  [0] Back")
    
    choice = input("Enter choice: ").strip().lower()
    
    if choice == "d":
        try:
            num = int(input("Enter file number to delete: "))
            if 1 <= num <= len(files):
                files[num-1].unlink()
                print("Deleted")
        except:
            print("Error")
    elif choice == "c":
        confirm = input("Are you sure? (y/n): ").strip().lower()
        if confirm == 'y':
            for f in files:
                try:
                    f.unlink()
                except:
                    pass
            print("All deleted")
    elif choice == "o":
        if sys.platform == 'win32':
            os.startfile(downloads_dir)
        elif sys.platform == 'darwin':
            subprocess.run(['open', str(downloads_dir)])
        else:
            subprocess.run(['xdg-open', str(downloads_dir)])

def show_download_history():
    history = load_history()
    
    print(f"\n{'='*60}")
    print(f"Download History ({len(history)})")
    print(f"{'='*60}")
    
    if not history:
        print("No history")
        return
    
    for i, item in enumerate(history[:20], 1):
        item_type = item.get("type", "unknown")
        url = item.get("url", "")
        fmt = item.get("format", "mp3")
        name = item.get("name", "")
        
        type_icon = {"playlist": "PL", "album": "AL", "track": "TR"}.get(item_type, "??")
        print(f"{i:2}. {type_icon} | {fmt:5} | {name or url[:40]}")

def get_format_selection():
    print("\nSelect Format:")
    print("  [1] MP3 (default)")
    print("  [2] FLAC (high quality)")
    print("  [3] M4A")
    print("  [4] WAV")
    print("  [5] OGG")
    
    choice = input("Enter choice [1]: ").strip()
    formats = {"1": "mp3", "2": "flac", "3": "m4a", "4": "wav", "5": "ogg"}
    return formats.get(choice, "mp3")

def search_and_download(query, output_dir):
    print(f"\n{'='*60}")
    print(f"Searching for: {query}")
    print(f"{'='*60}")
    
    output_dir = output_dir / "Search"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    cmd = get_python_cmd() + [
        "spotdl",
        f"search:{query}",
        "--output", str(output_dir),
        "--output-format", "mp3"
    ]
    
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
    
    for line in process.stdout:
        print(line, end='', flush=True)
    
    process.wait()
    return process.returncode == 0

def show_menu():
    print("\n" + "="*60)
    print("SDown Loader - Main Menu".center(50))
    print("="*60)
    print("""
Select Download Type:
  [1] Download Playlist
  [2] Download Single Track
  [3] Download Album
  [4] Search and Download
  [5] Batch Download URLs
  [6] Manage Downloads
  [7] Download History
  [8] Settings
  [0] Exit
""")
    
    choice = input("Enter your choice: ").strip()
    return choice

def show_settings_menu():
    while True:
        print("\n" + "="*60)
        print("Settings".center(50))
        print("="*60)
        print("""
  [1] Setup Spotify Authentication
  [2] Change Download Directory
  [3] Update spotdl
  [4] System Status
  [5] Check for Updates
  [6] About
  [0] Back
""")
        choice = input("Enter your choice: ").strip()
        
        if choice == "1":
            print("\nTo setup Authentication:")
            print("   1. Go to: https://developer.spotify.com/dashboard")
            print("   2. Create a new application")
            print("   3. Get Client ID and Client Secret")
            print("   4. Run: py -3 -m spotdl --user-auth")
            print("   5. Browser will open for login")
            input("\nPress Enter to continue...")
        elif choice == "3":
            print("Updating spotdl...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "spotdl"])
                print("Update successful!")
            except:
                print("Update failed")
            input("\nPress Enter to continue...")
        elif choice == "4":
            print("\nSystem Status:")
            spotdl_ok = check_dependencies()
            ffmpeg_ok = check_ffmpeg()
            print(f"   {'Installed' if spotdl_ok else 'Not installed'} spotdl")
            print(f"   {'Installed' if ffmpeg_ok else 'Not installed'} FFmpeg")
            input("\nPress Enter to continue...")
        elif choice == "5":
            print("Checking for updates...")
            try:
                result = subprocess.run([sys.executable, "-m", "pip", "index", "versions", "spotdl"], 
                                      capture_output=True, text=True, timeout=10)
                print(result.stdout if result.stdout else "App is up to date")
            except:
                print("Unable to check")
            input("\nPress Enter to continue...")
        elif choice == "6":
            show_about()
        elif choice == "0":
            break

def show_about():
    print("\n" + "="*60)
    print("About".center(50))
    print("="*60)
    print("""
  SDown Loader - Enhanced Version

  Version: 2.0.0
  Last Update: 2026
  
  Developer: zougar99
  Contact: @werlist99 (Telegram)
  
  Compatible with:
     - Windows
     - macOS  
     - Linux
  
  GitHub: https://github.com/zougar99/sdown-loader
  
  For support: Telegram @werlist99
""")
    input("\nPress Enter to continue...")

def get_url_from_user(prompt_text):
    url = None
    
    if HAS_CLIPBOARD:
        try:
            clipboard_text = pyperclip.paste()
            if clipboard_text and "spotify.com" in clipboard_text.strip():
                print(f"Link found in clipboard:")
                print(f"   {clipboard_text.strip()}")
                use_clip = input(f"\n{prompt_text} (y/n, default: y): ").strip().lower()
                if use_clip != 'n':
                    url = clipboard_text.strip()
        except:
            pass
    
    if not url:
        print(prompt_text)
        print("Example: https://open.spotify.com/playlist/...")
        url = input("Enter URL: ").strip()
    
    return url

def main():
    global HAS_CLIPBOARD
    
    if sys.platform == 'win32':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    
    print("\n" + "="*60)
    print("SDown Loader - Enhanced Version".center(50))
    print("="*60)
    
    if not check_dependencies():
        print("\nspotdl is not installed")
        response = input("Install it now? (y/n): ").strip().lower()
        if response == 'y':
            print("Installing...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", "spotdl"])
                print("Installation successful!")
            except:
                print("Installation failed")
                return
        else:
            return
    
    if not HAS_CLIPBOARD:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyperclip"], 
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            import pyperclip
            HAS_CLIPBOARD = True
        except:
            pass
    
    if not check_ffmpeg():
        print("\nFFmpeg is not installed")
        print(get_ffmpeg_install_instructions())
        return
    
    downloads_dir = Path("downloads")
    downloads_dir.mkdir(exist_ok=True)
    
    while True:
        choice = show_menu()
        
        if choice == "1":
            url = get_url_from_user("Enter Playlist URL:")
            if url:
                use_auth = input("Use Authentication? (y/n): ").strip().lower() == 'y'
                download_playlist(url, downloads_dir, use_auth)
            input("\nPress Enter to continue...")
        
        elif choice == "2":
            url = get_url_from_user("Enter Track URL:")
            if url:
                download_single_track(url, downloads_dir / "Singles")
            input("\nPress Enter to continue...")
        
        elif choice == "3":
            url = get_url_from_user("Enter Album URL:")
            if url:
                download_album(url, downloads_dir)
            input("\nPress Enter to continue...")
        
        elif choice == "4":
            query = input("Enter song/artist name to search: ").strip()
            if query:
                search_and_download(query, downloads_dir)
            input("\nPress Enter to continue...")
        
        elif choice == "5":
            print("Enter URLs (one per line, empty line to finish):")
            urls = []
            while True:
                line = input().strip()
                if not line:
                    break
                urls.append(line)
            if urls:
                output_format = get_format_selection()
                batch_download(urls, downloads_dir, output_format)
            input("\nPress Enter to continue...")
        
        elif choice == "6":
            manage_downloaded_files(downloads_dir)
            input("\nPress Enter to continue...")
        
        elif choice == "7":
            show_download_history()
            input("\nPress Enter to continue...")
        
        elif choice == "8":
            show_settings_menu()
        
        elif choice == "0":
            print("\nGoodbye! Thanks for using SDown Loader")
            break
        
        else:
            print("Invalid option")

if __name__ == "__main__":
    main()