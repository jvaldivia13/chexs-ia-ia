import uuid
from chess_engine import ChessEngine
from typing import Dict, Optional


class Game:
    def __init__(self, game_id: str, difficulty: str):
        self.game_id = game_id
        self.difficulty = difficulty
        self.engine = ChessEngine()
        self.move_history = []


games: Dict[str, Game] = {}


def create_game(difficulty: str) -> Game:
    game_id = str(uuid.uuid4())
    game = Game(game_id, difficulty)
    games[game_id] = game
    return game


def get_game(game_id: str) -> Optional[Game]:
    return games.get(game_id)
