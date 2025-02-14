import yt_dlp
import os
import requests

# 🔹 إعدادات Airtable API
AIRTABLE_API_KEY = "patS1VYb5EHfiXXBV.71390a90cefd89f88d05485625c803ba5df091b89acf76a160685dca3f4d46aa"
AIRTABLE_BASE_ID = "app2j2xblYodCdMZQ"
AIRTABLE_TABLE_NAME = "Table2"

# 🔹 رابط Airtable API
AIRTABLE_URL = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_NAME}"

# 🔹 ترويسة الطلبات (Authorization)
HEADERS = {
    "Authorization": f"Bearer {AIRTABLE_API_KEY}",
    "Content-Type": "application/json"
}

# 📝 **1. جلب أحدث سجل يحتوي على رابط التغريدة**
def get_latest_tweet():
    response = requests.get(AIRTABLE_URL, headers=HEADERS)
    if response.status_code == 200:
        records = response.json().get("records", [])
        for record in records:
            if "tweet_url" in record["fields"]:  # التأكد من وجود التغريدة في السجل
                return record["id"], record["fields"]["tweet_url"]
    return None, None

# 🛠 **2. تحميل الفيديو من التغريدة**
def download_video(tweet_url):
    ydl_opts = {
        'quiet': True,
        'outtmpl': 'downloaded_video.mp4',  # حفظ الملف باسم محدد
        'format': 'best[ext=mp4]'  # اختيار أفضل جودة بصيغة MP4
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([tweet_url])  # تحميل الفيديو
        return "downloaded_video.mp4"  # إرجاع اسم الملف المحمّل
    except yt_dlp.utils.DownloadError as e:
        print(f"❌ خطأ في تحميل الفيديو: {str(e)}")
        return None

# 🔄 **3. رفع الفيديو إلى Airtable كمرفق**
def upload_video_to_airtable(record_id, video_path):
    with open(video_path, 'rb') as file:
        response = requests.post(
            "https://api.airtable.com/v0/meta/files/upload",
            headers={"Authorization": f"Bearer {AIRTABLE_API_KEY}"}
        )
        
        if response.status_code == 200:
            upload_url = response.json()["url"]
            
            # رفع الملف إلى Airtable عبر URL الموقّع
            files = {'file': open(video_path, 'rb')}
            upload_response = requests.put(upload_url, files=files)
            
            if upload_response.status_code == 200:
                # تحديث السجل في Airtable بالمرفق
                update_url = f"{AIRTABLE_URL}/{record_id}"
                payload = {"fields": {"Video_File": [{"url": upload_url}]}}
                update_response = requests.patch(update_url, json=payload, headers=HEADERS)

                if update_response.status_code == 200:
                    print(f"✅ تم رفع الفيديو وتحديث Airtable بنجاح!")
                else:
                    print(f"❌ فشل تحديث Airtable! التفاصيل: {update_response.text}")
            else:
                print(f"❌ فشل رفع الملف إلى Airtable! التفاصيل: {upload_response.text}")
        else:
            print(f"❌ فشل الحصول على URL رفع Airtable! التفاصيل: {response.text}")

# 🚀 **تشغيل العملية**
record_id, tweet_url = get_latest_tweet()
if record_id and tweet_url:
    print(f"🔗 رابط التغريدة: {tweet_url}")
    video_file = download_video(tweet_url)
    if video_file:
        upload_video_to_airtable(record_id, video_file)
else:
    print("❌ لم يتم العثور على سجل يحتوي على رابط تغريدة في Airtable!")
