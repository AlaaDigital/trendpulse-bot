import os
import requests
import random
from PIL import Image, ImageDraw, ImageFont
import textwrap

PAGE_ID = os.getenv("FB_PAGE_ID")
PAGE_TOKEN = os.getenv("FB_PAGE_TOKEN")

TRENDING_DATA = [
    {
        "title": "Marvel Studios Announcement",
        "volume": "300K+",
        "location": "US",
        "article": """Marvel Studios just shocked the internet with a massive announcement that has everyone talking!

According to reports, the studio revealed a new phase of movies that will change the MCU forever. Fans on X and TikTok are already breaking down every single detail.

Why is it trending?
- The announcement came out of nowhere during a live event
- It includes the return of a beloved character everyone thought was gone
- The trailer leaked and got 10M views in 1 hour

People are saying this could be the biggest Marvel moment since Endgame. The hype is unreal and memes are already everywhere.

What do you think? Is Marvel back on top? 👇"""
    },
    {
        "title": "iPhone 16 Pro Max Leaks",
        "volume": "500K+",
        "location": "Worldwide",
        "article": """The new iPhone 16 Pro Max leaks are insane and Apple fans can't handle it!

Leaked images show a completely new design with a bigger screen, titanium body, and a camera that looks like something from the future. Tech YouTubers are calling it the biggest upgrade in 3 years.

Key leaks:
- 8K video recording for the first time
- Battery that lasts 2 days
- New AI features built into iOS 18

The internet is divided - some say it's revolutionary, others say it's just another expensive phone. But one thing is sure, everyone is talking about it.

Would you buy it? 🤔"""
    },
]

def get_trending():
    return random.choice(TRENDING_DATA)

def generate_hashtags(title):
    words = title.split()
    tags = []
    for w in words:
        clean = ''.join(c for c in w if c.isalnum())
        if len(clean) > 2:
            tags.append(f"#{clean}")
    tags.extend(["#Trending", "#Viral", "#BreakingNews", "#ForYou", "#BingoyGana"])
    return " ".join(tags[:8])

def create_trend_image(title, volume, location):
    W, H = 1080, 1080
    img = Image.new('RGB', (W, H), color=(10, 10, 10))
    draw = ImageDraw.Draw(img)
    
    try:
        font_big = ImageFont.truetype("arial.ttf", 75)
        font_med = ImageFont.truetype("arial.ttf", 45)
        font_small = ImageFont.truetype("arial.ttf", 36)
    except:
        font_big = ImageFont.load_default()
        font_med = ImageFont.load_default()
        font_small = ImageFont.load_default()

    draw.rectangle([(0,0),(W,18)], fill=(255,45,85))
    draw.rectangle([(0,H-18),(W,H)], fill=(255,45,85))
    
    draw.text((50, 50), "🔥 TRENDING NOW", font=font_med, fill=(255,45,85))
    draw.text((50, 115), f"{location} • {volume} • {random.randint(10,23)}:{random.randint(10,59):02d} UTC", font=font_small, fill=(160,160,160))
    
    wrapped = textwrap.fill(title, width=18)
    draw.multiline_text((50, 260), wrapped, font=font_big, fill=(255,255,255), spacing=18)
    
    draw.text((50, 850), "👇 Full story in caption", font=font_med, fill=(255,45,85))
    draw.text((50, 920), "Bingoy Gana", font=font_small, fill=(100,100,100))
    
    path = "/tmp/trend.png"
    img.save(path)
    return path

def post_to_facebook(message, image_path=None):
    if not PAGE_ID or not PAGE_TOKEN:
        raise Exception("FB_PAGE_ID or FB_PAGE_TOKEN missing!")
    
    if image_path:
        url = f"https://graph.facebook.com/v20.0/{PAGE_ID}/photos"
        with open(image_path, 'rb') as f:
            files = {'source': f}
            data = {'message': message, 'access_token': PAGE_TOKEN}
            r = requests.post(url, files=files, data=data)
    else:
        url = f"https://graph.facebook.com/v20.0/{PAGE_ID}/feed"
        data = {'message': message, 'access_token': PAGE_TOKEN}
        r = requests.post(url, data=data)
    
    print(f"FB Response: {r.text}")
    r.raise_for_status()
    return r.json().get('post_id') or r.json().get('id')

def main():
    trend = get_trending()
    
    # === استراتيجية تكبير الصفحة: مقال كامل في البوست بدون رابط ===
    message = f"""📈 {trend['title']}
Trending in {trend['location']} [{trend['volume']}] 🔥

{trend['article']}

---
💬 شنو رأيك؟ اكتب في التعليقات!

{generate_hashtags(trend['title'])}"""
    
    image_path = create_trend_image(trend['title'], trend['volume'], trend['location'])
    post_id = post_to_facebook(message, image_path=image_path)
    print(f"✅ Posted with full article: {post_id}")

if __name__ == "__main__":
    main()
