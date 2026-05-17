#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SDown Loader - Spotify Downloader
تطبيق متكامل لتحميل الأغاني من Spotify
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
    print("✗ Error: Python 3.7 or higher required")
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
للتثبيت على Windows:
  1. حمل FFmpeg من: https://www.gyan.dev/ffmpeg/builds/
  2. فك الضغط وأضف المجلد bin إلى PATH
  3. أو استخدم: winget install ffmpeg
"""
    elif system == 'darwin':
        return """
للتثبيت على macOS:
  brew install ffmpeg
"""
    else:
        return """
للتثبيت على Linux:
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
    print(f"🎵 Downloading single track...")
    print(f"🔗 {url}")
    print(f"📁 Folder: {output_dir}")
    print(f"📦 Format: {output_format}")
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
        save_history({"type": "track", "url": url, "format": output_format, "time": str(Path().stat().st_ctime) if Path().exists() else ""})
    return success

def download_album(url, output_dir, output_format="mp3"):
    url = url.split('?')[0].split('#')[0].strip()
    
    if not re.match(r'https://(open\.)?spotify\.com/album/[a-zA-Z0-9]+', url):
        print("❌ رابط ألبوم غير صحيح")
        return False
    
    album_id = re.search(r'album/([a-zA-Z0-9]+)', url)
    album_name = f"Album_{album_id.group(1)}" if album_id else "Album"
    
    output_dir = output_dir / sanitize_filename(album_name)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\n{'='*60}")
    print(f"💿 Downloading album: {album_name}")
    print(f"🔗 {url}")
    print(f"📁 المجلد: {output_dir}")
    print(f"📦 الصيغة: {output_format}")
    print(f"{'='*60}")
    
    cmd = get_python_cmd() + [
        "spotdl",
        url,
        "--output", str(output_dir),
        "--output-format", output_format
    ]
    
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
    downloaded = 0
    total = 0
    
    for line in process.stdout:
        print(line, end='', flush=True)
        if "Downloaded" in line:
            downloaded += 1
        if "Skipping" in line:
            downloaded += 1
    
    process.wait()
    success = process.returncode == 0
    if success:
        save_history({"type": "album", "name": album_name, "url": url, "format": output_format})
    return success

def download_playlist(url, output_dir, use_auth=False, output_format="mp3"):
    url = url.split('?')[0].split('#')[0].strip()
    
    if not re.match(r'https://(open\.)?spotify\.com/playlist/[a-zA-Z0-9]+', url):
        print("❌ رابط playlist غير صحيح")
        return False
    
    playlist_id = re.search(r'playlist/([a-zA-Z0-9]+)', url)
    playlist_name = f"Playlist_{playlist_id.group(1)}" if playlist_id else "Playlist"
    
    output_dir = output_dir / sanitize_filename(playlist_name)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\n{'='*60}")
    print(f"📋 Downloading Playlist...")
    print(f"🔗 {url}")
    print(f"📁 المجلد: {output_dir}")
    print(f"📦 الصيغة: {output_format}")
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
    
    progress = {"current": 0, "total": 0, "errors": []}
    
    for line in process.stdout:
        print(line, end='', flush=True)
        line_lower = line.lower()
        if "downloading [" in line_lower:
            progress["current"] += 1
        elif "error" in line_lower:
            progress["errors"].append(line.strip())
    
    process.wait()
    
    if process.returncode == 0:
        print(f"\n✅ تم تحميل الـ Playlist بنجاح!")
        print(f"📁 الملفات في: {os.path.abspath(output_dir)}")
        save_history({"type": "playlist", "name": playlist_name, "url": url, "format": output_format})
        return True
    return False

def batch_download(urls, output_dir, output_format="mp3"):
    print(f"\n{'='*60}")
    print(f"📚 Downloading {len(urls)} items...")
    print(f"{'='*60}")
    
    success_count = 0
    for i, url in enumerate(urls, 1):
        print(f"\n📥 تحميل {i}/{len(urls)}")
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
            print(f"❌ خطأ في {url}: {e}")
    
    print(f"\n{'='*60}")
    print(f"✅ تم تحميل {success_count}/{len(urls)} بنجاح")
    print(f"{'='*60}")
    return success_count

def manage_downloaded_files(downloads_dir):
    files = list_downloaded_files(downloads_dir)
    
    if not files:
        print("\n📁 لا توجد ملفات محملة")
        return
    
    print(f"\n{'='*60}")
    print(f"📂 الملفات المحملة ({len(files)} ملف)")
    print(f"{'='*60}")
    
    total_size = 0
    for i, f in enumerate(files, 1):
        size = f.stat().st_size
        total_size += size
        size_str = format_size(size)
        print(f"{i:3}. {f.name[:50]:50} {size_str:>10}")
    
    print(f"\n📊 المساحة الإجمالية: {format_size(total_size)}")
    print(f"\nاختر:")
    print("  [D] حذف ملف")
    print("  [O] فتح المجلد")
    print("  [C] حذف الكل")
    print("  [0]戻る")
    
    choice = input("👉 اختيارك: ").strip().lower()
    
    if choice == "d":
        try:
            num = int(input("رقم الملف للحذف: "))
            if 1 <= num <= len(files):
                files[num-1].unlink()
                print("✅ تم الحذف")
        except:
            print("❌ خطأ")
    elif choice == "c":
        confirm = input("هل أنت متأكد؟ (y/n): ").strip().lower()
        if confirm == 'y':
            for f in files:
                try:
                    f.unlink()
                except:
                    pass
            print("✅ تم حذف الكل")
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
    print(f"📜 سجل التحميل ({len(history)})")
    print(f"{'='*60}")
    
    if not history:
        print("لا يوجد سجل")
        return
    
    for i, item in enumerate(history[:20], 1):
        item_type = item.get("type", "unknown")
        url = item.get("url", "")
        fmt = item.get("format", "mp3")
        name = item.get("name", "")
        
        type_icon = {"playlist": "📋", "album": "💿", "track": "🎵"}.get(item_type, "📄")
        print(f"{i:2}. {type_icon} {item_type.upper():8} | {fmt:5} | {name or url[:40]}")

def get_format_selection():
    print("\n📦 اختر الصيغة:")
    print("  [1] MP3 (افتراضي)")
    print("  [2] FLAC (جودة عالية)")
    print("  [3] M4A")
    print("  [4] WAV")
    print("  [5] OGG")
    
    choice = input("👉 اختيارك [1]: ").strip()
    formats = {"1": "mp3", "2": "flac", "3": "m4a", "4": "wav", "5": "ogg"}
    return formats.get(choice, "mp3")

def search_and_download(query, output_dir):
    print(f"\n{'='*60}")
    print(f"🔍 البحث عن: {query}")
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
    
    results = []
    for line in process.stdout:
        print(line, end='', flush=True)
        if "Found" in line and "result" in line:
            results.append(line.strip())
    
    process.wait()
    return process.returncode == 0

def show_menu():
    print("\n" + "="*60)
    print("🎵 SDown Loader - القائمة الرئيسية".center(50))
    print("="*60)
    print("""
اختر نوع التحميل:

  [1] 📋 تحميل Playlist كامل
  [2] 🎵 تحميل أغنية واحدة
  [3] 💿 تحميل ألبوم كامل
  [4] 🔍 بحث وتحميل
  [5] 📚 تحميل مجموعة روابط
  [6] 📂 إدارة الملفات المحملة
  [7] 📜 سجل التحميل
  [8] ⚙️  الإعدادات
  [0] 🚪 خروج

""")
    
    choice = input("👉 اختيارك: ").strip()
    return choice

def show_about():
    print("\n" + "="*60)
    print("ℹ️  حول التطبيق".center(50))
    print("="*60)
    print("""
🎵 SDown Loader - الإصدار المحسن

  📌 الإصدار: 2.0.0
  📅 التحديث: 2026
  
  👤 المطور: werlist99
  📞 تواصل: @werlist99 (Telegram)
  
  💻 متوافق مع:
     - Windows
     - macOS  
     - Linux
  
  📚 المميزات:
     - تحميل Playlist
     - تحميل أغاني وألبومات
     - بحث وتحميل
     - دعم صيغ متعددة
  
  📂 رابط GitHub: (اضافة رابطك هنا)
  
  📢 للتواصل والدعم:
     Telegram: @werlist99
""")
    input("\nاضغط Enter للعودة...")

def show_settings_menu():
    while True:
        print("\n" + "="*60)
        print("⚙️  الإعدادات".center(50))
        print("="*60)
        print("""
  [1] 🔐 إعداد Spotify Authentication
  [2] 📁 تغيير مجلد التحميل
  [3] 🔄 تحديث spotdl
  [4] ℹ️  حالة المتطلبات
  [5] 🆕 التحقق من التحديثات
  [6] ℹ️  حول التطبيق
  [0] 🔙 العودة

""")
        choice = input("👉 اختيارك: ").strip()
        
        if choice == "1":
            print("\n📝 لتعزيل Authentication:")
            print("   1. اذهب إلى: https://developer.spotify.com/dashboard")
            print("   2. أنشئ تطبيق جديد")
            print("   3. احصل على Client ID و Client Secret")
            print("   4. شغل: py -3 -m spotdl --user-auth")
            print("   5. سيتم فتح المتصفح للتسجيل")
            input("\nاضغط Enter للعودة...")
        elif choice == "3":
            print("🔄 جاري تحديث spotdl...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "spotdl"])
                print("✅ تم التحديث بنجاح!")
            except:
                print("❌ فشل التحديث")
            input("اضغط Enter للعودة...")
        elif choice == "4":
            print("\n📋 حالة المتطلبات:")
            spotdl_ok = check_dependencies()
            ffmpeg_ok = check_ffmpeg()
            print(f"   {'✅' if spotdl_ok else '❌'} spotdl: {'مثبت' if spotdl_ok else 'غير مثبت'}")
            print(f"   {'✅' if ffmpeg_ok else '❌'} FFmpeg: {'مثبت' if ffmpeg_ok else 'غير مثبت'}")
            input("\nاضغط Enter للعودة...")
        elif choice == "5":
            print("🔍 جاري التحقق من التحديثات...")
            try:
                result = subprocess.run([sys.executable, "-m", "pip", "index", "versions", "spotdl"], 
                                      capture_output=True, text=True, timeout=10)
                print(result.stdout if result.stdout else "التطبيق محدث")
            except:
                print("تعذر التحقق")
            input("اضغط Enter للعودة...")
        elif choice == "6":
            show_about()
        elif choice == "0":
            break

def get_url_from_user(prompt_text):
    url = None
    
    if HAS_CLIPBOARD:
        try:
            clipboard_text = pyperclip.paste()
            if clipboard_text and "spotify.com" in clipboard_text.strip():
                print(f"📋 تم العثور على رابط في الحافظة:")
                print(f"   {clipboard_text.strip()}")
                use_clip = input(f"\n{prompt_text} (y/n, default: y): ").strip().lower()
                if use_clip != 'n':
                    url = clipboard_text.strip()
        except:
            pass
    
    if not url:
        print(prompt_text)
        print("مثال: https://open.spotify.com/playlist/...")
        url = input("👉 ").strip()
    
    return url

def main():
    global HAS_CLIPBOARD
    
    if sys.platform == 'win32':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    
    print("\n" + "="*60)
    print("🎵 Spotify Downloader - الإصدار المحسن".center(50))
    print("="*60)
    
    if not check_dependencies():
        print("\n⚠️  spotdl غير مثبت")
        response = input("هل تريد تثبيته الآن؟ (y/n): ").strip().lower()
        if response == 'y':
            print("جاري التثبيت...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", "spotdl"])
                print("✅ تم التثبيت بنجاح!")
            except:
                print("❌ فشل التثبيت")
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
        print("\n⚠️  FFmpeg غير مثبت")
        print(get_ffmpeg_install_instructions())
        return
    
    downloads_dir = Path("downloads")
    downloads_dir.mkdir(exist_ok=True)
    
    while True:
        choice = show_menu()
        
        if choice == "1":
            url = get_url_from_user("أدخل رابط الـ Playlist:")
            if url:
                use_auth = input("هل تريد استخدام Authentication؟ (y/n): ").strip().lower() == 'y'
                download_playlist(url, downloads_dir, use_auth)
            input("\nاضغط Enter للعودة...")
        
        elif choice == "2":
            url = get_url_from_user("أدخل رابط الأغنية:")
            if url:
                download_single_track(url, downloads_dir / "Singles")
            input("\nاضغط Enter للعودة...")
        
        elif choice == "3":
            url = get_url_from_user("أدخل رابط الألبوم:")
            if url:
                download_album(url, downloads_dir)
            input("\nاضغط Enter للعودة...")
        
        elif choice == "4":
            query = input("🔍 أدخل اسم الأغنية أو الفنان للبحث: ").strip()
            if query:
                search_and_download(query, downloads_dir)
            input("\nاضغط Enter للعودة...")
        
        elif choice == "5":
            show_settings_menu()
        
        elif choice == "0":
            print("\n👋وداعاً! وشكراً لاستخدام SDown Loader")
            break
        
        else:
            print("❌ خيار غير صحيح")

if __name__ == "__main__":
    main()