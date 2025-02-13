import yt_dlp

def download_twitter_video(url):
    """تحميل الفيديو من تويتر باستخدام yt-dlp مع التحقق مما إذا كان الرابط يحتوي على فيديو."""

    ydl_opts = {
        'outtmpl': '%(title)s.%(ext)s',
        'format': 'bestvideo+bestaudio/best',
        'verbose': True,  # لعرض تفاصيل التحميل
        'noplaylist': True,  # منع تحميل قائمة تشغيل بالكامل
        'socket_timeout': 30  # مهلة زمنية 30 ثانية لمنع التأخير الطويل
    }

    try:
        print(f"🔍 جاري تحليل رابط الفيديو: {url}")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

            # التحقق مما إذا كان الرابط يحتوي على فيديو
            if 'entries' in info:
                video_info = info['entries'][0]  # أول عنصر في القائمة
            else:
                video_info = info

            if 'formats' not in video_info or not video_info['formats']:
                print("❌ الرابط لا يحتوي على فيديو.")
                return

            # تحميل الفيديو إذا كان متاحًا
            print("🎥 جاري تحميل الفيديو...")
            ydl.download([url])
            print("✅ تم تحميل الفيديو بنجاح.")

    except yt_dlp.utils.DownloadError as e:
        print(f"⚠️ خطأ أثناء التحميل: {str(e)}")
        print("❌ الرابط لا يحتوي على فيديو.")

# تجربة الكود برابط من تويتر
twitter_video_url = "https://x.com/NewsNow4USA/status/1889252022869782792"  # استبدل بالرابط الذي تريد اختباره
download_twitter_video(twitter_video_url)
