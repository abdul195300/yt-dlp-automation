import yt_dlp
import os
import json

# قراءة البيانات الواردة من GitHub Actions
event_path = os.getenv("GITHUB_EVENT_PATH")  # استلام البيانات من GitHub
if event_path and os.path.exists(event_path):
    with open(event_path, "r") as event_file:
        event_payload = json.load(event_file)
        tweet_url = event_payload.get("inputs", {}).get("tweet_url", "")

if not tweet_url:
    print("❌ لم يتم استلام رابط التغريدة بشكل صحيح!")
    exit(1)

def extract_video_url(url):
    """استخراج رابط الفيديو المباشر بدون تحميله."""
    ydl_opts = {"quiet": True}

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if "entries" in info:
                video_info = info["entries"][0]
            else:
                video_info = info

            if "formats" not in video_info or not video_info["formats"]:
                print("❌ الرابط لا يحتوي على فيديو.")
                return

            video_url = video_info["url"]
            print(f"🎥 رابط الفيديو المباشر: {video_url}")

    except yt_dlp.utils.DownloadError:
        print("❌ الرابط لا يحتوي على فيديو.")

# تشغيل الوظيفة لاستخراج الرابط
extract_video_url(tweet_url)
