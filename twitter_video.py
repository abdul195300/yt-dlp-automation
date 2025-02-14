import requests
import os
import yt_dlp

# 🔹 إعدادات Airtable API
AIRTABLE_API_KEY = "patS1VYb5EHfiXXBV.71390a90cefd89f88d05485625c803ba5df091b89acf76a160685dca3f4d46aa"  # ضع مفتاح Airtable API هنا
AIRTABLE_BASE_ID = "app2j2xblYodCdMZQ"  # ضع معرف قاعدة البيانات (Base ID)
AIRTABLE_TABLE_NAME = "Table2"  # ضع اسم الجدول

# 🔹 رابط Airtable API لجلب البيانات
AIRTABLE_URL = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_NAME}"

# 🔹 ترويسة الطلبات (Authorization)
HEADERS = {
    "Authorization": f"Bearer {AIRTABLE_API_KEY}",
    "Content-Type": "application/json"
}

# 📝 **1. جلب رابط التغريدة من Airtable**
def get_latest_tweet():
    response = requests.get(AIRTABLE_URL, headers=HEADERS)
    if response.status_code == 200:
        records = response.json().get("records", [])
        if records:
            return records[0]["id"], records[0]["fields"].get("Tweet_URL")
    return None, None

# 🛠 **2. استخراج رابط الفيديو من التغريدة**
def extract_video_url(tweet_url):
    ydl_opts = {
        'quiet': True,
        'simulate': True,  # استخراج المعلومات بدون تحميل
        'format': 'best',
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(tweet_url, download=False)
            if 'entries' in info:
                video_info = info['entries'][0]  # أول فيديو في القائمة
            else:
                video_info = info
            return video_info.get("url")
    except yt_dlp.utils.DownloadError:
        return None

# 🔄 **3. تحديث Airtable برابط الفيديو**
def update_airtable(record_id, video_url):
    update_url = f"{AIRTABLE_URL}/{record_id}"
    payload = {"fields": {"Video_URL": video_url if video_url else "❌ الرابط لا يحتوي على فيديو."}}
    response = requests.patch(update_url, json=payload, headers=HEADERS)
    return response.status_code == 200

# 🚀 **تشغيل الوظيفة**
record_id, tweet_url = get_latest_tweet()
if tweet_url:
    video_url = extract_video_url(tweet_url)
    if update_airtable(record_id, video_url):
        print(f"✅ تم تحديث Airtable برابط الفيديو: {video_url}")
    else:
        print("❌ فشل تحديث Airtable!")
else:
    print("❌ لم يتم العثور على تغريدة جديدة!")
