import praw
import yt_dlp
import os
import base64
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request
import requests

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

# فك تشفير الكوكيز من REDDIT_COOKIES_BASE64 وحفظها في ملف مؤقت
cookies_base64 = os.getenv("REDDIT_COOKIES_BASE64")
if not cookies_base64:
    raise ValueError("REDDIT_COOKIES_BASE64 is not set!")

cookies_data = base64.b64decode(cookies_base64).decode('utf-8')
cookies_file = "reddit_cookies.txt"
with open(cookies_file, "w") as f:
    f.write(cookies_data)

# تحميل الفيديو مع الصوت باستخدام الكوكيز
final_video_file = "reddit_video_with_audio.mp4"
ydl_opts = {
    'outtmpl': final_video_file,
    'format': 'bestvideo+bestaudio/best',
    'merge_output_format': 'mp4',
    'quiet': True,
    'cookies': cookies_file,  # تمرير ملف الكوكيز
}

with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    ydl.download([post_url])
print("Video downloaded successfully")

# إعداد Google Drive API
SCOPES = ['https://www.googleapis.com/auth/drive']
creds_json_base64 = os.getenv("GDRIVE_TOKEN_BASE64")
creds_json = base64.b64decode(creds_json_base64).decode('utf-8')
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

# إعداد Airtable API
AIRTABLE_API_KEY = os.getenv("AIRTABLE_API_KEY")
AIRTABLE_BASE_ID = os.getenv("AIRTABLE_BASE_ID")
AIRTABLE_TABLE_NAME = os.getenv("AIRTABLE_TABLE_NAME")

# رابط API لـ Airtable
airtable_url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_NAME}"

# إعداد الرأس (headers) للمصادقة
headers = {
    "Authorization": f"Bearer {AIRTABLE_API_KEY}",
    "Content-Type": "application/json"
}

# إنشاء سجل جديد في Airtable مع الرابط في حقل Videos
data = {
    "records": [
        {
            "fields": {
                "Videos": direct_link
            }
        }
    ]
}

# إرسال الطلب إلى Airtable
response = requests.post(airtable_url, headers=headers, json=data)

# التحقق من نجاح الطلب
if response.status_code == 200:
    print("Direct link successfully sent to Airtable in the 'Videos' field!")
else:
    print(f"Failed to send link to Airtable. Status code: {response.status_code}, Response: {response.text}")

# حذف الملفات المحلية
if os.path.exists(final_video_file):
    os.remove(final_video_file)
    print(f"Local file deleted: {final_video_file}")

if os.path.exists(cookies_file):
    os.remove(cookies_file)
    print(f"Cookies file deleted: {cookies_file}")
