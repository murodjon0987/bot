import asyncio
import random
from typing import Dict, List
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest

from game.manager import game_manager
from game.models import BunkerGame, Player, GamePhase
from game.scenarios import generate_catastrophe, generate_player_card
from game.evaluator import evaluate_bunker_survival
import config

router = Router()


# --- PMDA O'YINCHIGA DOSYENI YUBORISH ---
async def send_player_dossier_pm(player: Player, game: BunkerGame, bot: Bot):
    card = player.card
    if not card:
        return

    text = (
        f"🏰 <b>BUNKER: SIZNING MAXFIY ANKETANGIZ</b>\n"
        f"Guruh: <b>{game.chat_title}</b>\n\n"
        f"📇 <b>Kasbingiz:</b> {card.profession}\n"
        f"🧬 <b>Biologiyangiz:</b> {card.biology}\n"
        f"🩺 <b>Salomatligingiz:</b> {card.health}\n"
        f"🧠 <b>Xarakteringiz:</b> {card.trait}\n"
        f"🎒 <b>Bagajingiz:</b> {card.luggage}\n\n"
        f"🃏 <b>Maxsus Kartangiz:</b>\n"
        f"<b>{card.special_card.name}</b> — <i>{card.special_card.description}</i>\n\n"
        f"⚠️ <i>Ushbu ma'lumotlarni guruhdagi bahsda o'zingizni himoya qilish uchun ishlating!</i>"
    )

    kb = None
    if not card.special_card.is_used:
        kb = InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(
                text=f"✨ {card.special_card.name}ni ishlatish",
                callback_data=f"use_special:{game.chat_id}"
            )
        ]])

    try:
        await bot.send_message(player.user_id, text, reply_markup=kb, parse_mode="HTML")
    except (TelegramForbiddenError, TelegramBadRequest):
        # Foydalanuvchi botni bloklagan yoki /start bosmagan
        try:
            await bot.send_message(
                game.chat_id,
                f"⚠️ {player.mention}, siz botga shaxsiyda /start bosmagansiz! "
                f"Iltimos, anketangizni ko'rish uchun botga kiring.",
                parse_mode="HTML"
            )
        except Exception:
            pass


# --- O'YINNI BOSHLASH ---
async def start_bunker_game(chat_id: int, bot: Bot):
    game = game_manager.get_game(chat_id)
    if not game:
        return

    if len(game.players) < config.MIN_PLAYERS:
        await bot.send_message(
            chat_id,
            f"❌ <b>O'yin boshlanmadi!</b>\n"
            f"Yetarlicha o'yinchi to'planmadi (kamida {config.MIN_PLAYERS} kishi kerak edi, "
            f"ro'yxatdan o'tganlar: {len(game.players)} ta).\n"
            f"Yangi o'yin uchun /bunker buyrug'ini bering.",
            parse_mode="HTML"
        )
        game_manager.remove_game(chat_id)
        return

    game.phase = GamePhase.STARTING
    game.catastrophe = generate_catastrophe()
    
    # Bunker sig'imi: jami o'yinchilarning yarmi (kamida 2 kishi)
    total_count = len(game.players)
    game.bunker_capacity = max(2, total_count // 2)

    # Har bir o'yinchiga noyob karta beramiz
    for player in game.players.values():
        player.card = generate_player_card()
        player.is_alive = True
        player.can_vote = True
        player.has_immunity = False
        player.extra_votes = 0

    # Shaxsiy xabarlarda anketalarni jo'natish
    for player in game.players.values():
        await send_player_dossier_pm(player, game, bot)

    cat = game.catastrophe
    amenities_str = "\n".join([f"  • {a}" for a in cat.amenities])
    threats_str = "\n".join([f"  • {t}" for t in cat.threats])

    intro_text = (
        f"🚨 <b>GLOBAL FALOKAT YUZ BERDI!</b>\n"
        f"═══════════════════════════\n"
        f"<b>{cat.title}</b>\n\n"
        f"{cat.description}\n\n"
        f"⏳ <b>Bunkerda yashash muddati:</b> {cat.duration_years} yil\n"
        f"👥 <b>Jami da'vogarlar:</b> {total_count} kishi\n"
        f"🏰 <b>Bunkerdagi joylar soni:</b> {game.bunker_capacity} ta!\n"
        f"⚠️ <b>Chetlatilishi kerak bo'lganlar:</b> {total_count - game.bunker_capacity} kishi!\n\n"
        f"🏢 <b>Bunker sharoitlari:</b>\n{amenities_str}\n\n"
        f"☠️ <b>Tashqi tahdidlar:</b>\n{threats_str}\n"
        f"═══════════════════════════\n"
        f"<i>Barcha o'yinchilarga shaxsiy anketalar yuborildi! 5 soniyadan so'ng 1-raund boshlanadi...</i>"
    )

    await bot.send_message(chat_id, intro_text, parse_mode="HTML")
    await asyncio.sleep(5)

    # Raundlar siklini boshlaymiz
    game.timer_task = asyncio.create_task(run_game_loop(chat_id, bot))


# --- RAUNDLAR SIKLI (GAME LOOP) ---
async def run_game_loop(chat_id: int, bot: Bot):
    try:
        while True:
            game = game_manager.get_game(chat_id)
            if not game:
                return

            # G'alaba sharti tekshiruvi: Tiriklar soni bunker sig'imiga teng yoki kam bo'lsa
            if game.alive_count <= game.bunker_capacity:
                await finish_bunker_game(chat_id, bot)
                return

            # 1. KARTA OCHISH BOSQICHI
            game.phase = GamePhase.CARD_REVEAL
            reveal_key = get_reveal_key_for_round(game.round_number)
            reveal_title = get_reveal_title(reveal_key)

            # Tirik o'yinchilarning ushbu xususiyatini ochamiz
            for p in game.alive_players:
                if p.card:
                    p.card.revealed[reveal_key] = True

            cards_overview = format_revealed_cards(game, reveal_title)
            await bot.send_message(chat_id, cards_overview, parse_mode="HTML")
            await asyncio.sleep(3)

            # 2. MUHOKAMA BOSQICHI (DISCUSSION)
            game.phase = GamePhase.DISCUSSION
            disc_text = (
                f"🗣️ <b>{game.round_number}-RAUND: MUHOKAMA VAQTI!</b>\n\n"
                f"⏱️ Sizda <b>{config.DISCUSSION_TIMEOUT} soniya</b> bor!\n"
                f"Guruhda faol bahslashishni boshlang: Kim bunkerda qolishga loyiq, "
                f"kim esa tashqariga chiqarib yuborilishi kerak?\n\n"
                f"<i>Muhokama tugagach ovoz berish boshlanadi!</i>"
            )
            await bot.send_message(chat_id, disc_text, parse_mode="HTML")
            await asyncio.sleep(config.DISCUSSION_TIMEOUT)

            # 3. OVOZ BERISH BOSQICHI (VOTING)
            game = game_manager.get_game(chat_id)
            if not game or game.phase == GamePhase.FINISHED:
                return

            game.phase = GamePhase.VOTING
            game.votes.clear()
            for p in game.players.values():
                p.votes_received = 0

            vote_kb = build_voting_keyboard(game)
            vote_msg = await bot.send_message(
                chat_id,
                format_voting_text(game, config.VOTING_TIMEOUT),
                reply_markup=vote_kb,
                parse_mode="HTML"
            )
            game.current_message_id = vote_msg.message_id

            # Ovoz berish taymeri
            vote_time = config.VOTING_TIMEOUT
            while vote_time > 0:
                await asyncio.sleep(5)
                vote_time -= 5
                
                # Agar hamma tirik o'yinchilar ovoz berib bo'lgan bo'lsa
                eligible_voters = [p for p in game.alive_players if p.can_vote]
                if len(game.votes) >= len(eligible_voters):
                    break

                try:
                    await bot.edit_message_text(
                        chat_id=chat_id,
                        message_id=game.current_message_id,
                        text=format_voting_text(game, max(0, vote_time)),
                        reply_markup=build_voting_keyboard(game),
                        parse_mode="HTML"
                    )
                except Exception:
                    pass

            # 4. OVOZLARNI HISOBLASH VA CHETLATISH
            await process_elimination(chat_id, bot)
            await asyncio.sleep(4)

            game.round_number += 1

    except asyncio.CancelledError:
        pass
    except Exception as e:
        import logging
        logging.error(f"Game loop xatosi: {e}")


def get_reveal_key_for_round(round_num: int) -> str:
    if round_num == 1:
        return "profession"
    elif round_num == 2:
        return "biology"
    elif round_num == 3:
        return "health"
    elif round_num == 4:
        return "luggage"
    else:
        return "trait"


def get_reveal_title(key: str) -> str:
    titles = {
        "profession": "📇 KASB VA TAJRIBA",
        "biology": "🧬 BIOLOGIYA VA YOSH",
        "health": "🩺 SALOMATLIK HOLATI",
        "luggage": "🎒 BAGAJ VA BUYUMLAR",
        "trait": "🧠 XARAKTER XUSUSIYATI"
    }
    return titles.get(key, "KARTA")


def format_revealed_cards(game: BunkerGame, current_feature_title: str) -> str:
    text = (
        f"📢 <b>{game.round_number}-RAUND: KARTALAR OCHILDI!</b>\n"
        f"🎯 Ushbu raundda ochilgan karta: <b>{current_feature_title}</b>\n"
        f"───────────────────────────\n\n"
    )
    for idx, p in enumerate(game.alive_players, 1):
        card = p.card
        if not card:
            continue
        text += f"<b>{idx}. {p.full_name}:</b>\n"
        if card.revealed.get("profession"):
            text += f"  • 📇 Kasbi: {card.profession}\n"
        if card.revealed.get("biology"):
            text += f"  • 🧬 Biologiyasi: {card.biology}\n"
        if card.revealed.get("health"):
            text += f"  • 🩺 Salomatligi: {card.health}\n"
        if card.revealed.get("luggage"):
            text += f"  • 🎒 Bagaji: {card.luggage}\n"
        if card.revealed.get("trait"):
            text += f"  • 🧠 Xarakteri: {card.trait}\n"
        text += "\n"


    text += (
        f"🏰 Bunkerdagi bo'sh joylar: <b>{game.bunker_capacity} ta</b> | "
        f"Tirik da'vogarlar: <b>{game.alive_count} ta</b>"
    )
    return text


def build_voting_keyboard(game: BunkerGame) -> InlineKeyboardMarkup:
    buttons = []
    # Har bir tirik o'yinchi uchun bittadan tugma
    row = []
    for p in game.alive_players:
        vote_count = sum(
            game.players[voter_id].extra_votes + 1 
            for voter_id, target_id in game.votes.items() 
            if target_id == p.user_id
        )
        btn_text = f"🗳️ {p.full_name}"
        if vote_count > 0:
            btn_text += f" ({vote_count})"
            
        row.append(InlineKeyboardButton(text=btn_text, callback_data=f"vote:{p.user_id}"))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def format_voting_text(game: BunkerGame, time_left: int) -> str:
    eligible = len([p for p in game.alive_players if p.can_vote])
    voted_count = len(game.votes)
    return (
        f"🗳️ <b>OVOZ BERISH BOSQICHI!</b>\n"
        f"Qaysi o'yinchini bunker eshigidan tashqariga haydaymiz?\n\n"
        f"📊 <b>Ovoz berganlar:</b> {voted_count}/{eligible}\n"
        f"⏱️ <b>Qolgan vaqt:</b> {time_left} soniya\n\n"
        f"<i>O'zingizga ovoz bera olmaysiz. Haydamoqchi bo'lgan shaxsingiz ustiga bosing:</i>"
    )


# --- OVOZ BERISH CALLBACKI ---
@router.callback_query(F.data.startswith("vote:"))
async def cq_vote(query: CallbackQuery, bot: Bot):
    if not query.message or not query.data:
        return

    chat_id = query.message.chat.id
    game = game_manager.get_game(chat_id)
    if not game or game.phase != GamePhase.VOTING:
        await query.answer("Ovoz berish bosqichi yakunlangan.", show_alert=True)
        return

    voter_id = query.from_user.id
    voter = game.players.get(voter_id)
    if not voter or not voter.is_alive:
        await query.answer("Siz ushbu o'yinda tirik emassiz, ovoz bera olmaysiz.", show_alert=True)
        return

    if not voter.can_vote:
        await query.answer("Siz ushbu raundda maxsus karta sababli ovoz berishdan mahrum qilingansiz!", show_alert=True)
        return

    target_id = int(query.data.split(":")[1])
    if voter_id == target_id:
        await query.answer("O'zingizga qarshi ovoz bera olmaysiz!", show_alert=True)
        return

    target = game.players.get(target_id)
    if not target or not target.is_alive:
        await query.answer("Ushbu o'yinchi tirik emas.", show_alert=True)
        return

    # Ovozni saqlaymiz
    game.votes[voter_id] = target_id
    await query.answer(f"Siz {target.full_name}ga qarshi ovoz berdingiz!")

    # Tugmalarni darhol yangilaymiz
    if isinstance(query.message, Message):
        try:
            await query.message.edit_reply_markup(reply_markup=build_voting_keyboard(game))
        except Exception:
            pass



# --- CHETLATISH JARAYONI ---
async def process_elimination(chat_id: int, bot: Bot):
    game = game_manager.get_game(chat_id)
    if not game:
        return

    game.phase = GamePhase.ROUND_END

    # Ovozlar to'plami
    tally: Dict[int, int] = {}
    for voter_id, target_id in game.votes.items():
        voter = game.players.get(voter_id)
        weight = 1 + (voter.extra_votes if voter else 0)
        tally[target_id] = tally.get(target_id, 0) + weight

    if not tally:
        # Hech kim ovoz bermagan bo'lsa, tasodifiy bittasi
        victim = random.choice(game.alive_players)
        elim_reason = "Hech kim ovoz bermagani sababli, taqdir taqozosi (tasodif)"
    else:
        # Eng ko'p ovoz olgan o'yinchi
        max_votes = max(tally.values())
        candidates = [uid for uid, v in tally.items() if v == max_votes]
        victim_id = random.choice(candidates)
        victim = game.players[victim_id]
        elim_reason = f"{max_votes} ta ovoz bilan ko'pchilikning qarori"

    # Xaloskor immunitet kartasini tekshirish
    if victim.has_immunity:
        victim.has_immunity = False
        imm_text = (
            f"🛡️ <b>XALOSKOR IMMUNITET ISHGA TUSHDI!</b>\n\n"
            f"{victim.mention} eng ko'p ovoz to'plagan edi, biroq u o'zining "
            f"<b>'Xaloskor Immunitet'</b> maxsus kartasini qo'llaganligi sababli "
            f"ushbu raundda omon qoldi va bunkerda qoldi!\n"
            f"Hech kim o'yindan chiqarilmadi."
        )
        await bot.send_message(chat_id, imm_text, parse_mode="HTML")
    else:
        victim.is_alive = False
        game.eliminated_players.append(victim)

        # Qolgan barcha yashirin kartalarini fosh etamiz
        card = victim.card
        card_prof = card.profession if card else "Noma'lum"
        card_bio = card.biology if card else "Noma'lum"
        card_health = card.health if card else "Noma'lum"
        card_trait = card.trait if card else "Noma'lum"
        card_luggage = card.luggage if card else "Noma'lum"
        card_spec = card.special_card.name if card else "Noma'lum"

        elim_text = (
            f"🚪 <b>BUNKER ESHIGI YOPILDI! O'YINCHI HAYDALDI!</b>\n"
            f"═══════════════════════════\n"
            f"👤 <b>Haydalgan o'yinchi:</b> {victim.mention}\n"
            f"⚖️ <b>Sabab:</b> {elim_reason}\n\n"
            f"<i>U tashqarida muzlab / radiatsiyadan halok bo'ldi! Uning to'liq anketasi:</i>\n"
            f"• 📇 Kasbi: {card_prof}\n"
            f"• 🧬 Biologiyasi: {card_bio}\n"
            f"• 🩺 Salomatligi: {card_health}\n"
            f"• 🧠 Xarakteri: {card_trait}\n"
            f"• 🎒 Bagaji: {card_luggage}\n"
            f"• 🃏 Maxsus kartasi: {card_spec}\n"
            f"═══════════════════════════\n"
            f"🏰 Bunkerdagi qolgan tiriklar: <b>{game.alive_count} ta</b>\n"
            f"Kerakli son: <b>{game.bunker_capacity} ta</b>"
        )
        await bot.send_message(chat_id, elim_text, parse_mode="HTML")


    # Vaqtinchalik bufflarni tozalaymiz
    for p in game.players.values():
        p.extra_votes = 0
        p.can_vote = True


# --- MAXSUS KARTANI ISHLATISH (SPECIAL ACTION CARD) ---
@router.callback_query(F.data.startswith("use_special:"))
async def cq_use_special(query: CallbackQuery, bot: Bot):
    if not query.message or not query.data:
        return

    chat_id = int(query.data.split(":")[1])
    game = game_manager.get_game(chat_id)
    if not game or game.phase == GamePhase.FINISHED:
        await query.answer("O'yin yakunlangan yoki topilmadi.", show_alert=True)
        return


    user_id = query.from_user.id
    player = game.players.get(user_id)
    if not player or not player.is_alive or not player.card:
        await query.answer("Siz tirik emassiz yoki o'yinda emassiz.", show_alert=True)
        return

    card = player.card
    spec = card.special_card
    if spec.is_used:
        await query.answer("Siz ushbu maxsus kartangizdan allaqachon foydalangansiz!", show_alert=True)
        return

    spec.is_used = True
    announcement = ""

    if spec.card_id == "bunker_expand":
        game.bunker_capacity += 1
        announcement = (
            f"🚪 <b>MAXSUS KARTA: BUNKER KENGAYTIRILDI!</b>\n"
            f"{player.mention} yashirin xonani topdi! "
            f"Bunker sig'imi <b>+1 kishiga oshdi</b> (Endi: {game.bunker_capacity} ta odam qutqariladi)!"
        )
    elif spec.card_id == "heal_health":
        card.health = "✅ 100% mutlaqo sog'lom, mukammal immunitet va chidamlilik (Dori orqali shifo topdi)"
        announcement = (
            f"🧪 <b>MAXSUS KARTA: SALOMATLIK ELIKSIRI!</b>\n"
            f"{player.mention} shifobaxsh zardob ichdi va barcha kasalliklaridan butkul forig' bo'ldi!"
        )
    elif spec.card_id == "double_vote":
        player.extra_votes = 1
        announcement = (
            f"⚖️ <b>MAXSUS KARTA: IKKI HISSA OVOZ!</b>\n"
            f"{player.mention} joriy ovoz berishda <b>2 ta ovoz</b> huquqiga ega bo'ldi!"
        )
    elif spec.card_id == "immunity_shield":
        player.has_immunity = True
        announcement = (
            f"🛡️ <b>MAXSUS KARTA: XALOSKOR IMMUNITET!</b>\n"
            f"{player.mention} xaloskor qalqonni faollashtirdi! "
            f"Agar u navbatdagi ovoz berishda haydalsa, qalqon uni qutqaradi!"
        )
    elif spec.card_id == "swap_luggage":
        # Boshqa tirik o'yinchilar bilan almashtirish
        other_players = [p for p in game.alive_players if p.user_id != user_id and p.card is not None]
        if other_players:
            target = random.choice(other_players)
            target_card = target.card
            if target_card:
                my_luggage = card.luggage
                card.luggage = target_card.luggage
                target_card.luggage = my_luggage
                announcement = (
                    f"🔄 <b>MAXSUS KARTA: BAGAJ O'G'IRLASH!</b>\n"
                    f"{player.mention} yashirincha {target.mention} bilan bagajini almashtirib oldi!\n"
                    f"{player.full_name} yangi bagaji: {card.luggage}"
                )
            else:
                announcement = f"🔄 {player.mention} bagaj almashtirish kartasini ishlatdi."
        else:
            announcement = f"🔄 {player.mention} bagaj almashtirish kartasini ishlatdi, biroq boshqa hech kim yo'q."

    elif spec.card_id == "freeze_player":
        other_players = [p for p in game.alive_players if p.user_id != user_id]
        if other_players:
            target = random.choice(other_players)
            target.can_vote = False
            announcement = (
                f"🧊 <b>MAXSUS KARTA: OVOZNI MUZLATISH!</b>\n"
                f"{player.mention} {target.mention}ni ushbu raundda ovoz berish huquqidan mahrum qildi!"
            )
        else:
            announcement = f"🧊 {player.mention} ovoz muzlatish kartasini qo'lladi."

    await query.answer("Maxsus kartangiz muvaffaqiyatli ishlatildi! ✨")
    
    # Guruhga e'lon qilamiz
    if announcement:
        try:
            await bot.send_message(chat_id, announcement, parse_mode="HTML")
        except Exception:
            pass

    # PMdagi xabarni yangilash (tugmani olib tashlash)
    if isinstance(query.message, Message):
        try:
            await query.message.edit_reply_markup(reply_markup=None)
        except Exception:
            pass



# --- O'YINNI YAKUNLASH VA EPILOG ---
async def finish_bunker_game(chat_id: int, bot: Bot):
    game = game_manager.get_game(chat_id)
    if not game:
        return

    game.phase = GamePhase.FINISHED
    game.cancel_timer()

    # Omon qolganlar ro'yxati
    survivors_list = ""
    for idx, p in enumerate(game.alive_players, 1):
        prof = p.card.profession if p.card else "Noma'lum"
        survivors_list += f"<b>{idx}. {p.mention}</b> — 📇 {prof}\n"


    final_overview = (
        f"🏆 <b>BUNKER TO'LDI! QUTQARILGANLAR ANIQLANDI!</b>\n"
        f"═══════════════════════════\n"
        f"Bunker eshiklari mahkam tambalandi. Tashqaridagi falokat ortda qoldi.\n\n"
        f"👥 <b>Bunkerga kirgan qahramonlar:</b>\n"
        f"{survivors_list}\n"
        f"<i>Keling, endi ushbu jamoaning birgalikda omon qolish qobiliyatini tahlil qilamiz...</i>"
    )
    await bot.send_message(chat_id, final_overview, parse_mode="HTML")
    await asyncio.sleep(4)

    # Epilog hikoyasini chiqaramiz
    epilogue_text = evaluate_bunker_survival(game)
    await bot.send_message(chat_id, epilogue_text, parse_mode="HTML")

    # Xotirani to'liq tozalaymiz (0 MB DB)
    game_manager.remove_game(chat_id)
