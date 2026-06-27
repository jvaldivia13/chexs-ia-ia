import random
import chess
from chess_engine import ChessEngine


def get_ai_move(engine: ChessEngine, difficulty: str) -> str:
    """
    Get an AI move based on difficulty level.

    Args:
        engine: ChessEngine instance
        difficulty: "easy", "normal", or "difficult"

    Returns:
        A move in UCI format (e.g., "e2e4")
    """
    legal_moves = engine.get_legal_moves()

    if difficulty == "easy":
        return random.choice(legal_moves)
    elif difficulty == "normal":
        return get_normal_move(engine)
    elif difficulty == "difficult":
        return get_difficult_move(engine)

    return random.choice(legal_moves)


def evaluate_position(board: chess.Board) -> float:
    """Simple board evaluation: material count + positional factors"""
    piece_values = {
        chess.PAWN: 1,
        chess.KNIGHT: 3,
        chess.BISHOP: 3,
        chess.ROOK: 5,
        chess.QUEEN: 9,
        chess.KING: 0
    }

    score = 0.0

    # Material count
    for piece_type, value in piece_values.items():
        white_count = len(board.pieces(piece_type, chess.WHITE))
        black_count = len(board.pieces(piece_type, chess.BLACK))
        score += (white_count - black_count) * value

    # Simple positional bonus: center control
    center_squares = [chess.E4, chess.D4, chess.E5, chess.D5]
    for sq in center_squares:
        if board.piece_at(sq) and board.piece_at(sq).color == chess.WHITE:
            score += 0.5
        elif board.piece_at(sq) and board.piece_at(sq).color == chess.BLACK:
            score -= 0.5

    return score


def get_normal_move(engine: ChessEngine) -> str:
    """
    Evaluates positions 2 moves ahead, chooses best move.
    Uses minimax-like evaluation with position assessment.
    """
    legal_moves = engine.get_legal_moves()

    best_move = None
    best_score = -float('inf')

    for move_uci in legal_moves:
        # Try the move
        engine.board.push_uci(move_uci)

        # Evaluate after this move + opponent's best response
        position_score = evaluate_position(engine.board)

        # Simple lookahead: check if opponent has a strong response
        opponent_moves = [m.uci()[:4] for m in engine.board.legal_moves]
        worst_opponent_score = float('inf')

        for opp_move in opponent_moves:
            engine.board.push_uci(opp_move)
            opp_score = evaluate_position(engine.board)
            worst_opponent_score = min(worst_opponent_score, opp_score)
            engine.board.pop()

        # Net score: our position minus opponent's best response
        net_score = position_score - worst_opponent_score * 0.5

        if net_score > best_score:
            best_score = net_score
            best_move = move_uci

        engine.board.pop()

    return best_move if best_move else random.choice(legal_moves)


def get_difficult_move(engine: ChessEngine) -> str:
    """
    Placeholder for difficult difficulty AI.
    Currently returns a random legal move.
    """
    return random.choice(engine.get_legal_moves())
