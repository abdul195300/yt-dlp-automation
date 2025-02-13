import requests
import os
import yt_dlp

def extract_video_url(tweet_url):
    """استخراج رابط الفيديو بدون تحميله باستخدام yt-dlp"""
    ydl_opts = {
        'quiet': True,
        'simulate': True,  # لا تقم بالتحميل، فقط استخرج المعلومات
        'format': 'best',
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(tweet_url, download=False)
            if 'entries' in info:
                video_info = info['entries'][0]  # أول فيديو في القائمة
            else:
                video_info = info
            
            if 'url' in video_info:
                return video_info['url']
            else:
                return None
    except yt_dlp.utils.DownloadError:
        return None

# استلام رابط التغريدة من GitHub Actions
tweet_url = os.getenv("TWEET_URL")

# استخراج رابط الفيديو
video_url = extract_video_url(tweet_url)

# رابط الـ Webhook في Make.com
MAKE_WEBHOOK_URL = "https://hook.eu2.make.com/ijtimfp41bqh6upl2qnmvcqu6fyacizl"  # استبدل هذا بـ رابط Webhook الفعلي في Make.com

if video_url:
    payload = {
        "tweet_url": tweet_url,
        "video_url": video_url
    }
    headers = {"Content-Type": "application/json"}
    
    response = requests.post(MAKE_WEBHOOK_URL, json=payload, headers=headers)

    if response.status_code == 200:
        print("✅ تم إرسال الرابط بنجاح إلى Make.com!")
    else:
        print(f"❌ فشل الإرسال! كود الخطأ: {response.status_code}")
else:
    print("❌ الرابط لا يحتوي على فيديو.")
