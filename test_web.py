import asyncio
import sys
import aiohttp

reconfig_out = getattr(sys.stdout, "reconfigure", None)
if callable(reconfig_out):
    reconfig_out(encoding="utf-8")


from web.server import start_web_server


async def test_server():
    runner = await start_web_server("127.0.0.1", 8899)
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("http://127.0.0.1:8899/health") as resp:
                assert resp.status == 200
                data = await resp.json()
                assert data["status"] == "healthy"
                print("✅ /health endpoint 200 OK qaytardi:", data)

            async with session.get("http://127.0.0.1:8899/") as resp:
                assert resp.status == 200
                html = await resp.text()
                assert "BUNKER TELEGRAM BOT" in html
                print("✅ Root / endpoint 200 OK HTML qaytardi!")
    finally:
        await runner.cleanup()
        print("✅ Web server to'xtatildi!")


if __name__ == "__main__":
    asyncio.run(test_server())
