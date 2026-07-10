import uuid
from dataclasses import dataclass
from typing import Any, Dict, Optional

import chess

from ai import evaluate_position, get_ai_move
from chess_engine import ChessEngine
from llm_chess import choose_llm_move


VALID_PERSONAS = {"balanced", "aggressive", "defensive", "tactical"}
VALID_EXPERTISE = {"easy", "normal", "difficult"}
VALID_PROVIDERS = {"local", "openai", "deepseek"}


@dataclass
class A2AMessage:
    message_id: str
    sender: str
    recipient: str
    action: str
    payload: Dict[str, Any]


def normalize_agent_profile(profile: Optional[dict], fallback: dict) -> dict:
    data = {**fallback, **(profile or {})}
    if data.get("persona") not in VALID_PERSONAS:
        data["persona"] = fallback["persona"]
    if data.get("expertise") not in VALID_EXPERTISE:
        data["expertise"] = fallback["expertise"]
    if data.get("provider") not in VALID_PROVIDERS:
        data["provider"] = fallback.get("provider", "local")
    if not data.get("name"):
        data["name"] = fallback["name"]
    if data.get("model") == "":
        data["model"] = None
    return data


def build_turn_message(game, agent_color: str) -> A2AMessage:
    profile = game.white_agent if agent_color == "white" else game.black_agent
    opponent = game.black_agent if agent_color == "white" else game.white_agent
    return A2AMessage(
        message_id=str(uuid.uuid4()),
        sender=opponent["name"],
        recipient=profile["name"],
        action="chess.move.request",
        payload={
            "fen": game.engine.get_fen(),
            "agent_color": agent_color,
            "profile": profile,
            "move_history": list(game.move_history),
        },
    )


def select_agent_move(engine: ChessEngine, profile: dict) -> str:
    provider = profile.get("provider", "local")
    if provider != "local":
        llm_move = choose_llm_move(engine, profile)
        if llm_move in engine.get_legal_moves():
            return llm_move

    expertise = profile.get("expertise", "normal")
    persona = profile.get("persona", "balanced")

    if persona == "balanced":
        return get_ai_move(engine, expertise)

    legal_moves = engine.get_legal_moves()
    if not legal_moves:
        return ""

    if expertise == "easy":
        search_depth = 0
    elif expertise == "normal":
        search_depth = 1
    else:
        search_depth = 2

    agent_color = engine.board.turn
    scored_moves = []

    for move_uci in legal_moves:
        move = chess.Move.from_uci(move_uci)
        capture_bonus = 1.5 if engine.board.is_capture(move) else 0.0

        engine.board.push(move)
        check_bonus = 1.0 if engine.board.is_check() else 0.0
        score = evaluate_position(engine.board)
        if search_depth > 0 and not engine.board.is_game_over():
            score = _lookahead_score(engine.board, search_depth, agent_color)
        engine.board.pop()

        net_score = score if agent_color == chess.WHITE else -score
        if persona == "aggressive":
            net_score += capture_bonus + check_bonus
        elif persona == "defensive":
            net_score += _defensive_bonus(engine.board, move, agent_color)
        elif persona == "tactical":
            net_score += (capture_bonus * 1.25) + (check_bonus * 1.25)

        scored_moves.append((net_score, move_uci))

    scored_moves.sort(reverse=True)
    return scored_moves[0][1]


def apply_agent_turn(game) -> dict:
    agent_color = "white" if game.engine.board.turn == chess.WHITE else "black"
    profile = game.white_agent if agent_color == "white" else game.black_agent
    message = build_turn_message(game, agent_color)
    move = select_agent_move(game.engine, profile)

    if move:
        game.engine.make_move(move[:2], move[2:4], move[4:] or None)
        game.move_history.append(move)

    return {
        "agent_move": move or None,
        "agent_color": agent_color,
        "agent_name": profile["name"],
        "agent_profile": profile,
        "a2a_message_id": message.message_id,
    }


def _lookahead_score(board: chess.Board, depth: int, agent_color: chess.Color) -> float:
    if depth == 0 or board.is_game_over():
        return evaluate_position(board)

    scores = []
    for move in board.legal_moves:
        board.push(move)
        scores.append(_lookahead_score(board, depth - 1, agent_color))
        board.pop()

    if not scores:
        return evaluate_position(board)
    return max(scores) if board.turn == agent_color else min(scores)


def _defensive_bonus(board: chess.Board, move: chess.Move, agent_color: chess.Color) -> float:
    board.push(move)
    own_king_square = board.king(agent_color)
    attacked = bool(own_king_square is not None and board.is_attacked_by(not agent_color, own_king_square))
    board.pop()
    return -2.0 if attacked else 0.3
