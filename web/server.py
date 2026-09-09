from aiohttp import web
from game.manager import game_manager
import logging

logger = logging.getLogger(__name__)


async def handle_root(request: web.Request) -> web.Response:
    active_games = len(game_manager.games)
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Bunker Bot Server</title>
        <meta charset="utf-8">
        <style>
            body {{ font-family: sans-serif; background: #0f172a; color: #f8fafc; text-align: center; padding: 50px; }}
            .card {{ background: #1e293b; border-radius: 12px; padding: 30px; display: inline-block; box-shadow: 0 10px 25px rgba(0,0,0,0.5); }}
            h1 {{ color: #38bdf8; margin-bottom: 10px; }}
            .status {{ color: #4ade80; font-weight: bold; }}
            .badge {{ background: #334155; padding: 6px 12px; border-radius: 20px; font-size: 14px; }}
        </style>
    </head>
    <body>
        <div class="card">
            <h1>🛡️ BUNKER TELEGRAM BOT</h1>
            <p>Server holati: <span class="status">Faol (24/7 Online) 🟢</span></p>
            <p class="badge">Faol o'yinlar soni: {active_games}</p>
            <p style="margin-top: 20px; color: #94a3b8; font-size: 13px;">Render.com / Koyeb Uptime Monitoring tayyor</p>
        </div>
    </body>
    </html>
    """
    return web.Response(text=html_content, content_type="text/html")


async def handle_health(request: web.Request) -> web.Response:
    return web.json_response({
        "status": "healthy",
        "bot": "bunker_game_bot",
        "active_games": len(game_manager.games)
    })


def create_web_app() -> web.Application:
    app = web.Application()
    app.router.add_get("/", handle_root)
    app.router.add_get("/health", handle_health)
    return app


async def start_web_server(host: str, port: int) -> web.AppRunner:
    app = create_web_app()
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host, port)
    await site.start()
    logger.info(f"Web health server muvaffaqiyatli ishga tushdi: http://{host}:{port}")
    return runner
