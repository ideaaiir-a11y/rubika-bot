"""
rubika Content Automation Bot
Automates content creation and posting to rubika channels
Runs on GitHub Actions - completely free and 24/7
"""

import csv
import json
import random
import requests
import os
import time
from datetime import datetime

# ============= CONFIGURATION =============
rubika_BOT_TOKEN = os.environ.get("BOT_TOKEN")
rubika_CHAT_ID = os.environ.get("CHAT_ID")
PEXELS_API_KEY = os.environ.get("PEXELS_KEY")

# ============= TRANSLATION MAP (Common English to Persian) =============
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
    "body": "بدن",
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

# ============= IMAGE DESCRIPTIONS BY CATEGORY =============
IMAGE_DESCRIPTIONS = {
    "town": [
        "خانه‌های چوبی با رنگ‌های گرم پاییزی",
        "خیابان‌های سنگ‌فرش در کنار رودخانه",
        "منظره‌ای از کوه‌های سرسبز در پس‌زمینه",
        "غروب آفتاب در تپه‌های سرسبز",
        "صبح‌های مه‌آلود در دل طبیعت"
    ],
    "food": [
        "سفره‌ای رنگارنگ از غذاهای لذیذ",
        "آشپزی سنتی در آشپزخانه‌ای دنج",
        "طعم‌های بی‌نظیر از سراسر جهان",
        "دستور پخت‌های قدیمی با عشق",
        "رنگ و بوی غذاهای خیابانی"
    ],
    "beach": [
        "ساحلی شنی با آب‌های فیروزه‌ای",
        "غروب آفتاب بر روی امواج دریا",
        "درختان نخل در کنار ساحل",
        "موج‌های آرام که به ساحل می‌رسند",
        "جای پایی که در شن باقی مانده"
    ],
    "travel": [
        "چمدان‌های آماده برای سفر",
        "هواپیماهایی که در آسمان پرواز می‌کنند",
        "نقشه‌های قدیمی و قطب‌نما",
        "کوله‌پشتی و جاده‌های بی‌انتها",
        "پاسپورت و ویزاهای مختلف"
    ],
    "default": [
        "منظره‌ای بی‌نظیر از طبیعت",
        "زیبایی‌های پنهان جهان",
        "تجربه‌ای فراموش‌نشدنی",
        "لحظات شادی و آرامش",
        "سفری به دل طبیعت"
    ]
}

# ============= HASHTAGS BY CATEGORY =============
HASHTAGS = {
    "town": ["#سفر", "#آمریکا", "#شهرک_تاریخی", "#طبیعت", "#گردشگری"],
    "food": ["#غذا", "#آشپزی", "#رژیم_غذایی", "#سلامتی", "#آشپزخانه"],
    "beach": ["#ساحل", "#دریا", "#توریسم", "#تعطیلات", "#دریاچه"],
    "travel": ["#سفر", "#گردشگری", "#جهانگردی", "#ماجراجویی", "#توریسم"],
    "default": ["#سفر", "#گردشگری", "#دنیا", "#زیبایی", "#طبیعت"]
}

# ============= PERSIAN EMOJIS =============
EMOJI_SETS = {
    "town": ["🌍", "🏘️", "🌄", "🍂", "✨"],
    "food": ["🍽️", "🥗", "🍳", "👨‍🍳", "✨"],
    "beach": ["🏖️", "🌊", "☀️", "🌴", "✨"],
    "travel": ["✈️", "🗺️", "🎒", "🌟", "📍"],
    "default": ["🌟", "✨", "📍", "💫", "🌍"]
}

# ============= ADVERTISEMENT LINKS =============
AD_LINKS = [
    "https://go.rubika.ir/vodi65",
    "https://golinks.io/travel-deals",
    "https://t.me/your_channel"
]


def translate_to_persian(text):
    """Simple translation using dictionary mapping"""
    result = text
    for eng, per in TRANSLATE_MAP.items():
        result = result.replace(eng, per)
    
    # If no translation found, add some Persian flair
    if result == text:
        result = f"🌍 {text} که باید ببینید!"
    
    return result


def detect_category(title):
    """Detect content category from title"""
    title_lower = title.lower()
    
    if any(word in title_lower for word in ['town', 'country', 'cities', 'village']):
        return "town"
    elif any(word in title_lower for word in ['food', 'eat', 'cuisine', 'cooking', 'recipe']):
        return "food"
    elif any(word in title_lower for word in ['beach', 'sea', 'ocean', 'coast']):
        return "beach"
    elif any(word in title_lower for word in ['travel', 'trip', 'visit', 'tourism']):
        return "travel"
    else:
        return "default"


def search_pexels_image(query, category):
    """Search Pexels for relevant image"""
    if not PEXELS_API_KEY:
        # Return a default placeholder image if no API key
        return "https://images.pexels.com/photos/235734/pexels-photo-235774.jpeg"
    
    headers = {
        "Authorization": PEXELS_API_KEY
    }
    
    # Enhance query based on category
    enhanced_query = f"{query} {category}"
    
    try:
        # Search for photos
        search_url = f"https://api.pexels.com/v1/search?query={enhanced_query}&per_page=5&orientation=landscape"
        response = requests.get(search_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            photos = data.get('photos', [])
            
            if photos:
                # Get a high-quality image (prefer larger sizes)
                photo = random.choice(photos)
                src = photo.get('src', {})
                
                # Try to get largest available size
                for size in ['original', 'large', 'medium', 'small']:
                    if size in src and src[size]:
                        return src[size]
        
        return None
    except Exception as e:
        print(f"Pexels API error: {e}")
        return None


def format_rubika_post(title, source, likes, image_url, category):
    """Format the final rubika post"""
    
    # Translate title
    persian_title = translate_to_persian(title)
    
    # Get random elements based on category
    descs = IMAGE_DESCRIPTIONS.get(category, IMAGE_DESCRIPTIONS["default"])
    hashtags = HASHTAGS.get(category, HASHTAGS["default"])
    emojis = EMOJI_SETS.get(category, EMOJI_SETS["default"])
    
    # Select random elements
    selected_descs = random.sample(descs, min(3, len(descs)))
    selected_hashtags = random.sample(hashtags, min(3, len(hashtags)))
    emoji_header = random.choice(emojis)
    
    # Format descriptions
    descriptions_text = "\n".join([f"«{desc}»" for desc in selected_descs])
    
    # Calculate random engagement stats
    comments = random.randint(1, 10)
    shares = random.randint(1, 20)
    likes_formatted = f"{likes:,}" if likes >= 1000 else str(likes)
    
    # Build caption
    caption = f"""{emoji_header} {persian_title}

{descriptions_text}

{" ".join(selected_hashtags)}
{likes_formatted} لایک | {comments} نظر | {shares} به اشتراک گذاشته شده {random.choice(['💫', '✨', '🌟'])}

{random.choice(AD_LINKS)}"""
    
    return caption


def send_to_rubika(image_url, caption):
    """Send post to rubika channel"""
    if not rubika_BOT_TOKEN or not rubika_CHAT_ID:
        print("Missing rubika credentials!")
        return False
    
    url = f"https://botapi.rubika.ir/v3/{rubika_BOT_TOKEN}/sendPhoto"
    
    payload = {
        "photo": image_url,
        "caption": caption,
        "chat_id": rubika_CHAT_ID,
        "parse_mode": "HTML"
    }
    
    try:
        response = requests.post(url, json=payload, timeout=15)
        
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
    """Main processing function - reads CSV and sends posts"""
    
    # Read CSV file
    posts_created = 0
    
    try:
        with open('content.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            # Process each row
            for row in reader:
                title = row.get('title', '').strip()
                source = row.get('source', '').strip()
                likes = int(row.get('likes', '0'))
                
                if not title:
                    continue
                
                print(f"\n📝 Processing: {title}")
                
                # Detect category
                category = detect_category(title)
                
                # Search for image
                image_url = search_pexels_image(title, category)
                
                if not image_url:
                    # Use placeholder
                    image_url = "https://images.pexels.com/photos/235734/pexels-photo-235774.jpeg"
                
                # Format post
                caption = format_rubika_post(title, source, likes, image_url, category)
                
                # Send to rubika
                if send_to_rubika(image_url, caption):
                    posts_created += 1
                
                # Add delay to avoid rate limits
                time.sleep(2)
    
    except FileNotFoundError:
        print("❌ content.csv not found!")
    except Exception as e:
        print(f"❌ Error processing CSV: {e}")
    
    return posts_created


def main():
    """Main entry point"""
    print("🚀 Starting rubika Content Automation...")
    print(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    posts = process_csv()
    
    print("=" * 50)
    print(f"✅ Automation complete! {posts} posts sent.")
    print("🔄 Waiting for next scheduled run...")


if __name__ == "__main__":
    main()
