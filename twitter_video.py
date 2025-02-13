import yt_dlp
import json
import requests
import os

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")  # رمز API الخاص بـ GitHub
REPO_OWNER = "اسم_المستخدم_في_GitHub"
REPO_NAME = "اسم_المستودع_في_GitHub"

def get_twitter_video_url(url):
    """استخراج رابط الفيديو المباشر من تويتر بدون تحميل."""

    ydl_opts = {'quiet': True, 'socket_timeout': 10, 'noplaylist': True}

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            video_info = info['entries'][0] if 'entries' in info else info

            if 'formats' not in video_info or not video_info['formats']:
                return "❌ الرابط لا يحتوي على فيديو."

            return f"✅ رابط الفيديو: {video_info['url']}"

    except yt_dlp.utils.DownloadError:
        return "❌ الرابط لا يحتوي على فيديو."

# 🔹 جلب رابط التغريدة من Event Payload
event_payload_path = os.getenv("GITHUB_EVENT_PATH")
with open(event_payload_path, "r") as f:
    event_payload = json.load(f)
    tweet_url = event_payload["client_payload"]["tweet_url"]

result = get_twitter_video_url(tweet_url)

# 🔹 إرسال النتيجة إلى PyCharm عبر GitHub API
def send_result_to_pycharm(result):
    response = requests.post(
        f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/issues",
        headers={"Authorization": f"token {GITHUB_TOKEN}"},
        json={"title": "نتيجة تحليل التغريدة", "body": result}
    )
    print(response.json())

send_result_to_pycharm(result)
