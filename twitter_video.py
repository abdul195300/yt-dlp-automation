import yt_dlp

def download_twitter_video(url):
    """تحميل الفيديو من تويتر باستخدام yt-dlp مع التحقق مما إذا كان الرابط يحتوي على فيديو."""

    ydl_opts = {
        'outtmpl': '%(title)s.%(ext)s',
        'format': 'bestvideo+bestaudio/best',
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)  # نحصل على معلومات الرابط بدون تحميل

            # التحقق مما إذا كان الرابط يحتوي على فيديو
            if 'entries' in info:
                # في حالة وجود قائمة تشغيل أو منشور يحتوي على وسائط متعددة
                video_info = info['entries'][0]  # نحصل على أول عنصر في القائمة
            else:
                video_info = info

            if 'formats' not in video_info or not video_info['formats']:
                print("❌ الرابط لا يحتوي على فيديو.")
                return

            # تحميل الفيديو إذا كان متاحًا
            ydl.download([url])
            print("✅ تم تحميل الفيديو بنجاح.")

    except yt_dlp.utils.DownloadError:
        print("❌ الرابط لا يحتوي على فيديو.")

# تجربة الكود برابط من تويتر
twitter_video_url = "https://x.com/NewsNow4USA/status/1889252022869782792"  # استبدل بالرابط الذي تريد اختباره
download_twitter_video(twitter_video_url)
