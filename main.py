import asyncio
import logging
import sys
import os
import aiohttp

# Windows terminallarida UTF-8 emoji va belgilarni to'g'ri ko'rsatish
reconfig_out = getattr(sys.stdout, "reconfigure", None)
if callable(reconfig_out):
    reconfig_out(encoding="utf-8")

reconfig_err = getattr(sys.stderr, "reconfigure", None)
if callable(reconfig_err):
    reconfig_err(encoding="utf-8")


from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

import config
from web.server import start_web_server
from handlers import common_router, lobby_router, game_flow_router

# Logging sozlash
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] - %(name)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("bunker_bot")


async def self_keep_alive():
    """Render.com da 15 daqiqada uxlab qolmasligi uchun har 8 daqiqada o'zini o'zi ping qiladi"""
    app_url = os.getenv("RENDER_EXTERNAL_URL", "").strip()
    if not app_url:
        return
    logger.info(f"🔄 Self-Keep-Alive faollashtirildi: {app_url}/health")
    await asyncio.sleep(30)
    while True:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{app_url}/health", timeout=aiohttp.ClientTimeout(total=15)) as resp:
                    logger.info(f"💓 Keep-alive ping muvaffaqiyatli: status={resp.status}")

        except Exception as e:
            logger.warning(f"Keep-alive ping xatosi: {e}")
        await asyncio.sleep(8 * 60)  # Har 8 daqiqada


async def main():
    logger.info("🛡️ 'BUNKER' Telegram Boti ishga tushirilmoqda...")

    if not config.BOT_TOKEN:
        logger.error(
            "❌ XATOLIK: BOT_TOKEN topilmadi!\n"
            "Iltimos, '.env' faylini ochib, BotFather'dan olingan tokeningizni kiriting:\n"
            "BOT_TOKEN=123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ"
        )
        return

    # Bot va Dispatcher yaratish
    bot = Bot(
        token=config.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()

    # Routerlarni ulash
    dp.include_router(common_router)
    dp.include_router(lobby_router)
    dp.include_router(game_flow_router)

    # 24/7 Bepul xostinglar (Render.com, Koyeb) uchun fonida web serverni ishga tushirish
    runner = await start_web_server(config.HOST, config.PORT)

    # Render uxlab qolmasligi uchun o'zini-o'zi ping qilish vazifasini ishga tushirish
    asyncio.create_task(self_keep_alive())

    try:
        # Eski kutilgan xabarlarni tozalash va pollingni boshlash
        await bot.delete_webhook(drop_pending_updates=True)
        bot_info = await bot.get_me()
        logger.info(f"✅ Bot muvaffaqiyatli ulandi: @{bot_info.username} ({bot_info.full_name})")
        logger.info(f"🌐 24/7 Health Monitoring: http://{config.HOST}:{config.PORT}/health")

        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())

    finally:
        logger.info("🛑 Bot to'xtatilmoqda...")
        await runner.cleanup()
        await bot.session.close()
        logger.info("Bot sessiyasi yopildi.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot foydalanuvchi tomonidan to'xtatildi.")
