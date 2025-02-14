import yt_dlp
import os
import requests

# 🔹 إعدادات Airtable API
AIRTABLE_API_KEY = "patS1VYb5EHfiXXBV.71390a90cefd89f88d05485625c803ba5df091b89acf76a160685dca3f4d46aa"  # استبدل بـ API Key
AIRTABLE_BASE_ID = "app2j2xblYodCdMZQ"  # استبدل بـ Base ID
AIRTABLE_TABLE_NAME = "Table2"  # استبدل بـ اسم الجدول

# 🔹 رابط Airtable API لجلب البيانات
AIRTABLE_URL = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_NAME}"
HEADERS = {
    "Authorization": f"Bearer {AIRTABLE_API_KEY}",
    "Content-Type": "application/json"
}

# 📝 **1. جلب رابط الفيديو من Airtable**
def extract_video_url(url):
    """ استخراج رابط الفيديو المباشر من أي موقع مدعوم بواسطة yt-dlp """
    ydl_opts = {
        'quiet': True,
        'simulate': True,  # استخراج المعلومات بدون تحميل
        'format': 'best',
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if 'entries' in info:  
                video_info = info['entries'][0]  # أول فيديو في القائمة
            else:
                video_info = info

            if 'url' in video_info:
                return video_info['url']
            else:
                return None
    except Exception as e:
        print(f"⚠️ خطأ أثناء استخراج الفيديو: {str(e)}")
        return None
        
# 🔄 **3. تحديث Airtable برابط الفيديو**
def update_airtable(record_id, video_url):
    update_url = f"{AIRTABLE_URL}/{record_id}"
    payload = {"fields": {"Video_URL": video_url if video_url else "❌ لا يوجد فيديو"}}
    response = requests.patch(update_url, json=payload, headers=HEADERS)
    return response.status_code == 200

# 🚀 **تشغيل العملية**
record_id, video_source_url = get_latest_video_link()
if video_source_url:
    video_url = extract_video_url(video_source_url)
    if update_airtable(record_id, video_url):
        print(f"✅ تم تحديث Airtable برابط الفيديو: {video_url}")
    else:
        print("❌ فشل تحديث Airtable!")
else:
    print("❌ لم يتم العثور على فيديو جديد!")
