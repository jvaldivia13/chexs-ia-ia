import logging
import os
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from models import (
    AgentTurnRequest,
    AgentTurnResponse,
    NewGameRequest,
    NewGameResponse,
    MoveRequest,
    MoveResponse,
    GameStateResponse,
)
from game_state import DEFAULT_BLACK_AGENT, DEFAULT_WHITE_AGENT, create_game, get_game
from ai import get_ai_move
from a2a_agents import apply_agent_turn, normalize_agent_profile

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))

app = FastAPI()

DEFAULT_ALLOWED_ORIGINS = "http://localhost:5173,http://127.0.0.1:5173"
allowed_origins = [
    origin.strip()
    for origin in os.getenv("ALLOWED_ORIGINS", DEFAULT_ALLOWED_ORIGINS).split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

current_game_id = None


def resolve_game_id(game_id: Optional[str] = None) -> str:
    selected_game_id = game_id or current_game_id
    if not selected_game_id:
        raise HTTPException(status_code=400, detail="No active game")
    return selected_game_id


def current_turn(game) -> str:
    return "white" if game.engine.board.turn == True else "black"


def player_in_check(game) -> bool:
    return game.engine.is_check() and game.engine.board.turn == True


@app.post("/api/game/new", response_model=NewGameResponse)
@app.post("/game/new", response_model=NewGameResponse)
def new_game(request: NewGameRequest):
    global current_game_id

    if request.difficulty not in ["easy", "normal", "difficult"]:
        raise HTTPException(status_code=400, detail="Invalid difficulty")
    if request.mode not in ["human_vs_ai", "ai_vs_ai"]:
        raise HTTPException(status_code=400, detail="Invalid game mode")

    white_agent = normalize_agent_profile(
        request.white_agent.model_dump() if request.white_agent else None,
        DEFAULT_WHITE_AGENT,
    )
    black_agent = normalize_agent_profile(
        request.black_agent.model_dump() if request.black_agent else None,
        {**DEFAULT_BLACK_AGENT, "expertise": request.difficulty},
    )
    game = create_game(request.difficulty, request.mode, white_agent, black_agent)
    current_game_id = game.game_id

    return NewGameResponse(
        game_id=game.game_id,
        board_fen=game.engine.get_fen(),
        player_color="white",
        message="Game started",
        mode=game.mode,
        white_agent=game.white_agent,
        black_agent=game.black_agent,
    )


@app.post("/api/game/move", response_model=MoveResponse)
@app.post("/game/move", response_model=MoveResponse)
def make_move(request: MoveRequest):
    game_id = resolve_game_id(request.game_id)
    game = get_game(game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    if game.engine.get_game_status() != "ongoing":
        raise HTTPException(status_code=400, detail="Game is over")

    # Validate and apply player move
    if not game.engine.make_move(request.from_square, request.to_square, request.promotion):
        raise HTTPException(status_code=400, detail="Illegal move")

    player_move = request.from_square + request.to_square + (request.promotion.lower() if request.promotion else "")
    game.move_history.append(player_move)

    # Check game status
    game_status = game.engine.get_game_status()

    ai_move = None
    if request.auto_reply and game_status == "ongoing":
        # Get AI move
        candidate_move = get_ai_move(game.engine, game.difficulty)
        if candidate_move and game.engine.make_move(candidate_move[:2], candidate_move[2:4], candidate_move[4:] or None):
            ai_move = candidate_move
            game.move_history.append(ai_move)
            game_status = game.engine.get_game_status()

    return MoveResponse(
        player_move=player_move,
        ai_move=ai_move,
        board_fen=game.engine.get_fen(),
        game_status=game_status,
        legal_moves=game.engine.get_legal_moves() if game_status == "ongoing" else [],
        player_in_check=player_in_check(game),
        turn=current_turn(game),
        move_history=game.move_history,
    )


@app.post("/api/game/agent-turn", response_model=AgentTurnResponse)
@app.post("/game/agent-turn", response_model=AgentTurnResponse)
def agent_turn(request: AgentTurnRequest):
    game_id = resolve_game_id(request.game_id)
    game = get_game(game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    if game.engine.get_game_status() != "ongoing":
        active_profile = game.white_agent if current_turn(game) == "white" else game.black_agent
        return AgentTurnResponse(
            agent_move=None,
            agent_color=current_turn(game),
            agent_name=active_profile["name"],
            agent_profile=active_profile,
            a2a_message_id="",
            board_fen=game.engine.get_fen(),
            game_status=game.engine.get_game_status(),
            legal_moves=[],
            player_in_check=player_in_check(game),
            turn=current_turn(game),
            move_history=game.move_history,
        )

    result = apply_agent_turn(game)
    game_status = game.engine.get_game_status()
    return AgentTurnResponse(
        agent_move=result["agent_move"],
        agent_color=result["agent_color"],
        agent_name=result["agent_name"],
        agent_profile=result["agent_profile"],
        a2a_message_id=result["a2a_message_id"],
        board_fen=game.engine.get_fen(),
        game_status=game_status,
        legal_moves=game.engine.get_legal_moves() if game_status == "ongoing" else [],
        player_in_check=player_in_check(game),
        turn=current_turn(game),
        move_history=game.move_history,
    )


@app.get("/api/game/state", response_model=GameStateResponse)
@app.get("/game/state", response_model=GameStateResponse)
def game_state(game_id: Optional[str] = Query(default=None)):
    selected_game_id = resolve_game_id(game_id)
    game = get_game(selected_game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")

    return GameStateResponse(
        board_fen=game.engine.get_fen(),
        game_status=game.engine.get_game_status(),
        turn=current_turn(game),
        mode=game.mode,
        white_agent=game.white_agent,
        black_agent=game.black_agent,
        move_history=game.move_history,
    )


@app.get("/health")
def health_check():
    return {"status": "ok"}
