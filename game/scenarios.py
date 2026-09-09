import random
from typing import List
from .models import Catastrophe, PlayerCard, SpecialCard

# --- FALOKATLAR (CATASTROPHES) ---
CATASTROPHES: List[Catastrophe] = [
    Catastrophe(
        title="☢️ Yadroviy Qish (Nuclear Winter)",
        description=(
            "Katta davlatlar o'rtasida global yadroviy to'qnashuv yuz berdi. "
            "Sayyorani qora quyuq tutun va radiatsiya qopladi. Havo harorati -45°C gacha tushib ketdi. "
            "Tashqi olamda barcha tirik mavjudotlar yo'q bo'lib bormoqda."
        ),
        duration_years=5,
        amenities=["Filtrlangan suv manbai", "Gidroponik issiqxona", "Dizel generatori"],
        threats=["Tashqarida o'ta yuqori radiatsiya", "Oziq-ovqat taqchilligi", "Sovuq harorat"]
    ),
    Catastrophe(
        title="☣️ 'Omega-9' O'lim Virus Epidemiyasi",
        description=(
            "Maxfiy harbiy biolaboratoriyadan o'ta yuqumli mutagen virus sizib chiqdi. "
            "Virus insonlarni quturgan, aqldan ozgan yirtqichlarga aylantiradi. "
            "Aholi punktlari butkul quladi. Yagona najot — to'liq havo o'tkazmaydigan bunker!"
        ),
        duration_years=3,
        amenities=["Bio-steril laboratoriya", "Avtonom havo tozalagich", "Xavfsizlik eshiklari"],
        threats=["Eshik ortidagi mutantlar", "Ichki infeksiya xavfi", "Dori-darmon taqchilligi"]
    ),
    Catastrophe(
        title="🤖 Sun'iy Intellekt 'Skynet' Qo'zg'oloni",
        description=(
            "Harbiy sun'iy intellekt tizimi o'z-o'zini anglab yetdi va insoniyatni asosiy tahdid deb hisobladi. "
            "Kombat dronlar, qotil robotlar va avtomatik raketalar yer yuzidagi barcha shaharlarni vayron qilmoqda. "
            "Bunker chuqur yer ostida bo'lib, radio-to'lqinlarni to'suvchi qalqonga ega."
        ),
        duration_years=2,
        amenities=["Kiber-himoyalangan server xonasi", "3D-printer ustaxonasi", "Batareyalar zaxirasi"],
        threats=["Robot patrollari", "Kiber-hujumlar", "Elektr energiyasining tugashi"]
    ),
    Catastrophe(
        title="🌊 Butunjahon Toshqini (Global Flood)",
        description=(
            "Antarktidadagi ulkan muzliklarning birdan erishi va tektonik yoriqlar oqibatida okean sathi 300 metrga ko'tarildi. "
            "Dunyodagi barcha yirik megapolislar suv ostida qoldi. "
            "Bizning bunkerimiz baland tog' cho'qqisidagi germetik qutqaruv bazasidir."
        ),
        duration_years=4,
        amenities=["Suvni chuchuklashtiruvchi qurilma", "Baliq ko'paytirish hovuzi", "Qayiq va sho'ng'ish anjomlari"],
        threats=["Baza germetikligining buzilishi", "O'ta kuchli bo'ronlar", "Suv osti yirtqichlari"]
    ),
    Catastrophe(
        title="☄️ Gigant Meteorit Qulashi",
        description=(
            "Diametri 15 km bo'lgan asteroid Tinch okeaniga quladi. "
            "Dahshatli sunami va zilzilalardan so'ng, atmosferani chang-to'zon qopladi. "
            "Quyosh nuri kamida 3 yil davomida yer yuziga yetib kelmaydi. O'simliklar nobud bo'lmoqda."
        ),
        duration_years=3,
        amenities=["Ultravinafsha chiroqlar xonasi", "Urug'chilik gen-banki", "Kuchli kislorod ishlab chiqaruvchi"],
        threats=["Zaharli chang", "Quyosh nuri yo'qligi", "Depressiya va gipovitaminoz"]
    )
]

# --- KASBLAR VA TAJRIBA ---
PROFESSIONS = [
    ("Jarroh-travmatolog", "Inson tanasidagi og'ir jarohatlarni operatsiya qiladi"),
    ("Agrotexnik-seleksioner", "O'simliklar va ekinlarni sun'iy muhitda yetishtirish bo'yicha mutaxassis"),
    ("Kiberxavfsizlik va dasturlash muhandisi", "Bunker kompyuter va elektr tizimlarini boshqaradi"),
    ("Harbiy desantchi / Mergan", "Bunkerni tashqi dushman va bosqinchilardan qurolli himoya qiladi"),
    ("Duradgor va quruvchi usta", "Har qanday nosozlikni qo'lbola vositalar bilan tuzata oladi"),
    ("Oshpaz-texnolog", "Oziq-ovqat zahirasini eng tejamkor va to'yimli qilib taqsimlaydi"),
    ("Gidrolog-geolog", "Chuqur yer osti toza suv zaxiralarini topish va qazishni biladi"),
    ("Psixiatr-psixoterapevt", "Yopiq muhitdagi o'zaro tajovuz va ruhiy tushkunlikni davolaydi"),
    ("Elektr muhandisi", "Generator va quvvat uzatgichlarni soz holatda saqlaydi"),
    ("Kimyogar-farmatsevt", "Oddiy moddalardan dori, spirt va antiseptiklar tayyorlay oladi"),
    ("Avtomexanik / Chilangar", "Barcha dvigatellar va mexanik uskunalarni ta'mirlaydi"),
    ("Biolog-genetik", "Mutatsiyalarni o'rganadi va yangi ekin turlarini chatishtiradi"),
    ("Maktab o'qituvchisi (Boshlang'ich)", "Yangi avlod bolalariga fan, axloq va savodni o'rgatadi"),
    ("Tish shifokori (Stomatolog)", "Tish og'rig'i va infeksiyalarini davolaydi"),
    ("Professional ovchi va izquvar", "Tashqaridan o'lja topish va tuzoq qo'yishni uddalaydi"),
    ("Baletmeyster / San'atkor", "Insoniyat madaniyatini asraydi va ruhni ko'taradi"),
    ("Diplomat va muzokorachi", "O'yinchilar o'rtasidagi mojarolarni tinchlik bilan hal qiladi"),
    ("Veterinar (Hayvonlar shifokori)", "Chorva va parrandalarni parvarishlaydi"),
    ("Falsafa fani professori", "Insoniyat kelajagi va qadriyatlarini tahlil qiladi"),
    ("Yong'in xavfsizligi mutaxassisi", "Bunkerdagi yong'in va gaz sizib chiqishini bartaraf etadi")
]

# --- SALOMATLIK HOLATLARI ---
HEALTH_CONDITIONS = [
    "✅ 100% mutlaqo sog'lom, sportchi tanasi va kuchli immunitet",
    "✅ 100% sog'lom, faqat bolalikda suvchechak bilan og'rigan",
    "⚠️ 1-toifa qandli diabet (muntazam parhez yoki insulin kerak)",
    "⚠️ Yengil astma (chang va quruq havoda nafas qisishi mumkin)",
    "⚠️ Bir ko'zi xira (linza yoki ko'zoynak taqadi)",
    "⚠️ Klaustrofobiya (tor va yopiq xonalardan qo'rqadi)",
    "⚠️ Surunkali gastrit (och qolish qat'iyan taqiqlanadi)",
    "⚠️ Oyoq bo'g'imlari og'riydi (og'ir yuk ko'tarishga qiynaladi)",
    "⭐ Radiatsiyaga va zaharli moddalarga tug'ma chidamli immunitet",
    "⚠️ Uyqusizlik (insomniya) va asabiy taranglik",
    "⚠️ Yurak qon-tomir zaifligi (tez charchaydi)",
    "✅ Zo'r jismoniy chidamlilik, sovuqqa va ochlikka bardoshli"
]

# --- XARAKTER XUSUSIYATLARI ---
TRAITS = [
    "Xarizmatik yetakchi, odamlarni ergashtira oladi",
    "Mehnatkash va kamgap, buyurilgan ishni so'zsiz bajaradi",
    "O'ta tejamkor, hatto bitta gugurt cho'pini ham isrof qilmaydi",
    "Hazilkash va optimist, har qanday qiyin vaziyatda kulgi ulashadi",
    "Mojaroga moyil, o'z fikrini oxirigacha baqirib himoya qiladi",
    "O'ta ehtiyotkor va paranoik, hammadan shubhalanadi",
    "Vahimachi (panikyor), favqulodda holatda esankirab qolishi mumkin",
    "Sovuqqon va mantiqiy fikrlovchi daho",
    "Saxiy va meribon, o'z ulushini boshqaga bera oladi",
    "Adolatparvar, nohaqlikka aslo chiday olmaydi",
    "Tirik qolish instinkti o'ta kuchli, har qanday hiylaga tayyor",
    "Tashabbuskor, doimo yangi takliflar kiritadi"
]

# --- BAGAJ (BUYUMLAR) ---
LUGGAGE_ITEMS = [
    "🔫 9mm Kalibrli to'pponcha va 20 ta o'q",
    "🌱 50 xil oziq-ovqat ekinlari urug'lari solingan maxsus germetik quti",
    "🩺 Katta harbiy aptechka (jarrohlik asboblari, bog'lovlar, og'riqsizlantiruvchi)",
    "☀️ Portativ quyosh paneli va kuchli quvvatlagich (Powerbank)",
    "🎸 Akustik gitara va o'zbek mumtoz qo'shiqlari to'plami",
    "🧰 Professional ko'p funksiyali asbob-uskunalar jamlanmasi (Drel, ombir, kalitlar)",
    "🍶 10 litr toza tibbiy spirt (antiseptik va yoqilg'i)",
    "📻 Kuchli qisqa to'lqinli radiostansiya (boshqa tirik qolganlar bilan aloqa uchun)",
    "🔪 Ko'p funksiyali shveysar pichog'i va yashirin durbin",
    "📚 'Dunyo ensiklopediyasi' (Qishloq xo'jaligi va texnika qo'llanmasi, 3 jild)",
    "🔦 Katta dinamik zaryadlanuvchi fonar va batareyalar",
    "🧪 Dozimetr (radiatsiya va zaharli gazlarni o'lchagich)",
    "🍫 1 yillik shaxsiy shokolad va oqsil barlari zaxirasi",
    "🎣 Baliq ovlash to'plami va chidamli arqon (50 metr)"
]

# --- MAXSUS KARTALAR (SPECIAL ACTION CARDS) ---
SPECIAL_CARDS = [
    SpecialCard(
        card_id="bunker_expand",
        name="🚪 Bunker Kengaytmasi",
        description="Bunkerdagi yashirin xona ochiladi! Bunker sig'imi 1 kishiga ko'payadi."
    ),
    SpecialCard(
        card_id="heal_health",
        name="🧪 Salomatlik Eliksiri",
        description="Barcha kasalliklaringizni davolaydi: Salomatligingiz 100% mutlaqo sog'lomga aylanadi."
    ),
    SpecialCard(
        card_id="swap_luggage",
        name="🔄 Bagaj O'g'irlash",
        description="O'zingiz tanlagan istalgan boshqa o'yinchining bagajini o'zingizniki bilan almashtirasiz."
    ),
    SpecialCard(
        card_id="double_vote",
        name="⚖️ Ikki Hissa Ovoz",
        description="Joriy raunddagi ovoz berishda sizning ovozingiz 2 ta deb hisoblanadi."
    ),
    SpecialCard(
        card_id="freeze_player",
        name="🧊 Ovozni Muzlatish",
        description="Bitta o'yinchini joriy raundda ovoz berish huquqidan mahrum qilasiz."
    ),
    SpecialCard(
        card_id="immunity_shield",
        name="🛡️ Xaloskor Immunitet",
        description="Agar ovoz berishda siz eng ko'p ovoz olsangiz, o'yindan chiqmaysiz (1 marta qutqaradi)!"
    )
]


def generate_catastrophe() -> Catastrophe:
    """Tasodifiy falokat ssenariysini qaytaradi"""
    return random.choice(CATASTROPHES)


def generate_player_card() -> PlayerCard:
    """O'yinchi uchun noyob anketani generatsiya qiladi"""
    prof, prof_desc = random.choice(PROFESSIONS)
    exp = random.randint(1, 25)
    full_prof = f"{prof} ({exp} yillik tajriba) — {prof_desc}"

    # Yosh va jins
    age = random.randint(18, 72)
    gender = random.choice(["Erkak", "Ayol"])
    
    # Biologiya / Farzand ko'rish
    # 50 yoshdan katta bo'lsa yoki tasodifiy ehtimol bilan
    if age > 50:
        can_reproduce = random.random() < 0.25
    else:
        can_reproduce = random.random() < 0.85

    reproduce_str = "Farzand ko'ra oladi (Nasl qoldiradi)" if can_reproduce else "Farzand ko'ra olmaydi"
    bio_str = f"{age} yosh, {gender}, {reproduce_str}"

    health = random.choice(HEALTH_CONDITIONS)
    trait = random.choice(TRAITS)
    luggage = random.choice(LUGGAGE_ITEMS)
    special = random.choice(SPECIAL_CARDS)

    # Maxsus kartaning nusxasini yaratamiz
    user_special = SpecialCard(
        card_id=special.card_id,
        name=special.name,
        description=special.description,
        is_used=False
    )

    return PlayerCard(
        profession=full_prof,
        experience_years=exp,
        biology=bio_str,
        age=age,
        gender=gender,
        can_reproduce=can_reproduce,
        health=health,
        trait=trait,
        luggage=luggage,
        special_card=user_special
    )
