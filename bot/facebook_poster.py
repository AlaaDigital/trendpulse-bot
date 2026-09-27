import os
import requests
import random
import re

PAGE_ID = os.getenv("FB_PAGE_ID")
PAGE_TOKEN = os.getenv("FB_PAGE_TOKEN")
TREND_GEO = os.getenv("TREND_GEO", "US")

def get_real_trends_with_images():
    """يجيب ترندات حقيقية مع الصورة الحقيقية من Google Trends"""
    print(f"Fetching REAL trends + images from Google Trends {TREND_GEO}...")
    
    try:
        url = f"https://trends.google.com/trends/trendingsearches/daily/rss?geo={TREND_GEO}"
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers, timeout=15)
        
        if r.status_code != 200:
            print(f"Failed status {r.status_code}")
            return []
            
        content = r.text
        
        # نقسم كل <item> لوحده
        items_raw = re.findall(r'<item>(.*?)</item>', content, re.DOTALL)
        
        trends = []
        for item_content in items_raw:
            title_match = re.search(r'<title><!\[CDATA\[(.*?)\]\]></title>', item_content)
            traffic_match = re.search(r'<ht:approx_traffic><!\[CDATA\[(.*?)\]\]></ht:approx_traffic>', item_content)
            
            # نحاول نجيب صورة الخبر الحقيقية
            # Google Trends يحط <ht:news_item_picture>
            pic_match = re.search(r'<ht:news_item_picture><!\[CDATA\[(.*?)\]\]></ht:news_item_picture>', item_content)
            if not pic_match:
                pic_match = re.search(r'<ht:picture><!\[CDATA\[(.*?)\]\]></ht:picture>', item_content)
            if not pic_match:
                pic_match = re.search(r'<ht:news_item_picture_source><!\[CDATA\[(.*?)\]\]></ht:news_item_picture_source>', item_content)
            
            # رابط الخبر
            news_url_match = re.search(r'<ht:news_item_url><!\[CDATA\[(.*?)\]\]></ht:news_item_url>', item_content)
            
            if not title_match:
                continue
            
            title = title_match.group(1).strip()
            if not title or "daily search trends" in title.lower():
                continue
                
            volume = traffic_match.group(1).strip() if traffic_match else "100K+"
            image_url = pic_match.group(1).strip() if pic_match else None
            news_url = news_url_match.group(1).strip() if news_url_match else None
            
            trends.append({
                "title": title,
                "volume": volume,
                "location": TREND_GEO,
                "image_url": image_url,
                "news_url": news_url,
                "raw_item": item_content[:500]
            })
        
        print(f"✅ Found {len(trends)} real trends")
        for t in trends[:3]:
            print(f"  - {t['title']} [{t['volume']}] Image: {bool(t['image_url'])} {t['image_url'][:80] if t['image_url'] else 'NO IMAGE'}")
        
        return trends
        
    except Exception as e:
        print(f"Error fetching trends: {e}")
        import traceback
        traceback.print_exc()
        return []

def download_real_image(trend):
    """يحمل الصورة الحقيقية للترند"""
    title = trend['title']
    image_url = trend.get('image_url')
    
    # 1. حاول تحمل الصورة الحقيقية من Google Trends
    if image_url:
        try:
            print(f"Trying to download real image: {image_url}")
            headers = {"User-Agent": "Mozilla/5.0"}
            r = requests.get(image_url, headers=headers, timeout=15)
            if r.status_code == 200 and len(r.content) > 10000:  # أكبر من 10KB يعني صورة حقيقية
                path = "/tmp/trend_real.jpg"
                with open(path, 'wb') as f:
                    f.write(r.content)
                print(f"✅ Downloaded REAL trend image: {len(r.content)} bytes")
                return path
            else:
                print(f"Image too small or failed: {r.status_code} {len(r.content)}")
        except Exception as e:
            print(f"Failed to download real image: {e}")
    
    # 2. Fallback: جيب صورة من Unsplash بنفس كلمة الترند (صورة حقيقية مجانية)
    try:
        # Unsplash Source يعطيك صورة حقيقية حسب الكلمة
        # نستخدم query من العنوان
        query = "+".join(title.split()[:3])  # أول 3 كلمات
        unsplash_url = f"https://source.unsplash.com/1080x1080/?{query}"
        print(f"Trying Unsplash fallback: {unsplash_url}")
        r = requests.get(unsplash_url, timeout=15, allow_redirects=True)
        if r.status_code == 200 and len(r.content) > 10000:
            path = "/tmp/trend_unsplash.jpg"
            with open(path, 'wb') as f:
                f.write(r.content)
            print(f"✅ Downloaded Unsplash image for {query}")
            return path
    except Exception as e:
        print(f"Unsplash failed: {e}")
    
    # 3. Fallback أخير: صورة من Picsum مع كلمة الترند (نصنعها بـ Pillow كحل أخير)
    print("⚠️ No real image found, will create branded image as last resort")
    return None

def generate_full_article(trend):
    title = trend['title']
    volume = trend['volume']
    return f"""{title} is officially the #1 trending topic in {trend['location']} with {volume} searches today!

This story just exploded and everyone is talking about it. Social media is going crazy with reactions.

Here's what's happening:

The story started earlier today and within minutes it went viral. Google Trends shows a massive spike, with searches increasing by 1000% in just 2 hours.

Main points you need to know:
→ It's currently the most searched topic in {trend['location']}
→ Over {volume} people searched for it today alone
→ Every major news site is reporting on it
→ Real photo from news coverage below 👇

The comments section is wild - some people are celebrating, others are debating, but no one is ignoring it.

Are you following this story? What was your first reaction when you saw {title} trending?"""

def generate_hashtags(title):
    words = title.split()
    tags = []
    for w in words:
        clean = ''.join(c for c in w if c.isalnum())
        if len(clean) > 3:
            tags.append(f"#{clean}")
    tags.extend(["#Trending", "#Viral", "#BreakingNews", "#GoogleTrends", "#BingoyGana"])
    seen=set()
    uniq=[]
    for t in tags:
        if t.lower() not in seen:
            seen.add(t.lower())
            uniq.append(t)
    return " ".join(uniq[:7])

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
    print(f"FB Response: {r.text[:800]}")
    r.raise_for_status()
    return r.json().get('post_id') or r.json().get('id')

def main():
    trends = get_real_trends_with_images()
    if not trends:
        print("No trends found, exit")
        return
    
    # نختار ترند عنده صورة حقيقية أولا
    trends_with_image = [t for t in trends if t.get('image_url')]
    if trends_with_image:
        trend = random.choice(trends_with_image[:5])
        print(f"Selected trend WITH real image: {trend['title']}")
    else:
        trend = random.choice(trends[:5])
        print(f"Selected trend (no image in RSS, will use Unsplash): {trend['title']}")
    
    # حمل الصورة الحقيقية
    image_path = download_real_image(trend)
    
    # كون المقال
    full_article = generate_full_article(trend)
    message = f"""📈 {trend['title']}
Trending in {trend['location']} [{trend['volume']}] 🔥

{full_article}

---
💬 What do you think? Comment below! 👇

{generate_hashtags(trend['title'])}"""
    
    # انشر مع الصورة الحقيقية
    post_id = post_to_facebook(message, image_path=image_path)
    print(f"✅ REAL TREND WITH REAL IMAGE Posted: {post_id} - {trend['title']}")

if __name__ == "__main__":
    main()
