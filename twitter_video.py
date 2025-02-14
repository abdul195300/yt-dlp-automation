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
DROPBOX_ACCESS_TOKEN = "sl.u.AFgsRlxHuL6g7Q9CgLa3yjOIdkpXoyJ9HSGmvf0AtVb7Nr_3yP2iyMfo8lhFTmqjdJ1t9_zoCnR9RC4oJsz9Ik5mvdCq43oNm-XQHO0u6rnBR22p5N5FtqeaU3o5Avmzg0Q2aQL8y0tJ59b-hIFwS5QLCjjzIhWGcpPR2bfnNIVhFtGNtpBkVJvb_FyqQvEgkE_ZTokLF_Q9luCjZFWCt1KIHZrHFSyPhS6kYpZ511b8e6cd6kIEHBw1UmQHtgM__4_tWzemJrhL8_ga96C7KbM7xGxhTH69rCNEcwmHQayw7Mq6DxExydtQtzjYs6VUURkvF09gCchcDFBFSoN3gKWbwCQpOzTpetNvAOjGItbSX1DN2UUhP-clLKxJZAiDSkkRT3TXq2qiRsp5x6Lp72k5AWwD-NKnwSyI9ma5dGt9sWvHoQgdXl6gsM-kFsuUd75fmuQy8Lw9VoxjCa2PQFzxucK3fx-Aom8WxfItrQAIcdCyxcDGJ26DhEWk3M1LERRIb13I_ybcBSlABlp_331pa1S9vxSENpNG0WPq-o96GVxNSHVaRLfe0uFv08LhWghTQe0xZ94VRXElRhPm1Niuzkw9c3B-VXzNowUd9TcDwRk4PA1FLr34goFoFMW4m_vk_Vj2GDXYMSSSwsdHMW1youGfU7fCVYBjQXu49wxGeM6PYSnqdzxLiX2qXXEAJ6zy1UIuWvQBBiripaRy413p_krCMjTQaAr2fiF0uPfTLS7C4aUzjsT1NQ59VNgheRG3Oodkc_mYB-hJIXsYK1B8KQ0arNMmpl2KGrXlDO-RckwxZXnX9Ik7OnsUqqyaz1h66wFI4ICmeCe5AEBhbEPmStrPYg_a0-cZZY_iq_iBl46PHfE680LnVcxhzCNc9Qzlmmg2yas40qLbwiWkmzKkCq7VXzgh4jw-7e0_COvhTReF_Ducf67rSSmN3UtNAGAUogAqSdzN9NBoc2drJw0jzgrdMdEmOxngJm1s-FG1Wyjjz8Q3BOIrwk-tZkKmgDYa6YA9SZA0-6OhBJFHOcJ8tolXRwmdQA4jmw-kpTlTve3RZxZyaFmHjMLVZ9-HhmZXjsBsrA1mBFIQfqitocsPCRabitHJzewwhhsq3Q-C-dnepOojG3Tec2wwEplmlmEE7O3wFEvK0LIjYZRkVPeKicdnD7Q-547GwvUJIxrQ135rORipq0EWf1LoT4pofzxbWohSwtK02vUw1bBjgjM4By7McGPQaBK9OavaKiTYqw"
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
