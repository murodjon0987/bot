from aiogram import Router, F, Bot
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.enums import ChatType
from game.manager import game_manager

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, bot: Bot):
    bot_user = await bot.get_me()
    from_name = message.from_user.full_name if message.from_user else "Do'stim"
    username = bot_user.username or "bunker_bot"

    if message.chat.type == ChatType.PRIVATE:
        text = (
            f"👋 <b>Salom, {from_name}!</b>\n\n"
            f"🛡️ <b>'BUNKER'</b> — bu Telegram guruhlarida o'ynaladigan eng qiziqarli "
            f"va psixologik omon qolish (Apokalipsis) o'yinidir!\n\n"
            f"📌 <b>O'yin qanday o'ynaladi?</b>\n"
            f"1. Meni o'z do'stlaringiz guruhiga qo'shing;\n"
            f"2. Guruhda <b>/bunker</b> yoki <b>/game</b> buyrug'ini yuboring;\n"
            f"3. O'yin boshlangach, har kimga bot shaxsiyda maxfiy anketa yuboradi;\n"
            f"4. Guruhda kim bunkerga kirishi va kim tashqarida qolishini bahslashib ovoz berasiz!\n\n"
            f"<i>Bunkerga qabul qilinish uchun tayyormisiz?</i>"
        )
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="➕ Botni guruhga qo'shish",
                    url=f"https://t.me/{username}?startgroup=true"
                )
            ],
            [
                InlineKeyboardButton(text="📜 O'yin qoidalari", callback_data="show_rules"),
                InlineKeyboardButton(text="🆘 Yordam", callback_data="show_help")
            ]
        ])
        await message.answer(text, reply_markup=kb, parse_mode="HTML")
    else:
        await message.answer(
            "🛡️ <b>Bunker o'yinini boshlash uchun /bunker yoki /game buyrug'ini yuboring!</b>",
            parse_mode="HTML"
        )


@router.message(Command("rules"))
async def cmd_rules(message: Message):
    await send_rules_message(message)


@router.callback_query(F.data == "show_rules")
async def cq_rules(query: CallbackQuery):
    if isinstance(query.message, Message):
        await send_rules_message(query.message)
    await query.answer()


async def send_rules_message(message: Message):
    rules_text = (
        "📜 <b>'BUNKER' O'YINI QOIDALARI:</b>\n\n"
        "1️⃣ <b>Falokat (Katastrofa):</b>\n"
        "O'yin boshida tasodifiy falokat (Yadro urushi, Virus, AI qo'zg'oloni...) e'lon qilinadi.\n"
        "Bunkerda joy cheklangan (masalan: 6 kishidan faqat 3 kishi kira oladi).\n\n"
        "2️⃣ <b>Shaxsiy Anketa (PMda beriladi):</b>\n"
        "Har bir o'yinchi botdan 6 ta kartani oladi:\n"
        "• 📇 <b>Kasbi:</b> Bunkerdagi roli va tajribasi.\n"
        "• 🧬 <b>Biologiyasi:</b> Yoshi, jinsi va nasl qoldirish layoqati.\n"
        "• 🩺 <b>Salomatligi:</b> Kasalliklari yoki sog'lomligi.\n"
        "• 🧠 <b>Xarakteri:</b> O'zini qanday tutishi.\n"
        "• 🎒 <b>Bagaji:</b> O'zi bilan olib kelgan foydali buyumi.\n"
        "• 🃏 <b>Maxsus karta:</b> O'yinni o'zgartiruvchi kutilmagan qobiliyat!\n\n"
        "3️⃣ <b>Raundlar va Ovoz berish:</b>\n"
        "Har raundda yangi xususiyat ochiladi, guruhda bahs bo'ladi va eng ko'p ovoz to'plagan 1 kishi bunker eshigi ortida qolib o'yindan chetlatiladi!\n\n"
        "4️⃣ <b>G'alaba:</b>\n"
        "Bunker to'lgach, bot saralangan jamoa omon qolgan-qolmaganini hisoblab beradi!"
    )
    await message.answer(rules_text, parse_mode="HTML")


@router.message(Command("help"))
async def cmd_help(message: Message):
    await send_help_message(message)


@router.callback_query(F.data == "show_help")
async def cq_help(query: CallbackQuery):
    if isinstance(query.message, Message):
        await send_help_message(query.message)
    await query.answer()


async def send_help_message(message: Message):
    help_text = (
        "🆘 <b>BOT BUYRUQLARI VA YORDAM:</b>\n\n"
        "🎮 <b>/bunker</b> yoki <b>/game</b> — Yangi o'yin uchun ro'yxatga olishni boshlash (faqat guruhda)\n"
        "🛑 <b>/stop_game</b> — Joriy o'yinni to'xtatish (guruh admini yoki boshlagan shaxs uchun)\n"
        "📜 <b>/rules</b> — O'yin qoidalarini ko'rish\n"
        "ℹ️ <b>/help</b> — Ushbu yordam xabarini ko'rsatish\n\n"
        "<i>Eslatma: O'yinda qatnashish uchun botga shaxsiyda /start bosgan bo'lishingiz shart, aks holda bot sizga anketa yubora olmaydi!</i>"
    )
    await message.answer(help_text, parse_mode="HTML")


@router.message(Command("stop_game"))
async def cmd_stop_game(message: Message, bot: Bot):
    if message.chat.type == ChatType.PRIVATE:
        await message.answer("Ushbu buyruq faqat guruhlarda ishlaydi.")
        return

    game = game_manager.get_game(message.chat.id)
    if not game:
        await message.answer("Ushbu guruhda ayni paytda faol o'yin yo'q.")
        return

    # Faqat guruh adminlari yoki o'yinni boshlagan shaxs to'xtata oladi
    is_admin = False
    from_id = message.from_user.id if message.from_user else 0
    try:
        if from_id > 0:
            member = await bot.get_chat_member(chat_id=message.chat.id, user_id=from_id)
            if member.status in ["creator", "administrator"]:
                is_admin = True
    except Exception:
        pass

    if not is_admin and from_id != game.initiator_id:
        await message.answer("⚠️ Faqat o'yin tashkilotchisi yoki guruh admini o'yinni to'xtata oladi.")
        return

    game_manager.remove_game(message.chat.id)
    await message.answer("🛑 <b>O'yin bekor qilindi va to'xtatildi.</b> Xotira tozalandi.", parse_mode="HTML")

