import yt_dlp
import os
import requests

# 🔹 إعدادات Airtable API
AIRTABLE_API_KEY = "patS1VYb5EHfiXXBV.71390a90cefd89f88d05485625c803ba5df091b89acf76a160685dca3f4d46aa"  # استبدل بـ API Key
AIRTABLE_BASE_ID = "app2j2xblYodCdMZQ"  # استبدل بـ Base ID
AIRTABLE_TABLE_NAME = "Table2"  # استبدل بـ اسم الجدول

# 🔹 رابط Airtable API لجلب البيانات
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

# 🔄 **3. تحديث نفس السجل في Airtable برابط الفيديو**
def update_airtable(record_id, video_url):
    update_url = f"{AIRTABLE_URL}/{record_id}"  # تحديد السجل المراد تحديثه
    payload = {"fields": {"Video_URL": video_url if video_url else "❌ الرابط لا يحتوي على فيديو."}}
    response = requests.patch(update_url, json=payload, headers=HEADERS)
    
    if response.status_code == 200:
        print(f"✅ تم تحديث السجل برابط الفيديو: {video_url}")
    else:
        print(f"❌ فشل تحديث Airtable! كود الخطأ: {response.status_code}, التفاصيل: {response.text}")

# 🚀 **تشغيل العملية**
record_id, tweet_url = get_latest_tweet()
if record_id and tweet_url:
    print(f"🔗 رابط التغريدة: {tweet_url}")
    video_url = extract_video_url(tweet_url)
    if video_url:
        print(f"🎥 رابط الفيديو المباشر: {video_url}")
    update_airtable(record_id, video_url)
else:
    print("❌ لم يتم العثور على سجل يحتوي على رابط تغريدة في Airtable!")
