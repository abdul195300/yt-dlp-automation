import yt_dlp
import requests
import os

# 🟢 إعدادات Airtable
AIRTABLE_API_KEY = "patS1VYb5EHfiXXBV.71390a90cefd89f88d05485625c803ba5df091b89acf76a160685dca3f4d46aa"  # استبدل بمفتاح Airtable API
AIRTABLE_BASE_ID = "app2j2xblYodCdMZQ"  # استبدل بـ Base ID
AIRTABLE_TABLE_NAME = "Table2"  # اسم الجدول في Airtable

# 🔹 رابط Airtable API لتحديث البيانات
AIRTABLE_URL = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_NAME}"

HEADERS = {
    "Authorization": f"Bearer {AIRTABLE_API_KEY}",
    "Content-Type": "application/json"
}

# 🟢 استلام رابط التغريدة من GitHub Actions
tweet_url = os.getenv("TWEET_URL")

if not tweet_url:
    print("❌ لم يتم توفير رابط التغريدة.")
    exit(1)

# 🟢 استخراج رابط الفيديو من التغريدة
def extract_video_url(url):
    """ استخراج رابط الفيديو المباشر من تويتر """
    ydl_opts = {
        'quiet': True,
        'skip_download': True,
        'force_generic_extractor': False
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            formats = info.get('formats', [])

            # البحث عن أفضل جودة فيديو متاحة
            video_url = next((f['url'] for f in formats if f['ext'] == 'mp4'), None)

            if video_url:
                return video_url
            else:
                return None

    except Exception as e:
        print(f"⚠️ خطأ أثناء استخراج الفيديو: {str(e)}")
        return None

# 🟢 استخراج رابط الفيديو
video_url = extract_video_url(tweet_url)

if video_url:
    print(f"🎥 رابط الفيديو المباشر: {video_url}")

    # تحديث Airtable برابط الفيديو
    payload = {
        "fields": {
            "tweet_url": tweet_url,
            "Video_URL": video_url
        }
    }

    response = requests.post(AIRTABLE_URL, json=payload, headers=HEADERS)

    if response.status_code == 200:
        print("✅ تم تحديث Airtable برابط الفيديو!")
    else:
        print(f"❌ فشل تحديث Airtable! كود الخطأ: {response.status_code}, التفاصيل: {response.text}")

else:
    print("❌ لم يتم العثور على فيديو في التغريدة.")
