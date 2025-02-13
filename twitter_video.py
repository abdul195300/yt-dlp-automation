import yt_dlp
import requests
import os

# رابط السيرفر المحلي في PyCharm (تأكد من تشغيل Flask في PyCharm)
PYCHARM_SERVER_URL = "http://127.0.0.1:5000/receive_video"

# استلام رابط التغريدة من GitHub Actions
tweet_url = os.getenv("TWEET_URL")

def extract_twitter_video(url):
    """ استخراج رابط الفيديو من تغريدة تويتر دون تحميل """
    
    ydl_opts = {
        'quiet': True,
        'noplaylist': True,  # عدم التعامل مع قوائم التشغيل
        'extract_flat': True,  # استخراج الروابط فقط دون تحميل
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

            if 'entries' in info:
                video_info = info['entries'][0]
            else:
                video_info = info

            if 'url' not in video_info:
                print("❌ التغريدة لا تحتوي على فيديو.")
                return None

            video_url = video_info['url']
            print(f"🎥 رابط الفيديو المباشر: {video_url}")
            return video_url

    except yt_dlp.utils.DownloadError as e:
        print(f"⚠️ خطأ أثناء استخراج الفيديو: {str(e)}")
        return None

# استخراج رابط الفيديو
video_url = extract_twitter_video(tweet_url)

# إرسال الرابط إلى PyCharm
if video_url:
    data = {"video_url": video_url}
    try:
        response = requests.post(PYCHARM_SERVER_URL, json=data)
        print(f"📩 تم إرسال الرابط إلى PyCharm بنجاح! ✅ (Status Code: {response.status_code})")
    except Exception as e:
        print(f"⚠️ فشل إرسال الرابط إلى PyCharm: {e}")
else:
    print("❌ لم يتم العثور على رابط فيديو.")
