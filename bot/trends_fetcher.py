import requests
import feedparser
import random

GEOS = ["US", "CA", "GB"]

FALLBACK_TRENDS = [
    {"title": "Taylor Swift New Album", "traffic": "500K+", "country": "US"},
    {"title": "Marvel Studios Announcement", "traffic": "300K+", "country": "US"},
    {"title": "Netflix Top 10 Movies", "traffic": "200K+", "country": "GB"},
    {"title": "Drake New Song", "traffic": "400K+", "country": "CA"},
    {"title": "Oscars 2026 Predictions", "traffic": "250K+", "country": "US"},
]

def get_trends(geo="US", max_results=7):
    url = f"https://trends.google.com/trends/trendingsearches/daily/rss?geo={geo}"
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        resp = requests.get(url, headers=headers, timeout=15)
        feed = feedparser.parse(resp.content)
        trends = []
        for entry in feed.entries[:max_results]:
            title = entry.title.split(" - ")[0].strip()
            if title:
                trends.append({"title": title, "traffic": getattr(entry, 'ht_approx_traffic', ''), "country": geo})
        return trends
    except Exception as e:
        print(f"Error {geo}: {e}")
        return []

def get_all_entertainment_trends():
    all_trends = []
    for geo in GEOS:
        all_trends.extend(get_trends(geo, 7))
    if not all_trends:
        print("Using fallback trends")
        return FALLBACK_TRENDS
    seen=set(); unique=[]
    for tr in all_trends:
        if tr["title"].lower() not in seen:
            seen.add(tr["title"].lower()); unique.append(tr)
    random.shuffle(unique)
    return unique
