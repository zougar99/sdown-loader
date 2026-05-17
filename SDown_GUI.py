#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SDown Loader - GUI Version
تطبيق تحميل Spotify بواجهة رسومية
"""

import os
import sys
import subprocess
import re
import json
import threading
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path
from urllib.parse import urlparse

try:
    import pyperclip
    HAS_CLIPBOARD = True
except ImportError:
    HAS_CLIPBOARD = False

APP_VERSION = "2.0.0"
DEV_NAME = "zougar99"
GITHUB = "https://github.com/zougar99/sdown-loader"
TELEGRAM = "@werlist99"

class SpotifyDownloaderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title(f"SDown Loader v{APP_VERSION}")
        self.root.geometry("700x600")
        self.root.resizable(False, False)
        
        self.download_dir = Path("downloads")
        self.download_dir.mkdir(exist_ok=True)
        
        self.settings = self.load_settings()
        self.history = self.load_history()
        
        self.setup_styles()
        self.create_widgets()
        self.check_dependencies()
    
    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'), foreground='#1DB954')
        style.configure('TButton', font=('Arial', 10), padding=6)
        style.configure('TEntry', font=('Arial', 10))
        
    def load_settings(self):
        if Path("settings.json").exists():
            try:
                with open("settings.json", "r") as f:
                    return json.load(f)
            except:
                pass
        return {
            "download_dir": "downloads",
            "format": "mp3",
            "quality": "normal",
            "use_auth": False
        }
    
    def save_settings(self):
        with open("settings.json", "w") as f:
            json.dump(self.settings, f)
    
    def load_history(self):
        if Path("download_history.json").exists():
            try:
                with open("download_history.json", "r") as f:
                    return json.load(f)
            except:
                pass
        return []
    
    def save_history_entry(self, entry):
        self.history.insert(0, entry)
        if len(self.history) > 50:
            self.history = self.history[:50]
        with open("download_history.json", "w") as f:
            json.dump(self.history, f, ensure_ascii=False)
    
    def check_dependencies(self):
        try:
            import spotdl
            self.lbl_status.config(text="✅ spotdl مثبت", foreground="green")
        except:
            self.lbl_status.config(text="⚠️ spotdl غير مثبت", foreground="orange")
        
        import shutil
        if shutil.which("ffmpeg"):
            self.lbl_ffmpeg.config(text="✅ FFmpeg مثبت", foreground="green")
        else:
            self.lbl_ffmpeg.config(text="⚠️ FFmpeg غير مثبت", foreground="orange")
    
    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill=tk.X, pady=(0, 20))
        
        lbl_title = ttk.Label(title_frame, text=f"🎵 SDown Loader v{APP_VERSION}", style='Title.TLabel')
        lbl_title.pack()
        
        lbl_dev = ttk.Label(title_frame, text=f"👤 {DEV_NAME} | 📞 {TELEGRAM}", font=('Arial', 9))
        lbl_dev.pack(pady=5)
        
        link_frame = ttk.LabelFrame(main_frame, text="📋 الرابط", padding="10")
        link_frame.pack(fill=tk.X, pady=10)
        
        self.entry_url = ttk.Entry(link_frame, width=60, font=('Arial', 11))
        self.entry_url.pack(side=tk.LEFT, padx=(0, 10))
        
        btn_paste = ttk.Button(link_frame, text="📋 لصق", command=self.paste_from_clipboard)
        btn_paste.pack(side=tk.LEFT)
        
        options_frame = ttk.LabelFrame(main_frame, text="⚙️ الإعدادات", padding="10")
        options_frame.pack(fill=tk.X, pady=10)
        
        format_frame = ttk.Frame(options_frame)
        format_frame.pack(fill=tk.X, pady=5)
        ttk.Label(format_frame, text="📦 الصيغة:").pack(side=tk.LEFT)
        self.combo_format = ttk.Combobox(format_frame, values=["mp3", "flac", "m4a", "wav", "ogg"], 
                                         state="readonly", width=10)
        self.combo_format.set(self.settings.get("format", "mp3"))
        self.combo_format.pack(side=tk.LEFT, padx=10)
        
        quality_frame = ttk.Frame(options_frame)
        quality_frame.pack(fill=tk.X, pady=5)
        ttk.Label(quality_frame, text="🎚️ الجودة:").pack(side=tk.LEFT)
        self.combo_quality = ttk.Combobox(quality_frame, values=["low", "normal", "high"], 
                                          state="readonly", width=10)
        self.combo_quality.set(self.settings.get("quality", "normal"))
        self.combo_quality.pack(side=tk.LEFT, padx=10)
        
        dir_frame = ttk.Frame(options_frame)
        dir_frame.pack(fill=tk.X, pady=5)
        ttk.Label(dir_frame, text="📁 المجلد:").pack(side=tk.LEFT)
        self.entry_dir = ttk.Entry(dir_frame, width=35)
        self.entry_dir.insert(0, self.settings.get("download_dir", "downloads"))
        self.entry_dir.pack(side=tk.LEFT, padx=10)
        btn_dir = ttk.Button(dir_frame, text="📂 اختيار", command=self.choose_directory)
        btn_dir.pack(side=tk.LEFT)
        
        self.btn_download = ttk.Button(main_frame, text="⬇️ تحميل الآن", command=self.start_download)
        self.btn_download.pack(pady=20, ipadx=30)
        
        progress_frame = ttk.LabelFrame(main_frame, text="📊 التقدم", padding="10")
        progress_frame.pack(fill=tk.X, pady=10)
        
        self.progress_bar = ttk.Progressbar(progress_frame, mode='indeterminate')
        self.progress_bar.pack(fill=tk.X)
        
        self.lbl_progress = ttk.Label(progress_frame, text="جاهز", font=('Arial', 9))
        self.lbl_progress.pack(pady=5)
        
        log_frame = ttk.LabelFrame(main_frame, text="📜 السجل", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.text_log = tk.Text(log_frame, height=8, font=('Consolas', 9))
        self.text_log.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(log_frame, command=self.text_log.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_log.config(yscrollcommand=scrollbar.set)
        
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.lbl_status = ttk.Label(status_frame, text="...", font=('Arial', 8))
        self.lbl_status.pack(side=tk.LEFT)
        
        self.lbl_ffmpeg = ttk.Label(status_frame, text="...", font=('Arial', 8))
        self.lbl_ffmpeg.pack(side=tk.RIGHT)
        
        menu_bar = tk.Menu(self.root)
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="📂 فتح مجلد التحميل", command=self.open_download_folder)
        file_menu.add_command(label="⚙️ الإعدادات", command=self.show_settings)
        file_menu.add_separator()
        file_menu.add_command(label="🚪 خروج", command=self.root.quit)
        menu_bar.add_cascade(label="📁 ملف", menu=file_menu)
        
        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="ℹ️ حول", command=self.show_about)
        help_menu.add_command(label="📞 تواصل - Telegram", command=self.open_telegram)
        menu_bar.add_cascade(label="❓ مساعدة", menu=help_menu)
        
        self.root.config(menu=menu_bar)
    
    def paste_from_clipboard(self):
        if HAS_CLIPBOARD:
            try:
                text = pyperclip.paste()
                if text and "spotify.com" in text:
                    self.entry_url.delete(0, tk.END)
                    self.entry_url.insert(0, text)
            except:
                pass
    
    def choose_directory(self):
        folder = filedialog.askdirectory()
        if folder:
            self.entry_dir.delete(0, tk.END)
            self.entry_dir.insert(0, folder)
    
    def log(self, message):
        self.text_log.insert(tk.END, f"{message}\n")
        self.text_log.see(tk.END)
    
    def start_download(self):
        url = self.entry_url.get().strip()
        
        if not url:
            messagebox.showwarning("تحذير", "الرجاء إدخال الرابط")
            return
        
        if not re.match(r'https://(open\.)?spotify\.com/(playlist|track|album)/[a-zA-Z0-9]+', url):
            messagebox.showerror("خطأ", "رابط Spotify غير صحيح")
            return
        
        self.settings["format"] = self.combo_format.get()
        self.settings["quality"] = self.combo_quality.get()
        self.settings["download_dir"] = self.entry_dir.get()
        self.save_settings()
        
        self.btn_download.config(state=tk.DISABLED)
        self.progress_bar.start()
        self.log("🚀 جاري بدء التحميل...")
        
        thread = threading.Thread(target=self.download_thread, args=(url,))
        thread.daemon = True
        thread.start()
    
    def download_thread(self, url):
        output_dir = Path(self.entry_dir.get())
        output_dir.mkdir(parents=True, exist_ok=True)
        
        fmt = self.combo_format.get()
        
        cmd = [sys.executable, "-m", "spotdl", url, "--output", str(output_dir), "--output-format", fmt]
        
        try:
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, 
                                      text=True, bufsize=1)
            
            for line in process.stdout:
                self.root.after(0, lambda l=line: self.log(l.strip()))
            
            process.wait()
            
            self.root.after(0, self.download_complete)
            
        except Exception as e:
            self.root.after(0, lambda: self.log(f"❌ خطأ: {str(e)}"))
            self.root.after(0, self.download_failed)
    
    def download_complete(self):
        self.progress_bar.stop()
        self.btn_download.config(state=tk.NORMAL)
        self.lbl_progress.config(text="✅ تم التحميل بنجاح!")
        self.log("✅ تم التحميل بنجاح!")
        
        entry = {"url": self.entry_url.get(), "format": self.combo_format.get(), 
                 "time": str(Path().stat().st_mtime) if Path().exists() else ""}
        self.save_history_entry(entry)
        
        messagebox.showinfo("نجاح", "تم تحميل الملف بنجاح!")
    
    def download_failed(self):
        self.progress_bar.stop()
        self.btn_download.config(state=tk.NORMAL)
        self.lbl_progress.config(text="❌ فشل التحميل")
        self.log("❌ فشل التحميل")
    
    def open_download_folder(self):
        folder = self.entry_dir.get()
        if sys.platform == 'win32':
            os.startfile(folder)
        elif sys.platform == 'darwin':
            subprocess.run(['open', folder])
        else:
            subprocess.run(['xdg-open', folder])
    
    def show_settings(self):
        settings_win = tk.Toplevel(self.root)
        settings_win.title("الإعدادات")
        settings_win.geometry("400x300")
        
        ttk.Label(settings_win, text="⚙️ إعدادات التطبيق", font=('Arial', 14, 'bold')).pack(pady=20)
        
        ttk.Label(settings_win, text=f"الإصدار: {APP_VERSION}").pack()
        ttk.Label(settings_win, text=f"المطور: {DEV_NAME}").pack()
        ttk.Label(settings_win, text=f"تيليجرام: {TELEGRAM}").pack(pady=20)
        
        ttk.Button(settings_win, text="🔄 تحديث spotdl", command=self.update_spotdl).pack(pady=10)
        ttk.Button(settings_win, text="إغلاق", command=settings_win.destroy).pack(pady=10)
    
    def update_spotdl(self):
        self.log("🔄 جاري تحديث spotdl...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "spotdl"])
            self.log("✅ تم التحديث بنجاح!")
            messagebox.showinfo("نجاح", "تم تحديث spotdl بنجاح!")
        except:
            self.log("❌ فشل التحديث")
            messagebox.showerror("خطأ", "فشل تحديث spotdl")
    
    def show_about(self):
        about_win = tk.Toplevel(self.root)
        about_win.title("حول التطبيق")
        about_win.geometry("350x250")
        
        ttk.Label(about_win, text=f"🎵 SDown Loader", font=('Arial', 14, 'bold')).pack(pady=20)
        ttk.Label(about_win, text=f"الإصدار: {APP_VERSION}").pack()
        ttk.Label(about_win, text=f"2026").pack(pady=10)
        ttk.Label(about_win, text="─" * 30).pack()
        ttk.Label(about_win, text=f"👤 المطور: {DEV_NAME}").pack(pady=5)
        ttk.Label(about_win, text=f"📞 Telegram: {TELEGRAM}").pack(pady=5)
        ttk.Label(about_win, text="─" * 30).pack(pady=10)
        ttk.Label(about_win, text="متوافق: Windows, macOS, Linux").pack()
        
        ttk.Button(about_win, text="إغلاق", command=about_win.destroy).pack(pady=20)
    
    def open_telegram(self):
        if sys.platform == 'win32':
            os.system("start https://t.me/werlist99")
        elif sys.platform == 'darwin':
            subprocess.run(["open", "https://t.me/werlist99"])
        else:
            subprocess.run(["xdg-open", "https://t.me/werlist99"])

def main():
    root = tk.Tk()
    
    if sys.platform == 'win32':
        try:
            root.iconbitmap("spotify.ico")
        except:
            pass
    
    app = SpotifyDownloaderGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()