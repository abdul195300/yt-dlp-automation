import os
import requests
import yt_dlp
import logging
import re
from tenacity import retry, stop_after_attempt, wait_fixed
import json

# 🔐 بيانات الوصول
AIRTABLE_URL = "https://api.airtable.com/v0/YOUR_BASE_ID/YOUR_TABLE_NAME"
AIRTABLE_API_KEY = "patS1VYb5EHfiXXBV.71390a90cefd89f88d05485625c803ba5df091b89acf76a160685dca3f4d46aa"
DROPBOX_ACCESS_TOKEN = "sl.u.AFiZSncnGgFKMVoCCzIPPCLQG8P27yrp4hlP_4e5fAbR3Q0jsX0xmEd8iBYbq9-ijIIRWKDSBSJl8K8izE2qiuH_-8217aycdf5bN5iXC9DBPmIPYUDVjy_fOf8njK7oZJ1GOhDZu7_EOIQ32DgAfFPZ_z-dDJJQQ_TqKlYR8xv29Fqbh5AxxbDvP2ioi7YPGWjBOLLHdn3sDAGQOXOzPFu685ZPn_5h_vw4hpcSuEMSFy2JdOhLs6XA9xrq1JTjwJLwpmfXiE3L-a-rcXwVsj6817bZC8DQStcOJx_86jN67agVQo7loebGqWmHqrEkKX-828RPYFrt1DTNN6JnjII0lvQOUXuMvYLQyC0X1QbKk0U_ylf6wsjsmOAwZWOn_hyeADXvZpk9iVRfkkTPjy02PvTTqFf_iioZWN-TKQTD1Pj4q7ZVBDATIk11ooQ_tjb_8kubrjoEIWYTcOqJd5I7KhMr-ht55N9A5f3C35czYXeRUtD7EFhDH6owavBYIlEnGS_PQIdixv4cMTz06qoV11Dop2xlV52FJFJxfZB2k-osW0Ag-tXLOQZCV1422QV5SHJGFBs1_qGZC5-YJvb5PxDYI5AFtMLgV8qyLS8WMvnLpGrzp868E88V2j6kubTegW-MewC2_XxlvA6y9cCUjPsUkkaHi0TxpuXMTMiwsX3B24fZ_NV9o3kAv5CX8iEq4OmM_CcMnM3ycVEdXRO_8XHSplFUVBr2smHpqlw2LZ5JyWsuXsfgynp0LDUbb1xB1LFRV82nyVIEYqBE0pPCiZlkT0f6GRFUiTfSaopnpbrM_KmjlUJlce9ZwcjvcdmziAyYQDkGTN4JtXONfJI3P7CmoWYqJoItQCR5PSe480Se--dayPt0wEIr1hHwdd-Ai7IeMMCb-p9nD3eKcKDGith7CtcUxfjmc_ae6vmQxmQM_2zmcvgzY20lzogWWPuzPQ7GnjwhXTDEcbz3OBqCCFrEPns1Ul3VCrk9CIrLrGYVjtJ6th2oyHHEZ66e5Aq6x26d54PpJaYE3LZK_vhWo4e1jBOCg3nA9TQJqGomqA37zh9NhKPjVFHk-7yXkdRy3l_0QOsX918SutYTWlLJShfi7YhI4hZUkVco0HsdVEjESD3nJmej7s0Yb3oqd-dOyERXIJI_jOAcfcBACHfa77OZcKskkVRUy-RHPjnbDLxuRRLgSLxXWWmgHDodNdsP2PiFL2FSmWxzZtuT7_AZ6fMjMIPb5ZFed81BjNm5pE2KKTOxikVfAKNUlKR5S7c"  # مفتاح Dropbox
AIRTABLE_BASE_ID = "app2j2xblYodCdMZQ"  # استبدل بمعرف الـ Base من Airtable
AIRTABLE_TABLE_NAME = "Table2"  # اسم الجدول في Airtable

HEADERS = {
    "Authorization": f"Bearer {AIRTABLE_API_KEY}",
    "Content-Type": "application/json"
}

# 📥 تحميل الفيديو من تويتر
TWEET_URL = "https://x.com/mfu46/status/1890264190021243175"
video_filename = "twitter_video.mp4"

# تأكد أن الملف موجود
if not os.path.exists(video_filename):
    print(f"❌ الملف {video_filename} غير موجود. تأكد من تحميل الفيديو أولاً!")
    exit(1)

# ✅ **رفع الملف إلى Dropbox**
def upload_to_dropbox(local_file):
    dropbox_path = f"/{local_file}"
    with open(local_file, "rb") as f:
        response = requests.post(
            "https://content.dropboxapi.com/2/files/upload",
            headers={
                "Authorization": f"Bearer {DROPBOX_ACCESS_TOKEN}",
                "Dropbox-API-Arg": json.dumps({
                    "path": dropbox_path,
                    "mode": "add",
                    "autorename": True,
                    "mute": False
                }),
                "Content-Type": "application/octet-stream"
            },
            data=f.read()
        )

    if response.status_code == 200:
        shared_link = requests.post(
            "https://api.dropboxapi.com/2/sharing/create_shared_link_with_settings",
            headers={
                "Authorization": f"Bearer {DROPBOX_ACCESS_TOKEN}",
                "Content-Type": "application/json"
            },
            data=json.dumps({"path": dropbox_path})
        )

        if shared_link.status_code == 200:
            url = shared_link.json()["url"].replace("?dl=0", "?dl=1")  # تحويله إلى رابط مباشر
            print(f"✅ تم رفع الملف على Dropbox: {url}")
            return url
        else:
            print(f"❌ خطأ في مشاركة رابط Dropbox: {shared_link.text}")
            return None
    else:
        print(f"❌ خطأ في رفع الملف إلى Dropbox: {response.text}")
        return None

# 🖥️ **تحميل الفيديو إلى Dropbox والحصول على رابط مباشر**
video_url = upload_to_dropbox(video_filename)

if not video_url:
    print("❌ فشل في رفع الفيديو. تأكد من صحة توكن Dropbox.")
    exit(1)

# 📤 **إرسال البيانات إلى Airtable**
data = {
    "records": [
        {
            "fields": {
                "tweet_url": TWEET_URL,
                "Video_File": [{"url": video_url}]
            }
        }
    ]
}

print("📜 البيانات المرسلة إلى Airtable:")
print(json.dumps(data, indent=4))

response = requests.post(AIRTABLE_URL, json=data, headers=HEADERS)

if response.status_code in [200, 201]:
    print("✅ تم تحديث Airtable بنجاح!")
else:
    print(f"❌ فشل تحديث Airtable: {response.text}")
