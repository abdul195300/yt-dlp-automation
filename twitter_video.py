import os
import requests
import subprocess

# 🛠 إعداد متغيرات API
AIRTABLE_API_KEY = "patS1VYb5EHfiXXBV.71390a90cefd89f88d05485625c803ba5df091b89acf76a160685dca3f4d46aa"
AIRTABLE_BASE_ID = "app2j2xblYodCdMZQ"
AIRTABLE_TABLE_NAME = "Table2"  # تأكد من أن اسم الجدول صحيح
DROPBOX_ACCESS_TOKEN = "sl.u.AFiZSncnGgFKMVoCCzIPPCLQG8P27yrp4hlP_4e5fAbR3Q0jsX0xmEd8iBYbq9-ijIIRWKDSBSJl8K8izE2qiuH_-8217aycdf5bN5iXC9DBPmIPYUDVjy_fOf8njK7oZJ1GOhDZu7_EOIQ32DgAfFPZ_z-dDJJQQ_TqKlYR8xv29Fqbh5AxxbDvP2ioi7YPGWjBOLLHdn3sDAGQOXOzPFu685ZPn_5h_vw4hpcSuEMSFy2JdOhLs6XA9xrq1JTjwJLwpmfXiE3L-a-rcXwVsj6817bZC8DQStcOJx_86jN67agVQo7loebGqWmHqrEkKX-828RPYFrt1DTNN6JnjII0lvQOUXuMvYLQyC0X1QbKk0U_ylf6wsjsmOAwZWOn_hyeADXvZpk9iVRfkkTPjy02PvTTqFf_iioZWN-TKQTD1Pj4q7ZVBDATIk11ooQ_tjb_8kubrjoEIWYTcOqJd5I7KhMr-ht55N9A5f3C35czYXeRUtD7EFhDH6owavBYIlEnGS_PQIdixv4cMTz06qoV11Dop2xlV52FJFJxfZB2k-osW0Ag-tXLOQZCV1422QV5SHJGFBs1_qGZC5-YJvb5PxDYI5AFtMLgV8qyLS8WMvnLpGrzp868E88V2j6kubTegW-MewC2_XxlvA6y9cCUjPsUkkaHi0TxpuXMTMiwsX3B24fZ_NV9o3kAv5CX8iEq4OmM_CcMnM3ycVEdXRO_8XHSplFUVBr2smHpqlw2LZ5JyWsuXsfgynp0LDUbb1xB1LFRV82nyVIEYqBE0pPCiZlkT0f6GRFUiTfSaopnpbrM_KmjlUJlce9ZwcjvcdmziAyYQDkGTN4JtXONfJI3P7CmoWYqJoItQCR5PSe480Se--dayPt0wEIr1hHwdd-Ai7IeMMCb-p9nD3eKcKDGith7CtcUxfjmc_ae6vmQxmQM_2zmcvgzY20lzogWWPuzPQ7GnjwhXTDEcbz3OBqCCFrEPns1Ul3VCrk9CIrLrGYVjtJ6th2oyHHEZ66e5Aq6x26d54PpJaYE3LZK_vhWo4e1jBOCg3nA9TQJqGomqA37zh9NhKPjVFHk-7yXkdRy3l_0QOsX918SutYTWlLJShfi7YhI4hZUkVco0HsdVEjESD3nJmej7s0Yb3oqd-dOyERXIJI_jOAcfcBACHfa77OZcKskkVRUy-RHPjnbDLxuRRLgSLxXWWmgHDodNdsP2PiFL2FSmWxzZtuT7_AZ6fMjMIPb5ZFed81BjNm5pE2KKTOxikVfAKNUlKR5S7c"  # مفتاح Dropbox

# 🔍 استرجاع آخر تغريدة من Airtable
AIRTABLE_URL = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_NAME}"
HEADERS = {"Authorization": f"Bearer {AIRTABLE_API_KEY}"}

response = requests.get(AIRTABLE_URL, headers=HEADERS)
data = response.json()

# 📌 استخراج الرابط من Airtable
if "records" in data and data["records"]:
    latest_record = data["records"][0]  # أول سجل في القائمة
    record_id = latest_record["id"]
    tweet_url = latest_record["fields"].get("tweet_url", "")
else:
    print("❌ لم يتم العثور على بيانات في Airtable!")
    exit(1)

if not tweet_url:
    print("❌ لم يتم العثور على رابط تغريدة في Airtable!")
    exit(1)

print(f"🔗 تم العثور على رابط التغريدة: {tweet_url}")

# 📥 تحميل الفيديو من تويتر باستخدام yt-dlp
video_filename = "twitter_video.mp4"
try:
    subprocess.run(
        ["yt-dlp", "-f", "best", "-o", video_filename, tweet_url], check=True
    )
except subprocess.CalledProcessError:
    print("❌ فشل تحميل الفيديو من تويتر!")
    exit(1)

print("✅ تم تحميل الفيديو بنجاح!")

# 📤 رفع الفيديو إلى Dropbox
DROPBOX_UPLOAD_PATH = f"/{video_filename}"
DROPBOX_UPLOAD_URL = "https://content.dropboxapi.com/2/files/upload"

with open(video_filename, "rb") as f:
    headers = {
        "Authorization": f"Bearer {DROPBOX_ACCESS_TOKEN}",
        "Dropbox-API-Arg": f'{{"path": "{DROPBOX_UPLOAD_PATH}", "mode": "add", "autorename": true, "mute": false}}',
        "Content-Type": "application/octet-stream",
    }
    upload_response = requests.post(DROPBOX_UPLOAD_URL, headers=headers, data=f)

if upload_response.status_code == 200:
    print("✅ تم رفع الفيديو إلى Dropbox!")
else:
    print("❌ فشل رفع الفيديو إلى Dropbox!", upload_response.text)
    exit(1)

# 🔗 استخراج رابط المشاركة من Dropbox
DROPBOX_SHARED_LINK_URL = "https://api.dropboxapi.com/2/sharing/create_shared_link_with_settings"
link_data = {"path": DROPBOX_UPLOAD_PATH, "settings": {"requested_visibility": "public"}}
headers = {"Authorization": f"Bearer {DROPBOX_ACCESS_TOKEN}", "Content-Type": "application/json"}

link_response = requests.post(DROPBOX_SHARED_LINK_URL, headers=headers, json=link_data)

if link_response.status_code == 200:
    dropbox_link = link_response.json()["url"].replace("?dl=0", "?raw=1")
    print(f"✅ رابط الفيديو على Dropbox: {dropbox_link}")
else:
    print("❌ فشل إنشاء رابط مشاركة من Dropbox!", link_response.text)
    exit(1)

# 📌 تحديث Airtable بحقل `Video_File`
update_url = f"{AIRTABLE_URL}/{record_id}"
update_data = {"fields": {"Video_File": dropbox_link}}
update_response = requests.patch(update_url, headers=HEADERS, json=update_data)

if update_response.status_code == 200:
    print("✅ تم تحديث Airtable برابط الفيديو!")
else:
    print("❌ فشل تحديث Airtable!", update_response.text)
