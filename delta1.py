import praw
import yt_dlp
import os
import base64
import json
import logging
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request
import requests

# إعداد التسجيل (Logging)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# إعدادات Reddit API باستخدام OAuth Refresh Token
reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    refresh_token=os.getenv("REDDIT_REFRESH_TOKEN"),
    user_agent=os.getenv("REDDIT_USER_AGENT"),
)

# رابط المنشور من متغير بيئي
post_url = os.getenv("REDDIT_POST_URL")
if not post_url:
    logger.error("REDDIT_POST_URL is not set!")
    raise ValueError("REDDIT_POST_URL is not set!")

logger.info(f"Processing Reddit post: {post_url}")

# استخراج المنشور
try:
    submission = reddit.submission(url=post_url)
except Exception as e:
    logger.error(f"Failed to fetch Reddit post: {e}")
    raise

# التحقق من وجود فيديو في المنشور
video_url = None
if hasattr(submission, 'media') and submission.media and 'reddit_video' in submission.media:
    video_url = submission.media['reddit_video']['fallback_url']
elif submission.url.endswith(('.mp4', '.m3u8')) or 'v.redd.it' in submission.url:
    video_url = submission.url

if not video_url:
    logger.error("No video found in the post!")
    raise ValueError("No video found in the post!")

logger.info(f"Video URL found: {video_url}")

# تحميل الفيديو مع الصوت باستخدام yt-dlp (بدون كوكيز)
final_video_file = "reddit_video_with_audio.mp4"
ydl_opts = {
    'outtmpl': final_video_file,
    'format': 'bestvideo+bestaudio/best',
    'merge_output_format': 'mp4',
    'quiet': False,
    'verbose': True,
}

try:
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([post_url])
    logger.info("Video downloaded successfully")
except Exception as e:
    logger.error(f"Failed to download video with yt-dlp: {e}")
    raise

# إعداد Google Drive API
SCOPES = ['https://www.googleapis.com/auth/drive']
creds_json_base64 = os.getenv("GDRIVE_TOKEN_BASE64")
if not creds_json_base64:
    logger.error("GDRIVE_TOKEN_BASE64 is not set!")
    raise ValueError("GDRIVE_TOKEN_BASE64 is not set!")

try:
    creds_json = base64.b64decode(creds_json_base64).decode('utf-8')
    creds_dict = json.loads(creds_json)
    creds = Credentials.from_authorized_user_info(creds_dict, SCOPES)
except Exception as e:
    logger.error(f"Failed to decode GDRIVE_TOKEN_BASE64: {e}")
    raise

if creds and creds.expired and creds.refresh_token:
    try:
        creds.refresh(Request())
    except Exception as e:
        logger.error(f"Failed to refresh Google Drive credentials: {e}")
        raise

try:
    service = build('drive', 'v3', credentials=creds)
except Exception as e:
    logger.error(f"Failed to build Google Drive service: {e}")
    raise

# رفع الفيديو إلى Google Drive
file_metadata = {'name': 'reddit_video_with_audio.mp4'}
media = MediaFileUpload(final_video_file, mimetype='video/mp4')
try:
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    file_id = file.get('id')
    logger.info(f"Video uploaded to Google Drive! File ID: {file_id}")
except Exception as e:
    logger.error(f"Failed to upload video to Google Drive: {e}")
    raise

# جعل الملف عامًا
try:
    service.permissions().create(
        fileId=file_id,
        body={'role': 'reader', 'type': 'anyone'}
    ).execute()
    logger.info("File permissions set to public")
except Exception as e:
    logger.error(f"Failed to set file permissions: {e}")
    raise

# إنشاء الرابط المباشر
direct_link = f"https://drive.google.com/uc?export=download&id={file_id}"
logger.info(f"Direct link: {direct_link}")

# إعداد Airtable API
AIRTABLE_API_KEY = os.getenv("AIRTABLE_API_KEY")
AIRTABLE_BASE_ID = os.getenv("AIRTABLE_BASE_ID")
AIRTABLE_TABLE_NAME = os.getenv("AIRTABLE_TABLE_NAME")

if not all([AIRTABLE_API_KEY, AIRTABLE_BASE_ID, AIRTABLE_TABLE_NAME]):
    logger.error("Airtable environment variables are not set!")
    raise ValueError("Airtable environment variables are not set!")

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
try:
    response = requests.post(airtable_url, headers=headers, json=data)
    if response.status_code == 200 or response.status_code == 201:
        logger.info("Direct link successfully sent to Airtable in the 'Videos' field!")
    else:
        logger.error(f"Failed to send link to Airtable. Status code: {response.status_code}, Response: {response.text}")
        raise Exception("Failed to send link to Airtable")
except Exception as e:
    logger.error(f"Failed to send request to Airtable: {e}")
    raise

# حذف الملفات المحلية
try:
    if os.path.exists(final_video_file):
        os.remove(final_video_file)
        logger.info(f"Local file deleted: {final_video_file}")
except Exception as e:
    logger.warning(f"Failed to delete local file: {e}")
