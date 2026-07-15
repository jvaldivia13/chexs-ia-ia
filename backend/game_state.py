import time
import uuid
from chess_engine import ChessEngine
from typing import Dict, Optional

# Games are held in memory only, with no session/auth concept, so a long-running
# server would otherwise accumulate one entry per game forever. Anything untouched
# for longer than this is considered abandoned and gets pruned on the next create.
GAME_TTL_SECONDS = 3600


DEFAULT_WHITE_AGENT = {
    "name": "Atlas",
    "persona": "balanced",
    "expertise": "normal",
    "provider": "local",
    "model": None,
    "style": "capablanca",
}

DEFAULT_BLACK_AGENT = {
    "name": "Nyx",
    "persona": "tactical",
    "expertise": "normal",
    "provider": "deepseek",
    "model": "deepseek-reasoner",
    "style": "kasparov",
}


class Game:
    def __init__(
        self,
        game_id: str,
        difficulty: str,
        mode: str = "human_vs_ai",
        white_agent: Optional[dict] = None,
        black_agent: Optional[dict] = None,
    ):
        self.game_id = game_id
        self.difficulty = difficulty
        self.mode = mode
        self.white_agent = white_agent or DEFAULT_WHITE_AGENT.copy()
        self.black_agent = black_agent or {
            **DEFAULT_BLACK_AGENT,
            "expertise": difficulty,
        }
        self.engine = ChessEngine()
        self.move_history = []
        self.last_accessed = time.monotonic()


games: Dict[str, Game] = {}


def _prune_expired_games() -> None:
    cutoff = time.monotonic() - GAME_TTL_SECONDS
    expired = [game_id for game_id, game in games.items() if game.last_accessed < cutoff]
    for game_id in expired:
        del games[game_id]


def create_game(
    difficulty: str,
    mode: str = "human_vs_ai",
    white_agent: Optional[dict] = None,
    black_agent: Optional[dict] = None,
) -> Game:
    _prune_expired_games()
    game_id = str(uuid.uuid4())
    game = Game(game_id, difficulty, mode, white_agent, black_agent)
    games[game_id] = game
    return game


def get_game(game_id: str) -> Optional[Game]:
    game = games.get(game_id)
    if game:
        game.last_accessed = time.monotonic()
    return game
