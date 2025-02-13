import yt_dlp
import json
import requests
import os

def get_twitter_video_url(url):
    """استخراج رابط الفيديو المباشر بدون تحميله."""
    ydl_opts = {'quiet': True, 'socket_timeout': 10, 'noplaylist': True}

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            video_info = info['entries'][0] if 'entries' in info else info

            if 'formats' not in video_info or not video_info['formats']:
                return {"status": "error", "message": "❌ الرابط لا يحتوي على فيديو."}

            return {"status": "success", "video_url": video_info['url']}

    except yt_dlp.utils.DownloadError:
        return {"status": "error", "message": "❌ الرابط لا يحتوي على فيديو."}

# 🔹 جلب رابط التغريدة من Event Payload
event_payload_path = os.getenv("GITHUB_EVENT_PATH")
with open(event_payload_path, "r") as f:
    event_payload = json.load(f)
    tweet_url = event_payload["client_payload"]["tweet_url"]

result = get_twitter_video_url(tweet_url)

# 🔹 إرسال النتيجة إلى PyCharm عبر Webhook
PYCHARM_WEBHOOK = os.getenv("PYCHARM_WEBHOOK")
if PYCHARM_WEBHOOK:
    response = requests.post(PYCHARM_WEBHOOK, json=result)
    print(f"✅ تم إرسال النتيجة إلى PyCharm. حالة الإرسال: {response.status_code}")
else:
    print("⚠️ لم يتم تعيين Webhook لإرسال النتيجة.")
