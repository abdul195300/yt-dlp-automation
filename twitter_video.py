import yt_dlp
import os
import requests

# 🔹 الحصول على رابط التغريدة من GitHub Actions
tweet_url = os.getenv("TWEET_URL")

if not tweet_url:
    print("❌ لم يتم توفير رابط التغريدة!")
    exit(1)

# 🔹 إعداد yt-dlp لاستخراج رابط الفيديو فقط
ydl_opts = {
    'quiet': True,
    'no_warnings': True,
    'extract_flat': True
}

try:
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(tweet_url, download=False)
        
        if 'entries' in info:
            video_info = info['entries'][0]
        else:
            video_info = info

        if 'url' in video_info:
            video_url = video_info['url']
            print(f"🎥 رابط الفيديو المباشر: {video_url}")

            # 🔹 إرسال الرابط إلى PyCharm عبر Flask
            response = requests.post("http://127.0.0.1:5000/receive_video", json={"video_url": video_url})
            if response.status_code == 200:
                print("✅ تم إرسال الرابط إلى PyCharm بنجاح!")
            else:
                print("⚠️ فشل إرسال الرابط إلى PyCharm!")

        else:
            print("❌ الرابط لا يحتوي على فيديو.")

except Exception as e:
    print(f"⚠️ خطأ أثناء استخراج الرابط: {e}")
