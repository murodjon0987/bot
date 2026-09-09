import asyncio
import sys
from unittest.mock import MagicMock

reconfig_out = getattr(sys.stdout, "reconfigure", None)
if callable(reconfig_out):
    reconfig_out(encoding="utf-8")


from game.models import GamePhase, Player
from game.manager import game_manager
from game.scenarios import generate_catastrophe, generate_player_card
from game.evaluator import evaluate_bunker_survival


def test_scenario_generation():
    cat = generate_catastrophe()
    assert cat.title
    assert cat.duration_years > 0
    assert len(cat.amenities) > 0

    card = generate_player_card()
    assert card.profession
    assert card.age >= 18
    assert card.special_card.card_id
    print("✅ Scenario & Card generation passed!")


def test_game_manager_flow():
    chat_id = -100123456789
    game = game_manager.create_game(
        chat_id=chat_id,
        chat_title="Sinov Guruhi",
        initiator_id=101,
        initiator_name="Ali"
    )

    # 4 ta o'yinchi qo'shamiz
    for uid, name in [(101, "Ali"), (102, "Vali"), (103, "Gani"), (104, "Sami")]:
        fake_user = MagicMock()
        fake_user.id = uid
        fake_user.full_name = name
        fake_user.username = f"user_{uid}"
        success, msg = game_manager.add_player(chat_id, fake_user)
        assert success

    assert len(game.players) == 4
    assert game.alive_count == 4

    # O'yinni tayyorlash
    game.phase = GamePhase.STARTING
    game.catastrophe = generate_catastrophe()
    game.bunker_capacity = 2

    for p in game.players.values():
        p.card = generate_player_card()

    # O'yinchini chetlatish sinovi
    p1 = game.players[104]
    p1.is_alive = False
    game.eliminated_players.append(p1)
    assert game.alive_count == 3

    # Yana bir o'yinchini chetlatamiz (shunda 2 ta qoladi == bunker_capacity)
    p2 = game.players[103]
    p2.is_alive = False
    game.eliminated_players.append(p2)
    assert game.alive_count == 2

    # Epilog hisoblash
    epilogue = evaluate_bunker_survival(game)
    assert "BUNKER EPILOGI" in epilogue
    assert "Omon qolish indeksi" in epilogue
    print("✅ Epilogue evaluation passed!")

    # Tozalash
    game_manager.remove_game(chat_id)
    assert game_manager.get_game(chat_id) is None
    print("✅ In-memory cleanup passed (0 MB DB)!")


if __name__ == "__main__":
    test_scenario_generation()
    test_game_manager_flow()
    print("\n🎉 Barcha unit-testlar muvaffaqiyatli o'tdi!")
