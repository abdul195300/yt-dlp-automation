import os
import requests
import yt_dlp
import logging
import re
from tenacity import retry, stop_after_attempt, wait_fixed
import json

# ✨ تعريف متغيرات Airtable
AIRTABLE_BASE_ID = "app2j2xblYodCdMZQ"  # استبدل بمعرف الـ Base من Airtable
AIRTABLE_TABLE_NAME = "Table2"  # اسم الجدول في Airtable
API_KEY = "patS1VYb5EHfiXXBV.71390a90cefd89f88d05485625c803ba5df091b89acf76a160685dca3f4d46aa"  # استبدل بمفتاح API الخاص بـ Airtable
AIRTABLE_URL = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_NAME}"
DROPBOX_ACCESS_TOKEN = "sl.u.AFiZSncnGgFKMVoCCzIPPCLQG8P27yrp4hlP_4e5fAbR3Q0jsX0xmEd8iBYbq9-ijIIRWKDSBSJl8K8izE2qiuH_-8217aycdf5bN5iXC9DBPmIPYUDVjy_fOf8njK7oZJ1GOhDZu7_EOIQ32DgAfFPZ_z-dDJJQQ_TqKlYR8xv29Fqbh5AxxbDvP2ioi7YPGWjBOLLHdn3sDAGQOXOzPFu685ZPn_5h_vw4hpcSuEMSFy2JdOhLs6XA9xrq1JTjwJLwpmfXiE3L-a-rcXwVsj6817bZC8DQStcOJx_86jN67agVQo7loebGqWmHqrEkKX-828RPYFrt1DTNN6JnjII0lvQOUXuMvYLQyC0X1QbKk0U_ylf6wsjsmOAwZWOn_hyeADXvZpk9iVRfkkTPjy02PvTTqFf_iioZWN-TKQTD1Pj4q7ZVBDATIk11ooQ_tjb_8kubrjoEIWYTcOqJd5I7KhMr-ht55N9A5f3C35czYXeRUtD7EFhDH6owavBYIlEnGS_PQIdixv4cMTz06qoV11Dop2xlV52FJFJxfZB2k-osW0Ag-tXLOQZCV1422QV5SHJGFBs1_qGZC5-YJvb5PxDYI5AFtMLgV8qyLS8WMvnLpGrzp868E88V2j6kubTegW-MewC2_XxlvA6y9cCUjPsUkkaHi0TxpuXMTMiwsX3B24fZ_NV9o3kAv5CX8iEq4OmM_CcMnM3ycVEdXRO_8XHSplFUVBr2smHpqlw2LZ5JyWsuXsfgynp0LDUbb1xB1LFRV82nyVIEYqBE0pPCiZlkT0f6GRFUiTfSaopnpbrM_KmjlUJlce9ZwcjvcdmziAyYQDkGTN4JtXONfJI3P7CmoWYqJoItQCR5PSe480Se--dayPt0wEIr1hHwdd-Ai7IeMMCb-p9nD3eKcKDGith7CtcUxfjmc_ae6vmQxmQM_2zmcvgzY20lzogWWPuzPQ7GnjwhXTDEcbz3OBqCCFrEPns1Ul3VCrk9CIrLrGYVjtJ6th2oyHHEZ66e5Aq6x26d54PpJaYE3LZK_vhWo4e1jBOCg3nA9TQJqGomqA37zh9NhKPjVFHk-7yXkdRy3l_0QOsX918SutYTWlLJShfi7YhI4hZUkVco0HsdVEjESD3nJmej7s0Yb3oqd-dOyERXIJI_jOAcfcBACHfa77OZcKskkVRUy-RHPjnbDLxuRRLgSLxXWWmgHDodNdsP2PiFL2FSmWxzZtuT7_AZ6fMjMIPb5ZFed81BjNm5pE2KKTOxikVfAKNUlKR5S7c")  # مفتاح Dropbox

# إعداد الهيدر لاستخدام API Key
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# 📌 استخراج أحدث تغريدة من Airtable
def get_latest_tweet():
    response = requests.get(AIRTABLE_URL, headers=HEADERS)
    if response.status_code == 200:
        records = response.json().get("records", [])
        if records:
            latest_record = records[0]  # الحصول على أول سجل
            record_id = latest_record["id"]
            tweet_url = latest_record["fields"].get("tweet_url", "")
            return record_id, tweet_url
    return None, None

# 🎥 تحميل الفيديو من تويتر
def download_twitter_video(tweet_url):
    ydl_opts = {
        "outtmpl": "twitter_video.%(ext)s",  # حفظ الملف باسم
        "format": "best"
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([tweet_url])
    return "twitter_video.mp4"  # تأكد من أن الامتداد صحيح

# 🔄 تحديث Airtable برابط الفيديو بعد التحميل
def update_airtable(record_id, video_file):
    video_url = f"https://your-storage.com/{video_file}"  # ضع رابط التخزين السحابي هنا
    data = {"fields": {"Video_File": video_url}}
    response = requests.patch(f"{AIRTABLE_URL}/{record_id}", headers=HEADERS, json=data)
    return response.status_code == 200

# 🏁 تشغيل المهام
if __name__ == "__main__":
    record_id, tweet_url = get_latest_tweet()
    if record_id and tweet_url:
        print(f"📥 تحميل الفيديو من: {tweet_url}")
        video_file = download_twitter_video(tweet_url)
        if video_file:
            print(f"✅ تم تحميل الفيديو: {video_file}")
            if update_airtable(record_id, video_file):
                print("✅ تم تحديث Airtable بنجاح!")
            else:
                print("❌ فشل تحديث Airtable!")
        else:
            print("❌ فشل تحميل الفيديو!")
    else:
        print("❌ لم يتم العثور على رابط تغريدة في Airtable!")
