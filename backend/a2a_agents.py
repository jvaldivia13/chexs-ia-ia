import uuid
from dataclasses import dataclass
from typing import Any, Dict, Optional

import chess

from ai import evaluate_position, get_ai_move, minimax
from chess_engine import ChessEngine
from llm_chess import choose_llm_move


# Below this net material swing (in pawns), an LLM-proposed move is treated as
# a sound choice. LLM moves come from a text prompt with no material-aware
# search behind them at all, so they need a lightweight tactical safety net
# before being trusted -- this is the same magnitude as "hanging a minor piece".
_BLUNDER_THRESHOLD = 2.0

_PERSONA_TOLERANCE = {
    "defensive": 0.20,
    "balanced": 0.35,
    "aggressive": 0.60,
    "tactical": 0.75,
}
_CANDIDATE_COUNT = 3


def _is_blunder(engine: ChessEngine, move_uci: str, threshold: float = _BLUNDER_THRESHOLD) -> bool:
    """True if the opponent's best reply to this move swings material against
    the mover by more than `threshold`, with no compensation (e.g. delivering
    checkmate is never a blunder regardless of material given up)."""
    move = chess.Move.from_uci(move_uci)
    mover_color = engine.board.turn
    before = evaluate_position(engine.board)

    engine.board.push(move)
    if engine.board.is_checkmate():
        engine.board.pop()
        return False

    reply_score = minimax(
        engine.board,
        depth=1,
        alpha=-float('inf'),
        beta=float('inf'),
        is_maximizing=engine.board.turn == chess.WHITE,
    )
    engine.board.pop()

    net_before = before if mover_color == chess.WHITE else -before
    net_after = reply_score if mover_color == chess.WHITE else -reply_score
    return (net_after - net_before) < -threshold


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
        candidates = analyze_move_candidates(engine, profile.get("expertise", "normal"))
        llm_move = choose_llm_move(engine, {**profile, "_candidates": candidates})
        candidate_scores = {candidate["move"]: candidate["score"] for candidate in candidates}
        if llm_move in candidate_scores and candidates:
            tolerance = _PERSONA_TOLERANCE.get(profile.get("persona", "balanced"), 0.35)
            if candidates[0]["score"] - candidate_scores[llm_move] <= tolerance and not _is_blunder(engine, llm_move):
                return llm_move
        if candidates:
            return candidates[0]["move"]

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


def analyze_move_candidates(engine: ChessEngine, expertise: str, top_k: int = _CANDIDATE_COUNT) -> list[dict]:
    """Produce a small set of calculated moves for LLM deliberation."""
    depth = {"easy": 1, "normal": 2, "difficult": 3}.get(expertise, 2)
    board = engine.board
    mover = board.turn
    before_material = _material_score(board)
    candidates = []

    for move in list(board.legal_moves):
        is_capture = board.is_capture(move)
        board.push(move)
        try:
            score, continuation = _search_with_pv(board, depth - 1, -float("inf"), float("inf"))
            mover_score = score if mover == chess.WHITE else -score
            material_delta = _material_score(board) - before_material
            material_delta = material_delta if mover == chess.WHITE else -material_delta
            candidates.append({
                "move": move.uci(),
                "score": round(mover_score, 3),
                "principal_variation": [move.uci(), *continuation],
                "features": {
                    "material_delta": round(material_delta, 3),
                    "is_capture": is_capture,
                    "gives_check": board.is_check(),
                },
            })
        finally:
            board.pop()

    candidates.sort(key=lambda candidate: (-candidate["score"], candidate["move"]))
    return candidates[:top_k]


def _search_with_pv(board: chess.Board, depth: int, alpha: float, beta: float) -> tuple[float, list[str]]:
    if board.is_game_over():
        return evaluate_position(board), []
    if depth == 0:
        return _quiescence(board, alpha, beta), []

    maximizing = board.turn == chess.WHITE
    best_score = -float("inf") if maximizing else float("inf")
    best_line = []
    for move in list(board.legal_moves):
        board.push(move)
        try:
            score, line = _search_with_pv(board, depth - 1, alpha, beta)
        finally:
            board.pop()
        if (maximizing and score > best_score) or (not maximizing and score < best_score):
            best_score, best_line = score, [move.uci(), *line]
        if maximizing:
            alpha = max(alpha, best_score)
        else:
            beta = min(beta, best_score)
        if beta <= alpha:
            break
    return best_score, best_line


def _quiescence(board: chess.Board, alpha: float, beta: float, remaining: int = 4) -> float:
    """Continue through captures/promotions so leaf evaluations are stable."""
    stand_pat = evaluate_position(board)
    if remaining == 0 or board.is_game_over():
        return stand_pat
    maximizing = board.turn == chess.WHITE
    if maximizing:
        if stand_pat >= beta:
            return stand_pat
        alpha = max(alpha, stand_pat)
    else:
        if stand_pat <= alpha:
            return stand_pat
        beta = min(beta, stand_pat)

    best = stand_pat
    for move in [move for move in board.legal_moves if board.is_capture(move) or move.promotion]:
        board.push(move)
        try:
            score = _quiescence(board, alpha, beta, remaining - 1)
        finally:
            board.pop()
        best = max(best, score) if maximizing else min(best, score)
        if maximizing:
            alpha = max(alpha, best)
        else:
            beta = min(beta, best)
        if beta <= alpha:
            break
    return best


def _material_score(board: chess.Board) -> float:
    values = {chess.PAWN: 1, chess.KNIGHT: 3, chess.BISHOP: 3, chess.ROOK: 5, chess.QUEEN: 9}
    return float(sum(
        (len(board.pieces(piece, chess.WHITE)) - len(board.pieces(piece, chess.BLACK))) * value
        for piece, value in values.items()
    ))


def apply_agent_turn(game) -> dict:
    agent_color = "white" if game.engine.board.turn == chess.WHITE else "black"
    profile = game.white_agent if agent_color == "white" else game.black_agent
    message = build_turn_message(game, agent_color)
    move = select_agent_move(game.engine, profile)

    applied = False
    if move:
        applied = game.engine.make_move(move[:2], move[2:4], move[4:] or None)
        if applied:
            game.move_history.append(move)

    return {
        "agent_move": move if applied else None,
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
