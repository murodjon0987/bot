import asyncio
from typing import Optional
from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.enums import ChatType
from game.manager import game_manager
from game.models import GamePhase
import config

router = Router()


def build_lobby_keyboard(bot_username: Optional[str]) -> InlineKeyboardMarkup:
    uname = bot_username or "bunker_game_bot"
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🛡️ Bunkerga kirish ➕", callback_data="lobby_join"),
            InlineKeyboardButton(text="🚪 Chiqish", callback_data="lobby_leave")
        ],
        [
            InlineKeyboardButton(text="🚀 Darhol boshlash", callback_data="lobby_start"),
            InlineKeyboardButton(text="💬 Botga /start (PM)", url=f"https://t.me/{uname}?start=join")
        ]
    ])


def format_lobby_text(game, remaining_time: int) -> str:
    players_list = ""
    for idx, p in enumerate(game.players.values(), 1):
        players_list += f"{idx}. {p.mention}\n"

    if not players_list:
        players_list = "<i>Hozircha hech kim ro'yxatdan o'tmadi.</i>\n"

    return (
        f"🚨 <b>DIQQAT! DUNYO HALOKAT YOQASIDA!</b>\n\n"
        f"Sayyorada global falokat yuz berdi. Yashirin <b>BUNKER</b> eshiklari ochildi!\n"
        f"Bunkerga faqat eng munosib va foydali insonlar qabul qilinadi!\n\n"
        f"👥 <b>Bunkerga da'vogarlar ({len(game.players)}/{config.MIN_PLAYERS}+):</b>\n"
        f"{players_list}\n"
        f"⏱️ <b>Qabul tugashiga:</b> {remaining_time} soniya\n"
        f"⚠️ <i>O'yin boshlanishi uchun kamida {config.MIN_PLAYERS} kishi kerak.</i>\n\n"
        f"👉 <i>Iltimos, bot shaxsiyiga kirib <b>/start</b> bosib qo'ying, aks holda anketangiz kelmaydi!</i>"
    )


async def run_lobby_timer(chat_id: int, bot: Bot):
    try:
        total_time = config.LOBBY_TIMEOUT
        step = 15  # Har 15 soniyada yangilash
        
        while total_time > 0:
            await asyncio.sleep(step)
            total_time -= step
            
            game = game_manager.get_game(chat_id)
            if not game or game.phase != GamePhase.LOBBY:
                return

            if total_time > 0 and game.lobby_message_id:
                bot_user = await bot.get_me()
                kb = build_lobby_keyboard(bot_user.username)
                text = format_lobby_text(game, total_time)
                try:
                    await bot.edit_message_text(
                        chat_id=chat_id,
                        message_id=game.lobby_message_id,
                        text=text,
                        reply_markup=kb,
                        parse_mode="HTML"
                    )
                except Exception:
                    pass

        # Taymer tugadi, o'yinni boshlaymiz
        from handlers.game_flow import start_bunker_game
        await start_bunker_game(chat_id, bot)

    except asyncio.CancelledError:
        pass
    except Exception as e:
        import logging
        logging.error(f"Lobby timer xatosi: {e}")


@router.message(Command("bunker", "game"))
async def cmd_bunker(message: Message, bot: Bot):
    if message.chat.type == ChatType.PRIVATE:
        await message.answer(
            "⚠️ Bunker o'yini faqat <b>Telegram guruhlarida</b> o'ynaladi!\n"
            "Meni do'stlaringiz guruhiga qo'shing va u yerda <b>/bunker</b> buyrug'ini bering.",
            parse_mode="HTML"
        )
        return

    if not message.from_user:
        return

    chat_id = message.chat.id
    existing_game = game_manager.get_game(chat_id)
    if existing_game and existing_game.phase != GamePhase.FINISHED:
        await message.answer("⚠️ Ushbu guruhda allaqachon faol o'yin ketmoqda! Uni to'xtatish uchun /stop_game bosing.")
        return

    # Yangi o'yin yaratamiz
    game = game_manager.create_game(
        chat_id=chat_id,
        chat_title=message.chat.title or "Guruh",
        initiator_id=message.from_user.id,
        initiator_name=message.from_user.full_name
    )

    # Tashkilotchini avtomatik ro'yxatga qo'shamiz
    game_manager.add_player(chat_id, message.from_user)

    bot_user = await bot.get_me()
    kb = build_lobby_keyboard(bot_user.username)
    text = format_lobby_text(game, config.LOBBY_TIMEOUT)

    sent_msg = await message.answer(text, reply_markup=kb, parse_mode="HTML")
    game.lobby_message_id = sent_msg.message_id

    # Taymerni ishga tushiramiz
    game.timer_task = asyncio.create_task(run_lobby_timer(chat_id, bot))


@router.callback_query(F.data == "lobby_join")
async def cq_lobby_join(query: CallbackQuery, bot: Bot):
    if not query.message or not query.from_user:
        return

    chat_id = query.message.chat.id
    game = game_manager.get_game(chat_id)
    if not game:
        await query.answer("O'yin topilmadi yoki yakunlangan.", show_alert=True)
        return

    success, msg = game_manager.add_player(chat_id, query.from_user)
    await query.answer(msg, show_alert=not success)

    if success and isinstance(query.message, Message):
        bot_user = await bot.get_me()
        kb = build_lobby_keyboard(bot_user.username)
        text = format_lobby_text(game, config.LOBBY_TIMEOUT)
        try:
            await query.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
        except Exception:
            pass


@router.callback_query(F.data == "lobby_leave")
async def cq_lobby_leave(query: CallbackQuery, bot: Bot):
    if not query.message or not query.from_user:
        return

    chat_id = query.message.chat.id
    game = game_manager.get_game(chat_id)
    if not game:
        await query.answer("O'yin topilmadi.", show_alert=True)
        return

    success, msg = game_manager.remove_player(chat_id, query.from_user.id)
    await query.answer(msg, show_alert=True)

    if success and isinstance(query.message, Message):
        bot_user = await bot.get_me()
        kb = build_lobby_keyboard(bot_user.username)
        text = format_lobby_text(game, config.LOBBY_TIMEOUT)
        try:
            await query.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
        except Exception:
            pass


@router.callback_query(F.data == "lobby_start")
async def cq_lobby_start(query: CallbackQuery, bot: Bot):
    if not query.message or not query.from_user:
        return

    chat_id = query.message.chat.id
    game = game_manager.get_game(chat_id)
    if not game or game.phase != GamePhase.LOBBY:
        await query.answer("O'yin allaqachon boshlangan yoki mavjud emas.", show_alert=True)
        return

    # Tashkilotchi yoki admin ekanini tekshirish
    is_admin = False
    try:
        member = await bot.get_chat_member(chat_id=chat_id, user_id=query.from_user.id)
        if member.status in ["creator", "administrator"]:
            is_admin = True
    except Exception:
        pass


    if query.from_user.id != game.initiator_id and not is_admin:
        await query.answer("⚠️ Faqat o'yinni boshlagan tashkilotchi yoki guruh admini start bera oladi!", show_alert=True)
        return

    if len(game.players) < config.MIN_PLAYERS:
        await query.answer(f"⚠️ O'yinni boshlash uchun kamida {config.MIN_PLAYERS} nafar o'yinchi kerak!", show_alert=True)
        return

    await query.answer("🚀 O'yin boshlanmoqda...")
    game.cancel_timer()

    from handlers.game_flow import start_bunker_game
    await start_bunker_game(chat_id, bot)
