import os
import requests
from trends_fetcher import get_all_entertainment_trends
import random
from datetime import datetime

PAGE_ID = os.environ.get("FB_PAGE_ID")
PAGE_TOKEN = os.environ.get("FB_PAGE_TOKEN")

TEMPLATES = [
    "🔥 Trending Now in {country}: {title} {traffic}\n\nWhat's your take? 👇 #Trending #Entertainment #Viral",
    "🚀 {title} is blowing up in {country}! {traffic} searches\n\nAre you following this? 👀 #Trends2026 #Entertainment",
    "✨ BREAKING TREND: {title} ({country}) - {traffic}\n\nDrop your opinion below! 💬 #GoogleTrends #US #UK #Canada",
    "📈 Hot Topic: {title}\nTrending in {country} with {traffic}\n\nThis is taking over the internet! 🔥",
    "🎬 Entertainment Pulse: {title} is TOP trend in {country} right now! {traffic}\n\nWhy is everyone talking about it? 🤔"
]

def post_to_facebook(message):
    url = f"https://graph.facebook.com/v20.0/{PAGE_ID}/feed"
    data = {
        "message": message,
        "access_token": PAGE_TOKEN
    }
    r = requests.post(url, data=data)
    print("FB Response:", r.text)
    r.raise_for_status()
    return r.json()

def main():
    if not PAGE_ID or not PAGE_TOKEN:
        raise ValueError("Set FB_PAGE_ID and FB_PAGE_TOKEN secrets")
    
    trends = get_all_entertainment_trends()
    if not trends:
        print("No trends found")
        return
    
    trend = random.choice(trends)
    template = random.choice(TEMPLATES)
    message = template.format(
        title=trend["title"],
        country=trend["country"],
        traffic=f"[{trend['traffic']}]" if trend["traffic"] else "Trending"
    )
    
    # Add timestamp to avoid duplicate detection
    message += f"\n\n⏰ {datetime.utcnow().strftime('%H:%M UTC')}"
    
    result = post_to_facebook(message)
    print(f"Posted: {result}")

if __name__ == "__main__":
    main()
