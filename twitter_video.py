import yt_dlp

tweet_url = "https://x.com/Enezator/status/1888942584749084713"  # استبدل هذا برابط تغريدة تحتوي على فيديو

ydl_opts = {
    'quiet': False,  # جعل الإخراج مرئيًا لمساعدتنا في حل المشاكل
    'simulate': True,  # عدم تحميل الفيديو، فقط استخراج الرابط
    'format': 'best'
}

try:
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(tweet_url, download=False)
        if 'entries' in info:
            video_info = info['entries'][0]  # أول فيديو في القائمة
        else:
            video_info = info
        print("🎥 رابط الفيديو:", video_info.get("url"))
except yt_dlp.utils.DownloadError as e:
    print("❌ لم يتم العثور على فيديو! السبب:", e)
