# SDown Loader

![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-blue)
![Python](https://img.shields.io/badge/Python-3.7%2B-green)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Version](https://img.shields.io/badge/Version-2.0.0-blue)

تطبيق متكامل لتحميل الأغاني من Spotify - يعمل على Windows و macOS و Linux

## المميزات

- 📋 تحميل Playlist كامل
- 🎵 تحميل أغنية واحدة
- 💿 تحميل ألبوم كامل
- 🔍 البحث وتحميل
- 📚 تحميل مجموعة روابط
- 📂 إدارة الملفات المحملة
- 📜 سجل التحميل
- 📦 دعم صيغ متعددة (MP3, FLAC, M4A, WAV, OGG)
- ⚙️ إعدادات متقدمة
- 📋 دعم الحافظة (نسخ الرابط تلقائياً)

## تواصل

📞 **Telegram**: @werlist99

للدعم والاستفسارات تواصل معنا على Telegram

## المتطلبات

### Python
- Python 3.7 أو أعلى

### التبعيات
```bash
pip install spotdl pyperclip
```

### FFmpeg (مطلوب)
- **Windows**: حمل من [ffmpeg.org](https://www.gyan.dev/ffmpeg/builds/) أو استخدم `winget install ffmpeg`
- **macOS**: `brew install ffmpeg`
- **Linux**: `sudo apt install ffmpeg` (Debian/Ubuntu) أو `sudo pacman -S ffmpeg` (Arch)

## التثبيت

1. ثبت Python 3.7+ من [python.org](https://www.python.org/)
2. ثبت التبعيات:
```bash
pip install spotdl pyperclip
```
3. ثبت FFmpeg حسب نظامك

## الاستخدام

### تشغيل التطبيق
```bash
python spotify_downloader.py
```

### تحميل Playlist
اختر 1 وأدخل رابط الـ Playlist

### تحميل أغنية واحدة
اختر 2 وأدخل رابط الأغنية

### تحميل ألبوم
اختر 3 وأدخل رابط الألبوم

### البحث
اختر 4 وأدخل اسم الأغنية أو الفنان

## الأوامر المباشرة

```bash
# تحميل playlist
python spotify_downloader.py "https://open.spotify.com/playlist/..."

# تحميل مع authentication
python spotify_downloader.py --auth "https://open.spotify.com/playlist/..."
```

## هيكل المشروع

```
Spotify-Downloader/
├── spotify_downloader.py   # التطبيق الرئيسي
├── spotify_simple.py       # نسخة بسيطة
├── downloads/             # مجلد التحميلات (يُنشأ تلقائياً)
└── README.md              # هذا الملف
```

## استكشاف الأخطاء

### مشكلة FFmpeg
- تأكد من إضافة FFmpeg إلى PATH
- على Windows: أضف مسار ffmpeg/bin إلى متغيرات البيئة

### مشكلة Rate Limit
- انتظر 24 ساعة أو استخدم Spotify Authentication
- راجع: https://developer.spotify.com/dashboard

### مشكلة التثبيت
```bash
pip install --upgrade spotdl
```

## الترخيص

MIT License

## الإصدار

الإصدار الحالي: 2.0.0

## المطور

👤 **werlist99** - Telegram: @werlist99

## تحذير

هذا التطبيق للاستخدام الشخصي فقط. تأكد من احترام حقوق الملكية الفكرية.