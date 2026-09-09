import os
from dotenv import load_dotenv

# .env faylini yuklash
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
PORT = int(os.getenv("PORT", "8080"))
HOST = os.getenv("HOST", "0.0.0.0")

MIN_PLAYERS = int(os.getenv("MIN_PLAYERS", "4"))
LOBBY_TIMEOUT = int(os.getenv("LOBBY_TIMEOUT", "60"))
DISCUSSION_TIMEOUT = int(os.getenv("DISCUSSION_TIMEOUT", "60"))
VOTING_TIMEOUT = int(os.getenv("VOTING_TIMEOUT", "45"))
