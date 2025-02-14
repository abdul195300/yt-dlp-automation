import os
import requests
import yt_dlp
import logging
import re
from tenacity import retry, stop_after_attempt, wait_fixed

# 🔹 إعدادات من متغيرات البيئة
AIRTABLE_API_KEY = os.getenv("patS1VYb5EHfiXXBV.71390a90cefd89f88d05485625c803ba5df091b89acf76a160685dca3f4d46aa")  # تأكد من أن مفتاح API صحيح
DROPBOX_ACCESS_TOKEN = os.getenv("sl.u.AFiZSncnGgFKMVoCCzIPPCLQG8P27yrp4hlP_4e5fAbR3Q0jsX0xmEd8iBYbq9-ijIIRWKDSBSJl8K8izE2qiuH_-8217aycdf5bN5iXC9DBPmIPYUDVjy_fOf8njK7oZJ1GOhDZu7_EOIQ32DgAfFPZ_z-dDJJQQ_TqKlYR8xv29Fqbh5AxxbDvP2ioi7YPGWjBOLLHdn3sDAGQOXOzPFu685ZPn_5h_vw4hpcSuEMSFy2JdOhLs6XA9xrq1JTjwJLwpmfXiE3L-a-rcXwVsj6817bZC8DQStcOJx_86jN67agVQo7loebGqWmHqrEkKX-828RPYFrt1DTNN6JnjII0lvQOUXuMvYLQyC0X1QbKk0U_ylf6wsjsmOAwZWOn_hyeADXvZpk9iVRfkkTPjy02PvTTqFf_iioZWN-TKQTD1Pj4q7ZVBDATIk11ooQ_tjb_8kubrjoEIWYTcOqJd5I7KhMr-ht55N9A5f3C35czYXeRUtD7EFhDH6owavBYIlEnGS_PQIdixv4cMTz06qoV11Dop2xlV52FJFJxfZB2k-osW0Ag-tXLOQZCV1422QV5SHJGFBs1_qGZC5-YJvb5PxDYI5AFtMLgV8qyLS8WMvnLpGrzp868E88V2j6kubTegW-MewC2_XxlvA6y9cCUjPsUkkaHi0TxpuXMTMiwsX3B24fZ_NV9o3kAv5CX8iEq4OmM_CcMnM3ycVEdXRO_8XHSplFUVBr2smHpqlw2LZ5JyWsuXsfgynp0LDUbb1xB1LFRV82nyVIEYqBE0pPCiZlkT0f6GRFUiTfSaopnpbrM_KmjlUJlce9ZwcjvcdmziAyYQDkGTN4JtXONfJI3P7CmoWYqJoItQCR5PSe480Se--dayPt0wEIr1hHwdd-Ai7IeMMCb-p9nD3eKcKDGith7CtcUxfjmc_ae6vmQxmQM_2zmcvgzY20lzogWWPuzPQ7GnjwhXTDEcbz3OBqCCFrEPns1Ul3VCrk9CIrLrGYVjtJ6th2oyHHEZ66e5Aq6x26d54PpJaYE3LZK_vhWo4e1jBOCg3nA9TQJqGomqA37zh9NhKPjVFHk-7yXkdRy3l_0QOsX918SutYTWlLJShfi7YhI4hZUkVco0HsdVEjESD3nJmej7s0Yb3oqd-dOyERXIJI_jOAcfcBACHfa77OZcKskkVRUy-RHPjnbDLxuRRLgSLxXWWmgHDodNdsP2PiFL2FSmWxzZtuT7_AZ6fMjMIPb5ZFed81BjNm5pE2KKTOxikVfAKNUlKR5S7c")  # مفتاح Dropbox
AIRTABLE_BASE_ID = os.getenv("app2j2xblYodCdMZQ")
AIRTABLE_TABLE_NAME = "Table2"  # اسم الجدول في Airtable
DOWNLOAD_PATH = "downloaded_video.mp4"  # اسم الملف الذي سيتم حفظ الفيديو فيه

# 🔹 إعدادات التسجيل
logging.basicConfig(level=logging.INFO)

# 📝 **1. جلب أحدث سجل يحتوي على رابط التغريدة**
def get_latest_tweet():
    airtable_url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_NAME}"
    headers = {"Authorization": f"Bearer {AIRTABLE_API_KEY}", "Content-Type": "application/json"}

    response = requests.get(airtable_url, headers=headers)
    if response.status_code == 200:
        records = response.json().get("records", [])
        for record in records:
            if "tweet_url" in record["fields"]:  # التأكد من وجود رابط التغريدة في السجل
                return record["id"], record["fields"]["tweet_url"]
    logging.error("❌ لم يتم العثور على سجل يحتوي على رابط تغريدة في Airtable!")
    return None, None

# 🛠 **2. تحميل الفيديو من التغريدة باستخدام `yt-dlp`**
def download_video(tweet_url):
    ydl_opts = {
        'quiet': False,
        'outtmpl': DOWNLOAD_PATH,  # حفظ الفيديو بنفس الاسم
        'format': 'best[ext=mp4]',  # أفضل جودة بصيغة MP4
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([tweet_url])
        logging.info(f"✅ تم تحميل الفيديو من تويتر: {DOWNLOAD_PATH}")
        return DOWNLOAD_PATH
    except yt_dlp.utils.DownloadError as e:
        logging.error(f"❌ خطأ في تحميل الفيديو: {str(e)}")
        return None

# 🔄 **3. رفع الفيديو إلى Dropbox**
@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def upload_to_dropbox():
    try:
        with open(DOWNLOAD_PATH, "rb") as f:
            headers = {
                "Authorization": f"Bearer {DROPBOX_ACCESS_TOKEN}",
                "Content-Type": "application/octet-stream",
                "Dropbox-API-Arg": f'{{"path": "/{DOWNLOAD_PATH}", "mode": "add", "autorename": True, "mute": False}}'
            }
            response = requests.post("https://content.dropboxapi.com/2/files/upload", headers=headers, data=f)
            response.raise_for_status()
        
        logging.info("✅ تم رفع الفيديو إلى Dropbox بنجاح!")
        return get_shared_link()
    
    except Exception as e:
        logging.error(f"❌ فشل الرفع إلى Dropbox: {e}")
        raise

# 🔹 **4. الحصول على رابط مشاركة مباشر من Dropbox وتحويله إلى رابط تحميل مباشر**
def get_shared_link():
    try:
        headers = {
            "Authorization": f"Bearer {DROPBOX_ACCESS_TOKEN}",
            "Content-Type": "application/json"
        }
        data = {"path": f"/{DOWNLOAD_PATH}"}
        response = requests.post("https://api.dropboxapi.com/2/sharing/create_shared_link_with_settings", json=data, headers=headers)

        if response.status_code == 200:
            shared_link = response.json()["url"]
            logging.info(f"📌 رابط المشاركة من Dropbox: {shared_link}")

            # ✅ تحويل رابط Dropbox إلى رابط تنزيل مباشر
            direct_download_link = shared_link.replace("www.dropbox.com", "dl.dropboxusercontent.com").replace("?dl=0", "")
            logging.info(f"📌 رابط التحميل المباشر للفيديو: {direct_download_link}")

            return direct_download_link
        else:
            logging.error(f"❌ فشل الحصول على رابط المشاركة! التفاصيل: {response.text}")
            return None
    except Exception as e:
        logging.error(f"❌ خطأ أثناء الحصول على رابط Dropbox: {e}")
        return None

# 🔄 **5. تحديث سجل Airtable بالفيديو كمرفق**
def update_airtable(record_id, video_url):
    if not video_url or not re.match(r'^https?://', video_url):
        logging.warning("❌ رابط الفيديو غير صالح")
        return

    update_url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_NAME}/{record_id}"
    
    payload = {
        "fields": {
            "Video_File": [{"url": video_url}]
        }
    }
    
    headers = {
        "Authorization": f"Bearer {AIRTABLE_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.patch(update_url, json=payload, headers=headers)
        if response.status_code == 200:
            logging.info("✅ تم تحديث السجل في Airtable بنجاح!")
        else:
            logging.error(f"❌ فشل تحديث Airtable! كود الخطأ: {response.status_code}, التفاصيل: {response.text}")
    except Exception as e:
        logging.error(f"❌ خطأ أثناء تحديث Airtable: {e}")

# 🚀 **6. تشغيل العملية بالكامل**
if __name__ == "__main__":
    record_id, tweet_url = get_latest_tweet()
    if record_id and tweet_url:
        logging.info(f"🔗 رابط التغريدة: {tweet_url}")
        video_file = download_video(tweet_url)
        if video_file:
            video_url = upload_to_dropbox()  # رفع الفيديو إلى Dropbox
            if video_url:
                update_airtable(record_id, video_url)  # تحديث Airtable بالمرفق
    else:
        logging.error("❌ لم يتم العثور على أي رابط تغريدة في Airtable!")
