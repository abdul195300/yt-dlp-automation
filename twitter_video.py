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
DROPBOX_ACCESS_TOKEN = "sl.u.AFi0vG9NAyw7QotK7UNwgShAReqraeTNGHlcy9d8Byu7agfHxUe3UsoQR-hgmmeVdT9Y4Gdeg55uL2p8sx0cT6PwX6AOV9QCD-9WdG1uA4M2pjpL5UNLRVxJYYeqqPIMY36-HcQ1ksgbFSH8rv5lqFW8qAANH3Vf-8-RF_ip0H48vrqF3kiPBhzU7vhMMxaV4nS__fGFxXcyVH7sPXzyURNWPETZTIkmTQqifzhMflhg31DUGb7vXTOuGny9j5qdht8hXEVV-VDd8zGta1kkAe2-aN7mrFyR6NwkReE3OOMMlvDfDOKiyDhDdrow0yQ9gmt4fydLrzE85tWwxlZT8X1leKCO6LpHxvgkF01IUYzRovZFZcX92uIlD-uQI0nFqIgCJRyMVH1J1rW-LpFt60yHTvZQ39vlIbsV2xkcNRP91wc6BVyXkdRwyqa-1oOgruZyNMM2-OaLl_ZI2lhns6r0p1C3iE01W6YrTdF6Hco1R1hoXd9cZ6WaCVUspyKPhx3B8YM4ULMuq5DtHk8kup7E7YiMEj61wVtiFVT4r6Jx0dk0MGn6FpcRj9x8HoNJnOZSF5InimXaAk1M4iXDeixtYhCazqCDI3TrREsQhnNXHhQCU4CaJCis0mGODAAr6hgCmjsQBCQQGoKyQxqTjgYZI-_hQ2wq2Ug67EfeG-7ZIMKbzNs6eE6KxKuZT1fhzxp9kRcctWU14PSuA_VnImOm8GyezIdF4VJD6md_Bw1mNYlG0jWJeSPmAKdsovz79Ixwq_G_M2mcuH3WBu9k3YkIFa27dMDSpyGva9Bacwp-MdGmR-PIK23CDBUeMES89w3TenC6O3yTPMe1fVX0KOk4QGuBZbeZgIh1TiSGs5iCAwAAn_zgNmfQ0_cD0G09aZL6aL_Wz4HZIPyzirH-0jhs9ShT8EdeKZhERkW6KQkxks6sTsSzdiz-iT30Qqp7Mucrhre5G0IQS79xTj6Cg1SP4QSI8LMWPWi7ud3Zl9qP8kY0pv9mdGURlpBFe6DCv-GOLTpIXbEXFpsmeIxiGw9FVUVyg2fce4FGAfRNVTTXs4kdjzOiw3iI2uvMgVJEocs15ITw2rsWkxK7qupiDRXYNYAIBtc5SQso5kddy1z_7ZJQOL82bwsnHaeUdrm-yNH-JszV5_8ZypheeAmylEpg9zqujRqd4BF-Y5VV7kuLcL8OxSRRTsg64mkZP2dk5FpO2vwK6T4ciaxRcuaQ31PccuPtO0qY33BE1gwiQVSr5Tcbw6i9v5YR3KQ7ht2EISw"
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
        'quiet': False,  # تعطيل الوضع الصامت لرؤية التفاصيل
        'verbose': True,  # تشغيل وضع التصحيح لعرض مزيد من المعلومات
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

    # 🔹 طلب رابط المشاركة من Dropbox
    data = json.dumps({"path": DROPBOX_UPLOAD_PATH})
    response = requests.post("https://api.dropboxapi.com/2/sharing/create_shared_link_with_settings", headers=headers, data=data)

    if response.status_code == 200:
        shared_link = response.json()["url"]
        print(f"📌 رابط المشاركة من Dropbox: {shared_link}")

        # ✅ تحويل رابط Dropbox إلى رابط تنزيل مباشر:
        direct_download_link = shared_link.replace("www.dropbox.com", "dl.dropboxusercontent.com").replace("?dl=0", "")
        print(f"📌 رابط التحميل المباشر للفيديو: {direct_download_link}")

        return direct_download_link
    else:
        print(f"❌ فشل الحصول على رابط المشاركة! التفاصيل: {response.text}")
        return None
        
    # 🔄 **5. تحديث سجل Airtable بالفيديو كمرفق**
    def update_airtable(record_id, video_url):
    if not video_url or not video_url.startswith("http"):
        print("❌ الرابط المستخرج غير صالح، لن يتم تحديث Airtable!")
        return

    update_url = f"{AIRTABLE_URL}/{record_id}"
    
    # ✅ استخدم اسم الحقل الصحيح في Airtable
    correct_field_name = "Video_File"

    payload = {
        "fields": {
            correct_field_name: [{"url": video_url}]
        }
    }

    response = requests.patch(update_url, json=payload, headers=HEADERS)
    if response.status_code == 200:
        print("✅ تم تحديث السجل في Airtable بنجاح!")
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
