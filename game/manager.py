from typing import Dict, Optional, Tuple, List
from aiogram.types import User
from .models import BunkerGame, Player, GamePhase


class GameManager:
    """
    Barcha faol o'yinlarni Python ichki xotirasida (In-Memory) boshqaruvchi klass.
    Hech qanday ma'lumotlar bazasi talab qilinmaydi.
    """
    def __init__(self):
        self.games: Dict[int, BunkerGame] = {}

    def get_game(self, chat_id: int) -> Optional[BunkerGame]:
        return self.games.get(chat_id)

    def create_game(self, chat_id: int, chat_title: str, initiator_id: int, initiator_name: str) -> BunkerGame:
        # Agar avvalgi tugallanmagan o'yin bo'lsa, avval taymerini to'xtatamiz
        if chat_id in self.games:
            self.games[chat_id].cancel_timer()

        game = BunkerGame(
            chat_id=chat_id,
            chat_title=chat_title,
            initiator_id=initiator_id,
            initiator_name=initiator_name,
            phase=GamePhase.LOBBY
        )
        self.games[chat_id] = game
        return game

    def remove_game(self, chat_id: int) -> None:
        if chat_id in self.games:
            self.games[chat_id].cancel_timer()
            del self.games[chat_id]

    def add_player(self, chat_id: int, user: User) -> Tuple[bool, str]:
        game = self.get_game(chat_id)
        if not game:
            return False, "Ushbu guruhda faol o'yin topilmadi."

        if game.phase != GamePhase.LOBBY:
            return False, "O'yin allaqachon boshlangan, endi qo'shila olmaysiz."

        if user.id in game.players:
            return False, "Siz allaqachon ro'yxatdan o'tgansiz!"

        player = Player(
            user_id=user.id,
            full_name=user.full_name,
            username=user.username,
            is_alive=True
        )
        game.players[user.id] = player
        return True, "Siz bunker ro'yxatiga muvaffaqiyatli qo'shildingiz! 🛡️"

    def remove_player(self, chat_id: int, user_id: int) -> Tuple[bool, str]:
        game = self.get_game(chat_id)
        if not game:
            return False, "Faol o'yin topilmadi."

        if game.phase != GamePhase.LOBBY:
            return False, "O'yin boshlanganidan so'ng chiqib ketib bo'lmaydi."

        if user_id not in game.players:
            return False, "Siz o'yinchilar ro'yxatida emassiz."

        del game.players[user_id]
        return True, "Siz o'yin ro'yxatidan chiqdingiz."

    def find_games_with_player(self, user_id: int) -> List[BunkerGame]:
        return [g for g in self.games.values() if user_id in g.players and g.players[user_id].is_alive]


# Global instansiya
game_manager = GameManager()
