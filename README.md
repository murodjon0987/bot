# 🛡️ "BUNKER" Telegram O'yin Boti (Python 3.11+ / aiogram 3.x)

Telegram guruhlarida o'ynaladigan, 100% o'zbek tilidagi, psixologik, strategik va juda qiziqarli **"BUNKER" (Apokalipsisdan omon qolish)** o'yin boti.

---

## 🌟 Asosiy Xususiyatlari:

1. **Ma'lumotlar bazasisiz (0 MB Disk):**
   * SQLite, PostgreSQL yoki MySQL talab qilinmaydi.
   * Barcha o'yin ma'lumotlari Pythonning ichki xotirasida (In-Memory) saqlanadi va o'yin tugashi bilan darhol xotira tozalanadi (RAM sarfi atigi 20–30 MB).
2. **24/7 Bepul Xosting Mosligi (Render.com, Koyeb):**
   * Bot fonida `aiohttp` orqali `/health` va `/` web-serverini tinglaydi.
   * Render.com yoki Koyeb kabi platformalarda `Web Service` sifatida 24/7 o'chmasdan bepul ishlaydi. UptimeRobot orqali `/health` URL manzilini ping qilib turish kifoya.
3. **Cheksiz Parallel Guruhlar:**
   * Bir vaqtning o'zida yuzlab turli guruhlarda bir-biriga xalaqit bermasdan mustaqil o'yinlar o'ynaladi (`games[chat_id]`).
4. **Boy va Emotsional O'yin Mexanikasi:**
   * 5 xil global katastrofa (Yadro urushi, Virus, AI qo'zg'oloni, Global toshqin, Meteorit).
   * 20 dan ortiq kasblar va tajriba yillari.
   * Biologik ma'lumotlar, 12 xil salomatlik holati, o'ziga xos xarakterlar va 14 xil maxsus bagaj buyumlari.
   * 6 xil o'yinni o'zgartiruvchi Maxsus Kartalar (Bunker kengaytmasi, Shifo, Bagaj o'g'irlash, Ikki hissa ovoz, Muzlatish, Xaloskor immunitet).
   * O'yin oxirida bunkerga kirgan jamoaning kasblari, oziq-ovqati, dori-darmoni va nasl qoldirish qobiliyatini tahlil qiluvchi aqlli Badiiy Epilog Generator!

---

## 📁 Loyiha Strukturasi:

```text
mafia/
├── .env.example               # Muhit o'zgaruvchilari namunasi
├── requirements.txt           # Kutubxonalar ro'yxati
├── config.py                  # Konfiguratsiya sozlamalari
├── main.py                    # Kirish nuqtasi (aiogram + aiohttp web server)
├── README.md                  # Yo'riqnoma va dokumentatsiya
├── game/
│   ├── __init__.py
│   ├── models.py              # O'yinchi, Karta, Katastrofa dataclasslari
│   ├── scenarios.py           # O'zbekcha falokatlar, kasblar, anketalar
│   ├── manager.py             # In-memory guruh o'yinlari menejeri
│   └── evaluator.py           # Yakuniy omon qolish tahlili va epilog
├── handlers/
│   ├── __init__.py
│   ├── common.py              # /start, /help, /rules, /stop_game
│   ├── lobby.py               # /bunker, /game, ro'yxatga olish
│   └── game_flow.py           # Raundlar, ovoz berish, chetlatish, epilog
└── web/
    ├── __init__.py
    └── server.py              # 24/7 Uptime /health web-server
```

---

## 🚀 O'rnatish va Ishga Tushirish

### 1. Talablar
* Python 3.11 yoki undan yuqori versiya.

### 2. Kutubxonalarni o'rnatish
```bash
pip install -r requirements.txt
```

### 3. Konfiguratsiya (.env)
Loyihada `.env` faylini yarating va BotFather'dan olingan tokeningizni kiriting:
```env
BOT_TOKEN=123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ
PORT=8080
HOST=0.0.0.0
MIN_PLAYERS=4
LOBBY_TIMEOUT=60
DISCUSSION_TIMEOUT=60
VOTING_TIMEOUT=45
```

### 4. Botni ishga tushirish
```bash
python main.py
```
yoki Windows'da:
```powershell
py main.py
```

---

## ☁️ Render.com da 24/7 Bepul Xostingga Joylash

1. Loyihani o'z **GitHub** akkauntingizga yuklang (`git push origin main`).
2. [Render.com](https://render.com) saytiga kiring va **New +** -> **Web Service** ni tanlang.
3. GitHub repozitoriyangizni ulang.
4. Quyidagi parametrlarni o'rnating:
   * **Runtime:** `Python 3`
   * **Build Command:** `pip install -r requirements.txt`
   * **Start Command:** `python main.py`
   * **Instance Type:** `Free`
5. **Environment Variables** bo'limiga kiring:
   * `BOT_TOKEN`: Sizning bot tokeningiz
   * `PORT`: `10000` (Render avtomatik o'zi beradi)
6. **Deploy** tugmasini bosing!
7. Bot 24/7 doimiy ishlab turishi uchun [UptimeRobot.com](https://uptimerobot.com) saytiga kiring va Render sizga bergan havola orqali monitoring qo'ying:
   * URL: `https://sizning-ilova-nomingiz.onrender.com/health`
   * Monitoring turi: `HTTP(s)` (har 5 daqiqada ping).

---

## 🎮 O'yin Buyruqlari:

| Buyruq | Chat turi | Tavsif |
| :--- | :--- | :--- |
| `/start` | Shaxsiy / Guruh | Botni tanishtirish va shaxsiy xabarlarni ochish |
| `/bunker` yoki `/game` | Faqat guruh | Yangi Bunker o'yini uchun ro'yxatga olishni ochish |
| `/stop_game` | Faqat guruh | Faol o'yinni to'xtatish va xotirani tozalash |
| `/rules` | Har qanday | O'yin qoidalarini ko'rish |
| `/help` | Har qanday | Yordam xabarini ko'rsatish |
