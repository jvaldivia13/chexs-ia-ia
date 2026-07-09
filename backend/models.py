from pydantic import BaseModel
from typing import Optional, List

class NewGameRequest(BaseModel):
    difficulty: str  # 'easy', 'normal', 'difficult'

class NewGameResponse(BaseModel):
    game_id: str
    board_fen: str
    player_color: str
    message: str

class MoveRequest(BaseModel):
    game_id: Optional[str] = None
    from_square: str
    to_square: str
    promotion: Optional[str] = None

class MoveResponse(BaseModel):
    player_move: str
    ai_move: Optional[str]
    board_fen: str
    game_status: str
    legal_moves: List[str]
    player_in_check: bool

class GameStateResponse(BaseModel):
    board_fen: str
    game_status: str
    turn: str
