import yt_dlp
import os
import requests
import json

# 🔹 إعدادات Airtable
AIRTABLE_API_KEY = "patS1VYb5EHfiXXBV.71390a90cefd89f88d05485625c803ba5df091b89acf76a160685dca3f4d46aa"
AIRTABLE_BASE_ID = "app2j2xblYodCdMZQ"
AIRTABLE_TABLE_NAME = "Table2"
DOWNLOAD_PATH = "downloaded_video.mp4"

# 🔹 إعدادات Dropbox
DROPBOX_ACCESS_TOKEN = "sl.u.AFiXpeDi5f9XZdzVSBot7Xy-yEhGc1pkD6FEYrt4HNmGhEdq79igwDCq37f40JBWBHQBoRE0RdLP6GiKYB3B6nb8fbIo_bfvR7ixADOLXRURtuYJZaEO0pnqH7mxxn2VgjnotUS9cqGTEKxPLlWsfTWmDaceRzoiD2wUjV-B-Pjlpzh29PSYrqeRCHYqeuvP-pk3p3qoY5I2f8-NKeonUjPsUKBRmdxz2qhY7cySACX3dw1D7nCP_O-Ah5S7h7QXuVHBaU6UYbbzitcghmR0gYg9CUQYHTmElnDPJY3s-F1aOmIS_T-pU7CJLuDNdMlcY0zhFtzsTytdTXqRLgrZj1qD_ZqfM_ohvHniLgMetw3IOsoUfTaiWdyFujiPZVIVAzeJFbwLdqawUEWpJDUGde_UbkZ46-ncHRRaTvktB3lFukA86vCrdnuWvOnK2aXiZQ6weQO1RjIdkkylzu2XIY9x84EOR6qCo0oV0FkIzVw2B6-_U-jFcafccoxLz2S7ze2lNfSok95e51DEcnYxbz4bxYOMVnWhCF9nvsW0Ba0Njk_hUIkbfFa1vNIqOKpfxVWqmcjPkiiQ9kmcoNeJgT-Le_N1ts5-rSHRwjbKCTnU_j2hJTpobc2e06mvMmmD-_hFeLIiY8tim3snhn0xCRiMRVV89c0B8FabCJK9de1at8LrD4gu0fY1vw0FW_APxUCKXPhs_yb52RmwRTSt_egv5sK8mHEElDeWJFAuFnzvQn6Xhs0zFwQyxcabB0DAy6ysgV4X04-oYasfNCiF9SKbVQt2CFbhWLbY5SC_RpDAaMhDzFOP6V4Ll59-8ET_NB2EzEjwVSOydJGDZFHu7v9M0xHv5fFB32Dq36ctPDTx80ZGtVbLFcmILFcZEUDZBQfEYs-Wzl2Btx9idqcEwTQlnCq5ZHRzVElAOdnML3LILaunuMGrvWpHGXk3bB5NtE2ODCqCGvzJXPB9ZgszRroEbH9dnlT2cFsUxZczA0TPePmwJjb5cKhlwfF51Pvv7P9zHWfxrpvNQJrF1rigbyXORQNe9CaSlUewJbBlaTCZwoKr08vuWUGClSZYMpguRIHrFMwx3-2KVFZ-0sY6WDWK0dLelFT5eaeCxmZeccF5RTgeLx7Gjv8f1I1l192OWv2lxfmiBECl6YNHsY0dKjWvk8UNv-RaERaQkL6KQoanqXiaSslRaXQhczN50Zsp-R7D3UDU2-803bczv6NUV2JJkVxUHHZHdooHnGZdZ2xOU4sIAIXAdtc5VakESsAijG8"
DROPBOX_UPLOAD_PATH = f"/{DOWNLOAD_PATH}"  # اسم الملف بعد الرفع إلى Dropbox

# 🔹 رابط API الخاص بـ Airtable
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
        'outtmpl': DOWNLOAD_PATH,  # حفظ الفيديو بنفس الاسم
        'format': 'best[ext=mp4]',  # أفضل جودة بصيغة MP4
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([tweet_url])
        return DOWNLOAD_PATH
    except yt_dlp.utils.DownloadError as e:
        print(f"❌ خطأ في تحميل الفيديو: {str(e)}")
        return None

# 🔄 **3. رفع الفيديو إلى Dropbox والحصول على رابط مباشر**
def upload_to_dropbox():
    with open(DOWNLOAD_PATH, "rb") as f:
        headers = {
            "Authorization": f"Bearer {DROPBOX_ACCESS_TOKEN}",
            "Content-Type": "application/octet-stream",
            "Dropbox-API-Arg": json.dumps({
                "path": DROPBOX_UPLOAD_PATH,
                "mode": "add",
                "autorename": True,
                "mute": False
            })
        }
        response = requests.post("https://content.dropboxapi.com/2/files/upload", headers=headers, data=f)

    if response.status_code == 200:
        print("✅ تم رفع الفيديو إلى Dropbox!")
        return get_shared_link()
    else:
        print(f"❌ فشل رفع الفيديو! التفاصيل: {response.text}")
        return None

# 🔹 **4. الحصول على رابط مشاركة مباشر من Dropbox**
def get_shared_link():
    headers = {
        "Authorization": f"Bearer {DROPBOX_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    data = json.dumps({"path": DROPBOX_UPLOAD_PATH, "settings": {"requested_visibility": "public"}})
    response = requests.post("https://api.dropboxapi.com/2/sharing/create_shared_link_with_settings", headers=headers, data=data)

    if response.status_code == 200:
        link = response.json()["url"]
        direct_link = link.replace("?dl=0", "?raw=1")  # تحويل الرابط إلى رابط مباشر
        print(f"📌 رابط مباشر للفيديو: {direct_link}")
        return direct_link
    else:
        print(f"❌ فشل الحصول على رابط المشاركة! التفاصيل: {response.text}")
        return None

# 🔄 **5. تحديث سجل Airtable بالفيديو كمرفق**
def update_airtable(record_id, video_url):
    update_url = f"{AIRTABLE_URL}/{record_id}"
    payload = {"fields": {"Video_File": [{"url": video_url}]}}  # إضافة الفيديو كمرفق

    response = requests.patch(update_url, json=payload, headers=HEADERS)
    if response.status_code == 200:
        print("✅ تم تحديث السجل برابط الفيديو المرفق!")
    else:
        print(f"❌ فشل تحديث Airtable! كود الخطأ: {response.status_code}, التفاصيل: {response.text}")

# 🚀 **6. تشغيل العملية بالكامل**
record_id, tweet_url = get_latest_tweet()
if record_id and tweet_url:
    print(f"🔗 رابط التغريدة: {tweet_url}")
    video_file = download_video(tweet_url)
    if video_file:
        video_url = upload_to_dropbox()  # رفع الفيديو إلى Dropbox
        if video_url:
            update_airtable(record_id, video_url)  # تحديث Airtable بالمرفق
else:
    print("❌ لم يتم العثور على سجل يحتوي على رابط تغريدة في Airtable!")
