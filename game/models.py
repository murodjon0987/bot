from dataclasses import dataclass, field
from enum import Enum
import asyncio
from typing import Optional, Dict, List, Any


class GamePhase(Enum):
    LOBBY = "lobby"                 # Ro'yxatga olish
    STARTING = "starting"           # Kartalar taqsimlanmoqda
    CARD_REVEAL = "card_reveal"     # Karta ochish bosqichi
    DISCUSSION = "discussion"       # Muhokama va bahs
    VOTING = "voting"               # Ovoz berish
    ROUND_END = "round_end"         # Raund xulosasi va chetlatish
    FINISHED = "finished"           # O'yin yakunlangan


@dataclass
class SpecialCard:
    card_id: str
    name: str
    description: str
    is_used: bool = False


@dataclass
class PlayerCard:
    profession: str
    experience_years: int
    biology: str            # Masalan: "27 yosh, Erkak, Nasl qoldira oladi"
    age: int
    gender: str
    can_reproduce: bool
    health: str             # Masalan: "100% sog'lom, kuchli immunitet"
    trait: str              # Xarakter xususiyati: "Mehnatkash, sovuqqon"
    luggage: str            # Bagajdagi buyum: "Miltiq va 20 ta patron"
    special_card: SpecialCard
    revealed: Dict[str, bool] = field(default_factory=lambda: {
        "profession": False,
        "biology": False,
        "health": False,
        "trait": False,
        "luggage": False,
        "special_card": False
    })


@dataclass
class Player:
    user_id: int
    full_name: str
    username: Optional[str] = None
    is_alive: bool = True
    card: Optional[PlayerCard] = None
    votes_received: int = 0
    extra_votes: int = 0
    can_vote: bool = True
    has_immunity: bool = False

    @property
    def mention(self) -> str:
        if self.username:
            return f"@{self.username}"
        return f"<a href='tg://user?id={self.user_id}'>{self.full_name}</a>"


@dataclass
class Catastrophe:
    title: str
    description: str
    duration_years: int
    amenities: List[str]
    threats: List[str]


@dataclass
class BunkerGame:
    chat_id: int
    chat_title: str
    initiator_id: int
    initiator_name: str
    phase: GamePhase = GamePhase.LOBBY
    players: Dict[int, Player] = field(default_factory=dict)
    catastrophe: Optional[Catastrophe] = None
    bunker_capacity: int = 0
    round_number: int = 1
    timer_task: Optional[asyncio.Task] = None
    votes: Dict[int, int] = field(default_factory=dict)  # voter_id -> target_user_id
    lobby_message_id: Optional[int] = None
    current_message_id: Optional[int] = None
    eliminated_players: List[Player] = field(default_factory=list)

    @property
    def alive_players(self) -> List[Player]:
        return [p for p in self.players.values() if p.is_alive]

    @property
    def alive_count(self) -> int:
        return len(self.alive_players)

    def cancel_timer(self):
        if self.timer_task and not self.timer_task.done():
            self.timer_task.cancel()
            self.timer_task = None
