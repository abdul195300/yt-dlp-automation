import os
import praw
import yt_dlp
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request
import requests
import json
import tempfile
import base64

# أخذ رابط Reddit من المتغير البيئي
post_url = os.getenv("REDDIT_URL")
if not post_url:
    raise ValueError("يجب توفير رابط Reddit من المتغير البيئي REDDIT_URL")

# إعدادات Reddit API
reddit = praw.Reddit(
    client_id="UNKKLYTMC_CnFz-HByuvSQ",
    client_secret="UqKoUtUNV7jrVDhg8FQIdaVl2YTmfg",
    user_agent='u/Kitchen_Vehicle_8043',
)

submission = reddit.submission(url=post_url)

# تأكيد وجود فيديو
video_url = None
if "media" in submission.__dict__ and submission.media and "reddit_video" in submission.media:
    video_url = submission.media["reddit_video"]["fallback_url"]
elif submission.url.endswith(('.mp4', '.m3u8')) or "v.redd.it" in submission.url:
    video_url = submission.url

if not video_url:
    raise ValueError("لم يتم العثور على فيديو في المنشور!")

# استخدام مجلد مؤقت للفيديو فقط
with tempfile.TemporaryDirectory() as tmp_dir:
    final_video_file = os.path.join(tmp_dir, "reddit_video_with_audio.mp4")

    # فك الكوكيز من Secret إلى الملف في نفس مجلد السكربت
    cookies_base64 = os.getenv("REDDIT_COOKIES_BASE64")
    cookies_path = None
    if cookies_base64:
        cookies_path = "cookies.txt"
        with open(cookies_path, "wb") as f:
            f.write(base64.b64decode(cookies_base64))

    # إعداد yt-dlp
    ydl_opts = {
        'outtmpl': final_video_file,
        'format': 'bestvideo+bestaudio/best',
        'merge_output_format': 'mp4',
    }

    if cookies_path and os.path.exists(cookies_path):
        ydl_opts['cookiefile'] = cookies_path

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([post_url])
        print("✅ تم تحميل الفيديو باستخدام yt-dlp")
    except Exception as e:
        raise Exception("❌ فشل تحميل الفيديو:", e)

    # فك token.json من Secret
    token_base64 = os.getenv("GDRIVE_TOKEN_BASE64")
    if not token_base64:
        raise ValueError("⚠️ لم يتم العثور على Google Drive token")

    with open("token.json", "wb") as f:
        f.write(base64.b64decode(token_base64))

    # إعداد Google Drive API
    SCOPES = ['https://www.googleapis.com/auth/drive']
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())

    service = build('drive', 'v3', credentials=creds)

    # رفع الفيديو
    file_metadata = {'name': 'reddit_video_with_audio.mp4'}
    media = MediaFileUpload(final_video_file, mimetype='video/mp4')
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    file_id = file.get('id')
    print(f"✅ تم رفع الفيديو إلى Google Drive. ID: {file_id}")

    # جعل الملف عامًا
    service.permissions().create(
        fileId=file_id,
        body={'role': 'reader', 'type': 'anyone'}
    ).execute()

    # إنشاء رابط مباشر
    direct_link = f"https://drive.google.com/uc?export=download&id={file_id}"
    print(f"🔗 الرابط المباشر للفيديو: {direct_link}")

    # إعداد Airtable
    airtable_api_key = os.getenv("AIRTABLE_API_KEY")
    airtable_base_id = os.getenv("AIRTABLE_BASE_ID")
    airtable_table_name = os.getenv("AIRTABLE_TABLE_NAME")

    if not all([airtable_api_key, airtable_base_id, airtable_table_name]):
        raise ValueError("⚠️ تأكد من ضبط متغيرات Airtable")

    airtable_url = f"https://api.airtable.com/v0/{airtable_base_id}/{airtable_table_name}"
    headers = {
        "Authorization": f"Bearer {airtable_api_key}",
        "Content-Type": "application/json"
    }

    data = {
        "fields": {
            "Videos": direct_link
        }
    }

    response = requests.post(airtable_url, headers=headers, data=json.dumps(data))
    if response.status_code in [200, 201]:
        print("✅ تم إرسال الرابط إلى Airtable بنجاح")
    else:
        print("❌ فشل في إرسال الرابط إلى Airtable:", response.text)

# حذف ملف الكوكيز بعد الانتهاء
if cookies_path and os.path.exists(cookies_path):
    os.remove(cookies_path)
    print("🧹 تم حذف ملف الكوكيز المؤقت.")
