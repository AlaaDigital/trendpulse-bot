# TrendPulse Bot - مجاني 100% بدون VPS

بوت ينشر تلقائيا:
- بوست كل 30 دقيقة من ترند جوجل ترفيه أمريكا/كندا/بريطانيا
- 5 ريلزات في اليوم في أوقات الذروة

## كيف تركبه في 3 دقائق:

### 1. اعمل GitHub repo
- ادخل github.com -> New Repository -> اسم: trendpulse-bot -> Public
- ارفع كل الملفات اللي في هذا المجلد

### 2. زيد الـ Secrets
ادخل Settings -> Secrets and variables -> Actions -> New repository secret

- اسم: `FB_PAGE_ID` والقيمة: الـ ID اللي جبته من me/accounts
- اسم: `FB_PAGE_TOKEN` والقيمة: الـ Token اللي يبدأ بـ EAA...

### 3. فعل الـ Actions
ادخل تب Actions -> ستجد 2 workflows -> اضغط Enable

### 4. جرب الآن
ادخل Actions -> Post Trends Every 30 Minutes -> Run workflow -> Run

خلاص! البوت سيعمل وحده مجانا للأبد على خوادم GitHub.

## كيف تجيب Long-Lived Token (يعيش 60 يوم):
بدل الـ Token الحالي، اعمل هذا الرابط في المتصفح:
```
https://graph.facebook.com/v20.0/oauth/access_token?grant_type=fb_exchange_token&client_id=APP_ID&client_secret=APP_SECRET&fb_exchange_token=SHORT_TOKEN
```
APP_ID و APP_SECRET تجدهم في Dashboard -> App settings -> Basic

## ملاحظة أمان:
اذا نشرت Token في مكان عام، ادخل Graph API Explorer -> اضغط Delete بجانب Token واعمل واحد جديد.

