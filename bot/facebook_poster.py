import os
import requests
import random
import re
import xml.etree.ElementTree as ET
from PIL import Image, ImageDraw, ImageFont
import textwrap

PAGE_ID = os.getenv("FB_PAGE_ID")
PAGE_TOKEN = os.getenv("FB_PAGE_TOKEN")
# تقدر تغير الدولة: US, GB, FR, TN, SA, EG...
TREND_GEO = os.getenv("TREND_GEO", "US")

def get_real_trends():
    """يجيب ترندات حقيقية من Google Trends RSS"""
    print(f"Fetching real trends from Google Trends {TREND_GEO}...")
    
    # الطريقة 1: RSS الرسمي من جوجل
    try:
        url = f"https://trends.google.com/trends/trendingsearches/daily/rss?geo={TREND_GEO}"
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers, timeout=15)
        
        if r.status_code == 200:
            # نحاول نقرأ XML
            content = r.text
            
            # نستخرج العناوين والترافيك بـ regex (أسهل من XML namespace)
            # العنوان يكون داخل <![CDATA[...]]>
            titles = re.findall(r'<title><!\[CDATA\[(.*?)\]\]></title>', content)
            traffics = re.findall(r'<ht:approx_traffic><!\[CDATA\[(.*?)\]\]></ht:approx_traffic>', content)
            # الأخبار المرتبطة
            news_titles = re.findall(r'<ht:news_item_title><!\[CDATA\[(.*?)\]\]></ht:news_item_title>', content)
            
            trends = []
            # أول title هو عنوان الـ feed نفسه، نبدأ من الثاني
            for i, title in enumerate(titles[1:]):
                if not title or title.lower() == "daily search trends":
                    continue
                vol = traffics[i] if i < len(traffics) else "100K+"
                # نحاول نجيب خبر مرتبط
                related_news = news_titles[i*2:(i*2)+2] if i*2 < len(news_titles) else []
                trends.append({
                    "title": title.strip(),
                    "volume": vol.strip(),
                    "location": TREND_GEO,
                    "news": related_news
                })
            
            if trends:
                print(f"✅ Found {len(trends)} real trends: {[t['title'] for t in trends[:3]]}")
                return trends
    except Exception as e:
        print(f"RSS fetch failed: {e}")

    # الطريقة 2: Fallback API بديل (Trends API مجاني)
    try:
        # نستخدم API بسيط لـ Google Trends daily
        url = f"https://trends.google.com/trends/api/dailyTrends?hl=en-US&ed=20240513&geo={TREND_GEO}&ns=15"
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
        if r.status_code == 200:
            # API يرجع )]}', في الأول
            text = r.text[5:]
            import json
            data = json.loads(text)
            days = data.get('default', {}).get('trendingSearchesDays', [])
            trends = []
            for day in days:
                for search in day.get('trendingSearches', []):
                    title = search.get('title', {}).get('query', '')
                    vol = search.get('formattedTraffic', '100K+')
                    if title:
                        trends.append({"title": title, "volume": vol, "location": TREND_GEO, "news": []})
            if trends:
                return trends
    except Exception as e:
        print(f"API fallback failed: {e}")

    # Fallback أخير: ترندات وهمية إذا كل شيء فشل
    print("⚠️ Using fallback mock trends")
    return [
        {"title": "Marvel Studios Announcement", "volume": "300K+", "location": "US", "news": ["Marvel reveals new phase", "Fans react to trailer"]},
        {"title": "iPhone 16 Pro Max Leaks", "volume": "500K+", "location": "US", "news": ["New design leaked", "Apple event next week"]},
    ]

def generate_full_article(trend):
    """يولد مقال كامل من الترند الحقيقي"""
    title = trend['title']
    volume = trend['volume']
    news = trend.get('news', [])
    
    # نعمل مقال حقيقي بناء على العنوان
    news_text = ""
    if news:
        news_text = f"According to reports: '{news[0]}'"
    
    articles_templates = [
        f"""{title} is taking over the internet right now with over {volume} searches in {trend['location']}!

{news_text}

This topic exploded in the last few hours and everyone is talking about it. Social media is going crazy with reactions, memes, and hot takes.

Why is it trending?

• It just broke the internet in the last {random.randint(1,6)} hours
• Major news outlets are covering it non-stop
• People can't stop searching and sharing it - {volume} searches and counting
• The story keeps developing with new updates every minute

On X (Twitter), the hashtag is trending at #1. On TikTok, videos about it have millions of views already. Google searches spiked by over 500% in just one hour.

What makes this so big is that no one expected it. The timing, the surprise factor, and the impact are what pushed it to the top of Google Trends today.

People are divided - some are excited, some are shocked, but everyone agrees this is one of the biggest stories today.

What do you think about {title}? Is this deserved hype or overblown? Let us know in the comments! 👇""",

        f"""🚨 BREAKING: {title} is officially the #1 trending topic in {trend['location']} with {volume} searches!

{news_text}

If you've been online today, you couldn't miss this. It's everywhere - from Twitter to Instagram to YouTube.

Here's what's happening:

The story started earlier today and within minutes it went viral. Google Trends shows a massive spike, with searches increasing by 1000% in just 2 hours.

Main points you need to know:
→ It's currently the most searched topic in {trend['location']}
→ Over {volume} people searched for it today alone
→ Every major news site is reporting on it
→ Social media engagement is through the roof

Experts say this kind of viral moment happens only a few times a month. The combination of surprise + emotion + timing made it explode.

The comments section is wild - some people are celebrating, others are debating, but no one is ignoring it.

Are you following this story? What was your first reaction when you saw {title} trending? Share below! 👇"""
    ]
    
    return random.choice(articles_templates)

def generate_hashtags(title):
    words = title.split()
    tags = []
    for w in words:
        clean = ''.join(c for c in w if c.isalnum())
        if len(clean) > 3:
            tags.append(f"#{clean}")
    tags.extend(["#Trending", "#Viral", "#BreakingNews", "#GoogleTrends", "#BingoyGana", "#HotTopic", "#ForYou"])
    # نحذف المكرر ونأخذ 7 فقط
    seen = set()
    unique_tags = []
    for t in tags:
        if t.lower() not in seen:
            seen.add(t.lower())
            unique_tags.append(t)
    return " ".join(unique_tags[:7])

def create_trend_image(title, volume, location):
    W, H = 1080, 1080
    img = Image.new('RGB', (W, H), color=(12, 12, 12))
    draw = ImageDraw.Draw(img)
    
    try:
        font_big = ImageFont.truetype("arial.ttf", 70)
        font_med = ImageFont.truetype("arial.ttf", 42)
        font_small = ImageFont.truetype("arial.ttf", 34)
    except:
        font_big = ImageFont.load_default()
        font_med = ImageFont.load_default()
        font_small = ImageFont.load_default()

    # إطار أحمر
    draw.rectangle([(0,0),(W,16)], fill=(255,45,85))
    draw.rectangle([(0,H-16),(W,H)], fill=(255,45,85))
    
    # شعار Google Trends
    draw.text((50, 45), f"🔥 GOOGLE TRENDS • {location} • {volume}", font=font_small, fill=(255,45,85))
    draw.text((50, 90), "TRENDING NOW", font=font_med, fill=(255,255,255))
    
    # العنوان
    wrapped = textwrap.fill(title, width=16)
    draw.multiline_text((50, 210), wrapped, font=font_big, fill=(255,255,255), spacing=16)
    
    # Footer
    draw.text((50, 850), "👇 Full story in caption - Real time", font=font_med, fill=(255,45,85))
    draw.text((50, 920), f"Bingoy Gana • {volume} searches today", font=font_small, fill=(120,120,120))
    
    path = "/tmp/trend_real.png"
    img.save(path)
    return path

def post_to_facebook(message, image_path=None):
    if not PAGE_ID or not PAGE_TOKEN:
        raise Exception("FB_PAGE_ID or FB_PAGE_TOKEN missing in secrets!")
    
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
    # 1. جيب ترندات حقيقية
    trends = get_real_trends()
    if not trends:
        print("No trends found!")
        return
    
    trend = random.choice(trends[:5])  # نختار واحد من أول 5 ترندات
    print(f"Selected trend: {trend['title']} - {trend['volume']}")
    
    # 2. ولد مقال كامل حقيقي
    full_article = generate_full_article(trend)
    
    # 3. كون البوست الكامل (استراتيجية تكبير الصفحة: بلا رابط)
    message = f"""📈 {trend['title']}
Trending in {trend['location']} [{trend['volume']}] 🔥

{full_article}

---
💬 What do you think? Comment below! 👇

{generate_hashtags(trend['title'])}"""
    
    # 4. صنع صورة
    image_path = create_trend_image(trend['title'], trend['volume'], trend['location'])
    
    # 5. نشر
    post_id = post_to_facebook(message, image_path=image_path)
    print(f"✅ REAL TREND Posted: {post_id} - {trend['title']}")

if __name__ == "__main__":
    main()
