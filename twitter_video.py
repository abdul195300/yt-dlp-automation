import yt_dlp
import sys
import json
import requests

WEBHOOK_URL = "https://your-server.com/api/github-result"  # ضع API لاستقبال النتيجة

def check_twitter_video(url):
    ydl_opts = {'format': 'bestvideo+bestaudio/best', 'quiet': True}

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

            if 'entries' in info:
                video_info = info['entries'][0]
            else:
                video_info = info

            if 'formats' not in video_info or not video_info['formats']:
                result = {"tweet_url": url, "video_url": "❌ الرابط لا يحتوي على فيديو."}
            else:
                result = {"tweet_url": url, "video_url": video_info['url']}

            # إرسال النتيجة إلى API
            requests.post(WEBHOOK_URL, json=result)
            print(json.dumps(result))  # طباعة النتيجة

    except yt_dlp.utils.DownloadError:
        result = {"tweet_url": url, "video_url": "❌ الرابط لا يحتوي على فيديو."}
        requests.post(WEBHOOK_URL, json=result)
        print(json.dumps(result))

if __name__ == "__main__":
    tweet_url = sys.argv[1]
    check_twitter_video(tweet_url)
