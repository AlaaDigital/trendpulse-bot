import os
import requests
import random
from PIL import Image, ImageDraw, ImageFont
from trends_fetcher import get_all_entertainment_trends

PAGE_ID = os.environ.get("FB_PAGE_ID")
PAGE_TOKEN = os.environ.get("FB_PAGE_TOKEN")

# Create 1080x1920 reel (9:16)
WIDTH, HEIGHT = 1080, 1920

COLORS = [
    ((255, 64, 129), (64, 196, 255)), # pink to blue
    ((255, 193, 7), (255, 87, 34)),   # yellow to orange
    ((76, 175, 80), (0, 150, 136)),   # green gradient
    ((103, 58, 183), (33, 150, 243)), # purple to blue
]

def create_reel_image(trend_title, country):
    bg1, bg2 = random.choice(COLORS)
    # Create gradient
    img = Image.new('RGB', (WIDTH, HEIGHT), bg1)
    draw = ImageDraw.Draw(img)
    
    # Simple vertical gradient
    for y in range(HEIGHT):
        r = int(bg1[0] + (bg2[0]-bg1[0]) * y / HEIGHT)
        g = int(bg1[1] + (bg2[1]-bg1[1]) * y / HEIGHT)
        b = int(bg1[2] + (bg2[2]-bg1[2]) * y / HEIGHT)
        draw.line([(0, y), (WIDTH, y)], fill=(r,g,b))
    
    # Try to load font, fallback to default
    try:
        # GitHub Actions has DejaVu
        font_big = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 90)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 50)
    except:
        font_big = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # Overlay dark box for readability
    draw.rectangle([(50, 700), (WIDTH-50, 1300)], fill=(0,0,0,180))
    
    # Text wrapping
    title = trend_title[:60]
    draw.text((80, 750), f"🔥 TRENDING IN {country}", font=font_small, fill=(255,255,0))
    
    # Wrap title
    words = title.split()
    lines = []
    current = ""
    for w in words:
        if len(current + " " + w) < 20:
            current += " " + w
        else:
            lines.append(current.strip())
            current = w
    lines.append(current.strip())
    
    y_offset = 850
    for line in lines[:3]:
        draw.text((80, y_offset), line.upper(), font=font_big, fill=(255,255,255))
        y_offset += 120
    
    draw.text((80, y_offset+50), "Follow for daily trends 👇", font=font_small, fill=(255,255,255))
    
    path = "/tmp/reel.jpg"
    img.save(path)
    return path

def create_reel_video(image_path, trend_title):
    """Convert image to 7-second video using ffmpeg (available on GitHub Actions)"""
    video_path = "/tmp/reel.mp4"
    # Create video from image - 7 seconds, 1080x1920
    os.system(f"ffmpeg -y -loop 1 -i {image_path} -c:v libx264 -t 7 -pix_fmt yuv420p -vf scale=1080:1920 {video_path} -loglevel quiet")
    return video_path

def upload_reel(video_path, description):
    # Step 1: init upload
    url = f"https://graph.facebook.com/v20.0/{PAGE_ID}/video_reels"
    with open(video_path, 'rb') as f:
        files = {'video': f}
        data = {
            'access_token': PAGE_TOKEN,
            'description': description
        }
        r = requests.post(url, files=files, data=data)
        print("Reel upload response:", r.text)
        r.raise_for_status()
        return r.json()

def main():
    trends = get_all_entertainment_trends()
    if not trends:
        return
    trend = random.choice(trends)
    
    img_path = create_reel_image(trend["title"], trend["country"])
    video_path = create_reel_video(img_path, trend["title"])
    
    desc = f"🔥 {trend['title']} is trending in {trend['country']}!\n\n#reels #trending #entertainment #viral #fyp #googletrends #usa #uk #canada"
    
    result = upload_reel(video_path, desc)
    print(f"Reel posted: {result}")

if __name__ == "__main__":
    main()
