import praw
import yt_dlp
import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request
import json

# إعدادات Reddit API من المتغيرات البيئية
reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    user_agent=os.getenv("REDDIT_USER_AGENT"),
)

# رابط المنشور من متغير بيئي
post_url = os.getenv("REDDIT_POST_URL")
submission = reddit.submission(url=post_url)

# استخراج رابط الفيديو
video_url = None
if "media" in submission.__dict__ and submission.media and "reddit_video" in submission.media:
    video_url = submission.media["reddit_video"]["fallback_url"]
elif submission.url.endswith(('.mp4', '.m3u8')) or "v.redd.it" in submission.url:
    video_url = submission.url

if not video_url:
    raise ValueError("No video found in the post!")

# تحميل الفيديو مع الصوت
final_video_file = "reddit_video_with_audio.mp4"
ydl_opts = {
    'outtmpl': final_video_file,
    'format': 'bestvideo+bestaudio/best',
    'merge_output_format': 'mp4',
    'quiet': True,
}

with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    ydl.download([post_url])
print("Video downloaded successfully")

# إعداد Google Drive API
SCOPES = ['https://www.googleapis.com/auth/drive']
creds_json = os.getenv("GOOGLE_CREDENTIALS")  # يتم تمريره كـ JSON string
creds_dict = json.loads(creds_json)
creds = Credentials.from_authorized_user_info(creds_dict, SCOPES)

if creds and creds.expired and creds.refresh_token:
    creds.refresh(Request())

service = build('drive', 'v3', credentials=creds)

# رفع الفيديو إلى Google Drive
file_metadata = {'name': 'reddit_video_with_audio.mp4'}
media = MediaFileUpload(final_video_file, mimetype='video/mp4')
file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()

file_id = file.get('id')
print(f"Video uploaded to Google Drive! File ID: {file_id}")

# جعل الملف عامًا
service.permissions().create(
    fileId=file_id,
    body={'role': 'reader', 'type': 'anyone'}
).execute()

# إنشاء الرابط المباشر
direct_link = f"https://drive.google.com/uc?export=download&id={file_id}"
print(f"Direct link: {direct_link}")

# حذف الملف المحلي
if os.path.exists(final_video_file):
    os.remove(final_video_file)
    print(f"Local file deleted: {final_video_file}")
