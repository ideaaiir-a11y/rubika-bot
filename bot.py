import csv
import os
import random
import requests
import time
from datetime import datetime

# ============= CONFIGURATION =============
rubika_BOT_TOKEN = os.environ.get("BOT_TOKEN")
rubika_CHAT_ID = os.environ.get("CHAT_ID")

# ============= TRANSLATION MAP =============
TRANSLATE_MAP = {
    "small towns": "شهرک‌های کوچک",
    "picturesque": "زیبا و رویایی",
    "America": "آمریکا",
    "world": "دنیا",
    "countries": "کشورها",
    "cuisine": "غذاها",
    "food": "غذا",
    "beaches": "سواحل",
    "travel": "سفر",
    "hidden": "پنهان",
    "best": "بهترین",
    "ranked": "رتبه‌بندی شده",
    "every day": "هر روز",
    "eggs": "تخم‌مرغ",
    "eat": "بخورید",
    "friendly": "مهربان",
    "street food": "غذای خیابانی",
    "Asia": "آسیا",
    "Europe": "اروپا",
    "visit": "بازدید",
    "travelers": "مسافران",
    "20 of the most": "۲۰ مورد از زیباترین",
    "What happens to your body": "اگر روزانه این غذا را بخورید چه اتفاقی می‌افتد؟",
    "The friendliest": "مهربان‌ترین",
    "Best street food": "بهترین غذاهای خیابانی",
    "Hidden beaches": "سواحل مخفی",
}

# ============= ADVERTISEMENT LINKS =============
AD_LINKS = [
    "https://go.rubika.ir/vodi65",
    "https://golinks.io/travel-deals",
    "https://rubika.ir/codenevesht"
]

def translate_to_persian(text):
    result = text
    for eng, per in TRANSLATE_MAP.items():
        result = result.replace(eng, per)
    if result == text:
        result = f"🌍 {text} که باید ببینید!"
    return result

def format_rubika_post(title, source, likes, image_url):
    persian_title = translate_to_persian(title)
    caption = f"""✨ {persian_title}

📌 منبع: {source}
❤️ {likes} لایک

🔗 تصویر: {image_url}

{random.choice(AD_LINKS)}"""
    return caption

def send_to_rubika(caption):
    if not rubika_BOT_TOKEN or not rubika_CHAT_ID:
        print("❌ Missing rubika credentials!")
        return False

url = f'https://botapi.rubika.ir/v3/{token}/sendMessage'
response = requests.post(url, json=data)

print(response.text)
  
data = {
    "chat_id": rubika_CHAT_ID,
    "text": "caption",
}


    try:
        response = requests.post(url, data=payload, timeout=15)
        if response.status_code == 200:
            print("✅ Post sent successfully!")
            return True
        else:
            print(f"❌ rubika error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Failed to send to rubika: {e}")
        return False

def process_csv():
    posts_created = 0
    try:
        with open('content.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                title = row.get('title', '').strip()
                source = row.get('source', '').strip()
                likes = int(row.get('likes', '0'))
                if not title:
                    continue

                print(f"\n📝 Processing: {title}")
                image_url = "https://images.pexels.com/photos/235734/pexels-photo-235774.jpeg"
                caption = format_rubika_post(title, source, likes, image_url)

                if send_to_rubika(caption):
                    posts_created += 1
                time.sleep(2)
    except FileNotFoundError:
        print("❌ content.csv not found!")
    except Exception as e:
        print(f"❌ Error processing CSV: {e}")
    return posts_created

def main():
    print("🚀 Starting rubika Content Automation...")
    print(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    posts = process_csv()
    print("=" * 50)
    print(f"✅ Automation complete! {posts} posts sent.")
    print("🔄 Waiting for next scheduled run...")

if __name__ == "__main__":
    main()
