from typing import List
from .models import BunkerGame, Player


def evaluate_bunker_survival(game: BunkerGame) -> str:
    """
    Bunkerga kirgan omon qolganlar tarkibini tahlil qilib,
    badiiy, qiziqarli va emotsional yakuniy hikoya tuzadi.
    """
    survivors: List[Player] = game.alive_players
    catastrophe = game.catastrophe
    years = catastrophe.duration_years if catastrophe else 3

    # Tahlil parametrlari
    has_medic = False
    has_farmer = False
    has_tech = False
    has_security = False
    has_fertile_male = False
    has_fertile_female = False
    critical_health_issues = []

    for p in survivors:
        card = p.card
        if not card:
            continue

        prof_lower = card.profession.lower()
        luggage_lower = card.luggage.lower()
        health_lower = card.health.lower()

        # Tibbiyot
        if any(w in prof_lower for w in ["jarroh", "stomatolog", "shifokor", "farmatsevt", "psixiatr"]) or "aptechka" in luggage_lower:
            has_medic = True

        # Qishloq xo'jaligi va oziq-ovqat
        if any(w in prof_lower for w in ["agrotexnik", "biolog", "oshpaz"]) or "urug'" in luggage_lower:
            has_farmer = True

        # Texnika va elektr
        if any(w in prof_lower for w in ["muhandis", "dasturlash", "chilangar", "geolog", "duradgor"]) or any(w in luggage_lower for w in ["quyosh paneli", "asbob-uskunalar"]):
            has_tech = True

        # Xavfsizlik va qurol
        if any(w in prof_lower for w in ["harbiy", "ovchi", "yong'in"]) or "to'pponcha" in luggage_lower:
            has_security = True

        # Nasl qoldirish
        if card.can_reproduce:
            if card.gender == "Erkak":
                has_fertile_male = True
            elif card.gender == "Ayol":
                has_fertile_female = True

        # Og'ir kasalliklar
        if "diabet" in health_lower or "yurak" in health_lower or "astma" in health_lower:
            critical_health_issues.append((p.full_name, card.health))

    # Omon qolish balli (Survival score)
    score = 30  # Asosiy baza
    log_stories = []

    # 1. Tibbiyot tekshiruvi
    if has_medic:
        score += 20
        log_stories.append("💊 <b>Tibbiyot:</b> Jamoada tibbiy bilimlar va dori-darmonlar yetarli bo'lgani sababli barcha ichki jarohat va infeksiyalar muvaffaqiyatli davolandi.")
    else:
        score -= 15
        log_stories.append("⚠️ <b>Tibbiyot xatosi:</b> Shifokor bo'lmagani sababli oddiy shamollash va tish og'rig'i ham dahshatli azobga aylandi.")

    # 2. Oziq-ovqat va ekinlar
    if has_farmer:
        score += 20
        log_stories.append("🌱 <b>Oziq-ovqat:</b> Bunker issiqxonasida yangi sabzavotlar va oziq-ovqatlar muntazam yetishtirildi. Ochlik xavfi bartaraf etildi.")
    else:
        score -= 20
        log_stories.append("🥫 <b>Ochlik:</b> Yangi ekinlar yetishtirishni hech kim bilmas edi. Konservalar tugagach, so'nggi yillarda qattiq ratsionga o'tildi.")

    # 3. Texnika va energiya
    if has_tech:
        score += 15
        log_stories.append("⚙️ <b>Energetika va Tizimlar:</b> Muhandislar generator va suv tozalagichdagi 3 ta xavfli avariyani o'z vaqtida tuzatib, bazani saqlab qolishdi.")
    else:
        score -= 15
        log_stories.append("⚡ <b>Tizim nosozligi:</b> Ventilyatsiya va elektr tizimidagi nosozliklar bir necha bor jamoani bo'g'ilib qolish yoqasiga olib keldi.")

    # 4. Xavfsizlik
    if has_security:
        score += 10
        log_stories.append("🛡️ <b>Xavfsizlik:</b> Tashqi eshikka hujum qilgan bosqinchilar va mutatsiyalar qurolli himoyachilar tomonidan qaytarildi.")
    else:
        log_stories.append("🚪 <b>Tinchlik:</b> Tashqi xavflar omadli tarzda bunker eshigini chetlab o'tdi.")

    # 5. Demografiya (Nasl davomiyligi)
    can_continue_civilization = has_fertile_male and has_fertile_female
    if can_continue_civilization:
        score += 15
        log_stories.append("👶 <b>Yangi Hayot:</b> Bunkerda sog'lom farzandlar dunyoga keldi! Insoniyat genofondi davom etishi ta'minlandi.")
    else:
        log_stories.append("🥀 <b>Genofond:</b> Afsuski, jamoada nasl qoldiruvchi muvozanat yo'qligi sababli yangi avlod tug'ilmadi.")

    score = max(10, min(100, score))

    # Yakuniy xulosa
    if score >= 75:
        verdict = "🏆 <b>MUVAFFAQIYATLI G'ALABA!</b>\nBunker aholisi falokatning barcha qiyinchiliklarini yengib o'tdi va yangi sivilizatsiyaga mustahkam tamal toshini qo'ydi!"
    elif score >= 50:
        verdict = "⚖️ <b>QALTIQI OMON QOLISH!</b>\nJamoa juda katta talafotlar, asabiy buzilishlar va mahrumliklar evaziga qiyinchilik bilan omon chiqdi."
    else:
        verdict = "💀 <b>FOJIALI YAKUN!</b>\nMuvozanatsiz tanlov oqibatida bunker ichki nizolar, ochlik va kasalliklar tufayli halokatga yuz tutdi."

    # Matnni yig'ish
    text = (
        f"═══════════════════════════\n"
        f"        🏰 <b>BUNKER EPILOGI ({years} YIL O'TIB)</b>\n"
        f"═══════════════════════════\n\n"
        f"📊 <b>Omon qolish indeksi:</b> {score}%\n\n"
        + "\n\n".join(log_stories) + "\n\n"
        f"───────────────────────────\n"
        f"{verdict}\n"
        f"───────────────────────────\n"
        f"O'yinda qatnashgan barcha ishtirokchilarga tashakkur! Yangi o'yin boshlash uchun /bunker bosing."
    )
    return text
