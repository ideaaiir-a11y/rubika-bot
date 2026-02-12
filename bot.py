# -*- coding: utf-8 -*-
"""
سیستم اتوماسیون محتوای اخلاقی
الهام‌گرفته از عناصر ایرانی: آتش، آب، باد، خاک
"""

import csv
import json
import logging
import os
import random
import time
from datetime import datetime
from rubika import Bot

# تنظیمات لاگ
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# اسرار از GitHub Secrets
BOT_TOKEN = os.environ.get("rubika_BOT_TOKEN")
CHANNEL_ID = os.environ.get("CHANNEL_ID")

# 🟡 خاک (Earth): لایه‌ی داده و امنیت
class Khak:
    """خاک: نگهداری وضعیت و امنیت"""
    def __init__(self, state_file="state.json"):
        self.state_file = state_file
        self.state = self._load_state()

    def _load_state(self):
        if os.path.exists(self.state_file):
            with open(self.state_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"last_post": None}

    def save_state(self):
        with open(self.state_file, "w", encoding="utf-8") as f:
            json.dump(self.state, f, ensure_ascii=False, indent=2)

# 🔵 آب (Water): جریان محتوا و CSV
class Ab:
    """آب: خواندن محتوا از CSV"""
    def __init__(self, csv_file="content.csv"):
        self.csv_file = csv_file

    def read_content(self):
        with open(self.csv_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            return list(reader)

# 🟢 باد (Wind): تحلیل و تعامل
class Bad:
    """باد: ردیابی تعامل و تحلیل ساده"""
    def __init__(self):
        self.analytics_file = "analytics.json"
        if not os.path.exists(self.analytics_file):
            with open(self.analytics_file, "w", encoding="utf-8") as f:
                json.dump({"posts_sent": 0}, f)

    def update(self):
        with open(self.analytics_file, "r+", encoding="utf-8") as f:
            data = json.load(f)
            data["posts_sent"] += 1
            f.seek(0)
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.truncate()

# 🔴 آتش (Fire): موتور انتشار
class Atash:
    """آتش: انرژی و موتور انتشار"""
    def __init__(self, bot_token, channel_id):
        self.bot = Bot(token=bot_token)
        self.channel_id = channel_id

    def publish(self, title, body, media_url, tags):
        caption = f"🔥 {title}\n\n{body}\n\n📌 برچسب‌ها: {tags}"
        if media_url:
            self.bot.send_photo(chat_id=self.channel_id, photo=media_url, caption=caption)
        else:
            self.bot.send_message(chat_id=self.channel_id, text=caption)
        logging.info(f"✅ پست ارسال شد: {title}")

# 🌍 چرخه اصلی
def gardish():
    khak = Khak()
    ab = Ab()
    bad = Bad()
    atash = Atash(BOT_TOKEN, CHANNEL_ID)

    content_list = ab.read_content()
    for item in content_list:
        timestamp = item["timestamp"]
        if khak.state["last_post"] == timestamp:
            continue
        atash.publish(item["title_fa"], item["body_fa"], item["media_url"], item["tags"])
        khak.state["last_post"] = timestamp
        khak.save_state()
        bad.update()
        time.sleep(2)  # نفس (interval)

if __name__ == "__main__":
    logging.info("🚀 شروع اتوماسیون محتوای اخلاقی...")
    gardish()
