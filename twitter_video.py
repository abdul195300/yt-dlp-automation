import yt_dlp
import requests
import os

# استلام رابط التغريدة من GitHub Actions
tweet_url = os.getenv("TWEET_URL")

if not tweet_url:
    print("❌ لم يتم توفير رابط التغريدة.")
    exit(1)

def extract_video_url(url):
    """ استخراج رابط الفيديو المباشر من تغريدة تويتر """
    ydl_opts = {
        'quiet': True,
        'skip_download': True,
        'force_generic_extractor': False
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            formats = info.get('formats', [])

            # البحث عن أفضل جودة فيديو متاحة
            video_url = next((f['url'] for f in formats if f['ext'] == 'mp4'), None)

            if video_url:
                return video_url
            else:
                return None

    except Exception as e:
        print(f"⚠️ خطأ أثناء استخراج الفيديو: {str(e)}")
        return None

# استخراج رابط الفيديو
video_url = extract_video_url(tweet_url)

if video_url:
    print(f"🎥 رابط الفيديو المباشر: {video_url}")

    # 🔹 إرسال الرابط إلى Make.com
    MAKE_WEBHOOK_URL = "https://hook.us1.make.com/xxxxxxx"  # استبدل بـ رابط Webhook الفعلي
    payload = {"tweet_url": tweet_url, "video_url": video_url}
    headers = {"Content-Type": "application/json"}

    response = requests.post(MAKE_WEBHOOK_URL, json=payload, headers=headers)

    if response.status_code == 200:
        print("✅ تم إرسال الرابط بنجاح إلى Make.com!")
    else:
        print(f"❌ فشل الإرسال! كود الخطأ: {response.status_code}")

else:
    print("❌ الرابط لا يحتوي على فيديو.")
