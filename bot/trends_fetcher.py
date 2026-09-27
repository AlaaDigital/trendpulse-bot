import feedparser
import random

# Google Trends Daily RSS for US, CA, GB
GEOS = {
    "US": "US",
    "CA": "CA", 
    "GB": "GB"
}

def get_trends(geo="US", max_results=10):
    url = f"https://trends.google.com/trends/trendingsearches/daily/rss?geo={geo}"
    feed = feedparser.parse(url)
    trends = []
    for entry in feed.entries[:max_results]:
        title = entry.title
        # entry.title is like "Topic - 50k+ searches"
        clean_title = title.split(" - ")[0] if " - " in title else title
        trends.append({
            "title": clean_title,
            "traffic": entry.get("ht_approx_traffic", ""),
            "link": entry.link
        })
    return trends

def get_all_entertainment_trends():
    """Fetch from 3 countries and mix"""
    all_trends = []
    for geo in GEOS:
        try:
            t = get_trends(geo, 7)
            for item in t:
                item["country"] = geo
                all_trends.append(item)
        except Exception as e:
            print(f"Error fetching {geo}: {e}")
    
    # Deduplicate by title
    seen = set()
    unique = []
    for tr in all_trends:
        if tr["title"].lower() not in seen:
            seen.add(tr["title"].lower())
            unique.append(tr)
    
    random.shuffle(unique)
    return unique

if __name__ == "__main__":
    print(get_all_entertainment_trends()[:5])
