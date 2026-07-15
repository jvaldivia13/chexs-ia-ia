from pydantic import BaseModel
from typing import Optional, List

class AgentProfile(BaseModel):
    name: str
    persona: str  # 'balanced', 'aggressive', 'defensive', 'tactical'
    expertise: str  # 'easy', 'normal', or 'difficult'
    provider: str = "local"  # 'local', 'openai', or 'deepseek'
    model: Optional[str] = None
    style: Optional[str] = None  # grandmaster style key, e.g. 'kasparov', 'tal', 'karpov', 'capablanca'

class NewGameRequest(BaseModel):
    difficulty: str  # 'easy', 'normal', 'difficult'
    mode: str = "human_vs_ai"  # 'human_vs_ai' or 'ai_vs_ai'
    white_agent: Optional[AgentProfile] = None
    black_agent: Optional[AgentProfile] = None

class NewGameResponse(BaseModel):
    game_id: str
    board_fen: str
    player_color: str
    message: str
    mode: str = "human_vs_ai"
    white_agent: Optional[AgentProfile] = None
    black_agent: Optional[AgentProfile] = None

class MoveRequest(BaseModel):
    game_id: Optional[str] = None
    from_square: str
    to_square: str
    promotion: Optional[str] = None
    auto_reply: bool = True

class MoveResponse(BaseModel):
    player_move: str
    ai_move: Optional[str]
    board_fen: str
    game_status: str
    legal_moves: List[str]
    player_in_check: bool
    turn: str
    move_history: List[str] = []

class AgentTurnRequest(BaseModel):
    game_id: Optional[str] = None

class AgentTurnResponse(BaseModel):
    agent_move: Optional[str]
    agent_color: str
    agent_name: str
    agent_profile: AgentProfile
    a2a_message_id: str
    board_fen: str
    game_status: str
    legal_moves: List[str]
    player_in_check: bool
    turn: str
    move_history: List[str]

class GameStateResponse(BaseModel):
    board_fen: str
    game_status: str
    turn: str
    mode: str = "human_vs_ai"
    white_agent: Optional[AgentProfile] = None
    black_agent: Optional[AgentProfile] = None
    move_history: List[str] = []
