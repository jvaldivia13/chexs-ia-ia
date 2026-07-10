import uuid
from chess_engine import ChessEngine
from typing import Dict, Optional


DEFAULT_WHITE_AGENT = {
    "name": "Atlas",
    "persona": "balanced",
    "expertise": "normal",
    "provider": "local",
    "model": None,
}

DEFAULT_BLACK_AGENT = {
    "name": "Nyx",
    "persona": "tactical",
    "expertise": "normal",
    "provider": "deepseek",
    "model": "deepseek-reasoner",
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


games: Dict[str, Game] = {}


def create_game(
    difficulty: str,
    mode: str = "human_vs_ai",
    white_agent: Optional[dict] = None,
    black_agent: Optional[dict] = None,
) -> Game:
    game_id = str(uuid.uuid4())
    game = Game(game_id, difficulty, mode, white_agent, black_agent)
    games[game_id] = game
    return game


def get_game(game_id: str) -> Optional[Game]:
    return games.get(game_id)
