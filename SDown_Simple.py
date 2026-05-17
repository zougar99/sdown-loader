#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Spotify Playlist Downloader - Simple Version
تطبيق بسيط: أعطه رابط playlist، سيحمّلها في مجلد بنفس الاسم
"""

import os
import sys
import subprocess
import re
from pathlib import Path

# Try to import clipboard functionality
try:
    import pyperclip
    HAS_CLIPBOARD = True
except ImportError:
    HAS_CLIPBOARD = False

# Check Python version
if sys.version_info < (3, 7):
    print("✗ Error: This script requires Python 3.7 or higher")
    sys.exit(1)

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import spotdl
        return True
    except ImportError:
        return False

def check_ffmpeg():
    """Check if FFmpeg is installed"""
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, 
                              text=True,
                              timeout=5)
        return result.returncode == 0
    except:
        return False

def sanitize_filename(name):
    """Remove invalid characters from filename"""
    # Remove invalid characters for Windows filenames
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        name = name.replace(char, '_')
    # Remove leading/trailing spaces and dots
    name = name.strip('. ')
    # Limit length
    if len(name) > 100:
        name = name[:100]
    return name

def get_playlist_name(url):
    """Extract playlist name from Spotify URL"""
    # Extract playlist ID
    match = re.search(r'playlist/([a-zA-Z0-9]+)', url)
    if not match:
        return "Playlist"
    
    playlist_id = match.group(1)
    
    # Try to get playlist name from spotdl (if available)
    # For now, we'll use a simple approach: use ID
    # The actual name will be set by spotdl when downloading
    return f"Playlist_{playlist_id}"

def download_playlist_simple(url, use_auth=False):
    """Download playlist to a folder with playlist name"""
    # Normalize URL
    url = url.split('?')[0].split('#')[0].strip()
    
    # Validate URL
    if not re.match(r'https://(open\.)?spotify\.com/playlist/[a-zA-Z0-9]+', url):
        print("❌ رابط غير صحيح. يجب أن يكون رابط playlist من Spotify")
        return False
    
    # Get playlist folder name
    playlist_id = re.search(r'playlist/([a-zA-Z0-9]+)', url)
    if playlist_id:
        playlist_id = playlist_id.group(1)
    else:
        playlist_id = "unknown"
    
    # Create downloads directory if it doesn't exist
    downloads_dir = Path("downloads")
    downloads_dir.mkdir(exist_ok=True)
    
    # Use playlist ID as folder name (spotdl will organize files inside)
    # The folder will be created by spotdl with proper naming
    output_dir = downloads_dir / f"Playlist_{playlist_id}"
    
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\n{'='*60}")
    print(f"📥 جاري تحميل: {url}")
    print(f"📁 سيتم الحفظ في: {output_dir}")
    if use_auth:
        print("🔐 استخدام Spotify authentication (يزيد الحد)")
        print("⚠️  تأكد من إعداد credentials أولاً")
        print("   راجع: RATE_LIMIT_HELP.txt للتعليمات")
    print(f"{'='*60}")
    print("⏳ قد يستغرق هذا بعض الوقت...")
    print("ℹ️  يستخدم YouTube Music للتحميل")
    print("ℹ️  يحتاج Spotify API للحصول على قائمة الأغاني")
    print()
    
    try:
        # Use spotdl to download playlist
        # Note: spotdl needs Spotify API to get playlist info
        cmd = [
            sys.executable, "-m", "spotdl",
            url,
            "--output", str(output_dir),
            "--output-format", "mp3"
        ]
        
        # Add authentication if requested (increases rate limit)
        if use_auth:
            cmd.append("--user-auth")
        
        print(f"🚀 بدء التحميل...\n")
        
        # Run spotdl
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        # Print output in real-time and capture errors
        error_output = []
        rate_limit_detected = False
        for line in process.stdout:
            print(line, end='', flush=True)
            # Check for rate limit error
            line_lower = line.lower()
            if "rate/request limit" in line_lower or "rate limit" in line_lower or "retry will occur after" in line_lower:
                error_output.append(line)
                rate_limit_detected = True
        
        process.wait()
        
        if process.returncode == 0:
            print(f"\n{'='*60}")
            print(f"✅ تم التحميل بنجاح!")
            print(f"📁 الملفات في: {os.path.abspath(output_dir)}")
            print(f"{'='*60}\n")
            return True
        else:
            print(f"\n{'='*60}")
            
            # Check if it's a rate limit error
            output_text = "".join(error_output) if error_output else ""
            if rate_limit_detected or "rate" in output_text.lower() or "limit" in output_text.lower() or "retry will occur" in output_text.lower():
                print("❌ وصلت إلى حد الطلبات من Spotify API")
                print("\n" + "="*60)
                print("📋 الحلول المتاحة:")
                print("="*60)
                print("\n1️⃣  الانتظار (الحل الأسهل):")
                print("   ⏰ انتظر 24 ساعة ثم جرب مرة أخرى")
                print("   📅 يمكنك المحاولة غداً في نفس الوقت")
                print("\n2️⃣  استخدام Spotify Authentication:")
                print("   🔐 هذا يزيد الحد بشكل كبير")
                print("   📝 أولاً، قم بإعداد Spotify credentials:")
                print("      - افتح: https://developer.spotify.com/dashboard")
                print("      - أنشئ تطبيق جديد")
                print("      - احصل على Client ID و Client Secret")
                print("   💻 ثم شغّل spotdl مع أي رابط playlist لإعداد authentication:")
                print("      py -3 -m spotdl --user-auth \"رابط_playlist\"")
                print("   🌐 سيتم فتح المتصفح - سجّل دخول ووافق على الصلاحيات")
                print("   ✅ بعدها استخدم:")
                print("      .\\run_simple.bat --auth \"رابط_playlist\"")
                print("\n3️⃣  استخدام VPN أو IP مختلف:")
                print("   🌐 قد يساعد في بعض الحالات")
                print("\n" + "="*60)
                print("ℹ️  ملاحظة: spotdl يحتاج Spotify API للحصول على قائمة الأغاني")
            else:
                print(f"❌ حدث خطأ أثناء التحميل")
                if error_output:
                    print("\nتفاصيل الخطأ:")
                    for err_line in error_output[-5:]:  # Show last 5 error lines
                        print(f"   {err_line.strip()}")
            
            print(f"\n{'='*60}\n")
            return False
            
    except KeyboardInterrupt:
        print(f"\n\n⚠️  تم إلغاء التحميل")
        return False
    except Exception as e:
        print(f"\n❌ خطأ: {str(e)}")
        return False

def main():
    """Main function"""
    global HAS_CLIPBOARD
    
    # Set UTF-8 encoding for Windows
    if sys.platform == 'win32':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    
    print("\n" + "="*60)
    print("🎵  Spotify Playlist Downloader - Simple  🎵".center(60))
    print("="*60)
    print()
    
    # Check dependencies
    if not check_dependencies():
        print("⚠️  spotdl غير مثبت")
        response = input("هل تريد تثبيته الآن؟ (y/n): ").strip().lower()
        if response == 'y':
            print("جاري التثبيت...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", "spotdl"])
                print("✅ تم التثبيت بنجاح!")
            except:
                print("❌ فشل التثبيت. يرجى تثبيته يدوياً: pip install spotdl")
                return
        else:
            print("❌ يرجى تثبيت spotdl أولاً: pip install spotdl")
            return
    
    # Try to install pyperclip for clipboard support (optional)
    if not HAS_CLIPBOARD:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyperclip"], 
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            import pyperclip
            HAS_CLIPBOARD = True
        except:
            pass  # pyperclip is optional
    
    # Check FFmpeg
    if not check_ffmpeg():
        print("\n⚠️  FFmpeg غير مثبت")
        print("FFmpeg مطلوب للعمل")
        print("\nلتثبيته:")
        print("  1. شغّل: install_ffmpeg.bat")
        print("  2. أو استخدم: winget install ffmpeg")
        print("  3. أو حمّل من: https://www.gyan.dev/ffmpeg/builds/")
        return
    
    # Get URL
    url = None
    use_auth = False
    
    # Check for --auth flag
    if len(sys.argv) > 1:
        if "--auth" in sys.argv:
            use_auth = True
            # Get URL (first non-flag argument)
            url = next((arg for arg in sys.argv[1:] if arg != "--auth" and not arg.startswith("--")), None)
        else:
            url = sys.argv[1]
    
    if not url:
        # Try to get from clipboard
        if HAS_CLIPBOARD:
            try:
                clipboard_text = pyperclip.paste()
                if clipboard_text and re.match(r'https://(open\.)?spotify\.com/playlist/[a-zA-Z0-9]+', clipboard_text.strip()):
                    print(f"📋 تم العثور على رابط في الحافظة:")
                    print(f"   {clipboard_text.strip()}")
                    use_clipboard = input("\nهل تريد استخدامه؟ (y/n, default: y): ").strip().lower()
                    if use_clipboard != 'n':
                        url = clipboard_text.strip()
            except:
                pass
        
        # If still no URL, ask user
        if not url:
            print("أدخل رابط Spotify Playlist:")
            print("(أو انسخ الرابط في الحافظة قبل التشغيل)")
            print("مثال: https://open.spotify.com/playlist/6yhn1XGZPfpWxwECruWDlR")
            print()
            url = input("👉 ").strip()
    
    if not url:
        print("❌ لم يتم إدخال رابط")
        return
    
    # Download
    download_playlist_simple(url, use_auth=use_auth)

if __name__ == "__main__":
    main()
