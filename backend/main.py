from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from models import NewGameRequest, NewGameResponse, MoveRequest, MoveResponse, GameStateResponse
from game_state import create_game, get_game
from ai import get_ai_move

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
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


@app.post("/api/game/new", response_model=NewGameResponse)
@app.post("/game/new", response_model=NewGameResponse)
def new_game(request: NewGameRequest):
    global current_game_id

    if request.difficulty not in ["easy", "normal", "difficult"]:
        raise HTTPException(status_code=400, detail="Invalid difficulty")

    game = create_game(request.difficulty)
    current_game_id = game.game_id

    return NewGameResponse(
        game_id=game.game_id,
        board_fen=game.engine.get_fen(),
        player_color="white",
        message="Game started"
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
    if game_status == "ongoing":
        # Get AI move
        ai_move = get_ai_move(game.engine, game.difficulty)
        if ai_move:
            game.engine.make_move(ai_move[:2], ai_move[2:4], ai_move[4:] or None)
            game.move_history.append(ai_move)
            game_status = game.engine.get_game_status()

    return MoveResponse(
        player_move=player_move,
        ai_move=ai_move,
        board_fen=game.engine.get_fen(),
        game_status=game_status,
        legal_moves=game.engine.get_legal_moves() if game_status == "ongoing" else [],
        player_in_check=game.engine.is_check() and game.engine.board.turn == True
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
        turn="white" if game.engine.board.turn == True else "black"
    )


@app.get("/health")
def health_check():
    return {"status": "ok"}
