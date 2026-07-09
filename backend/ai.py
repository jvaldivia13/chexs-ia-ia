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
    if not legal_moves:
        return ""

    if difficulty == "easy":
        return random.choice(legal_moves)
    elif difficulty == "normal":
        return get_normal_move(engine)
    elif difficulty == "difficult":
        return get_difficult_move(engine)

    return random.choice(legal_moves)


def evaluate_position(board: chess.Board) -> float:
    """Simple board evaluation: material count + positional factors"""
    if board.is_checkmate():
        return -10000.0 if board.turn == chess.WHITE else 10000.0
    if board.is_stalemate() or board.is_insufficient_material():
        return 0.0

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
    ai_color = engine.board.turn

    best_move = None
    best_score = -float('inf')

    for move_uci in legal_moves:
        engine.board.push_uci(move_uci)
        position_score = minimax(
            engine.board,
            depth=1,
            alpha=-float('inf'),
            beta=float('inf'),
            is_maximizing=engine.board.turn == chess.WHITE
        )
        net_score = position_score if ai_color == chess.WHITE else -position_score

        if net_score > best_score:
            best_score = net_score
            best_move = move_uci

        engine.board.pop()

    return best_move if best_move else random.choice(legal_moves)


def get_difficult_move(engine: ChessEngine) -> str:
    """Minimax with alpha-beta pruning, depth 3"""
    legal_moves = engine.get_legal_moves()
    ai_color = engine.board.turn

    best_move = None
    best_score = -float('inf')
    for move_uci in legal_moves:
        engine.board.push_uci(move_uci)
        score = minimax(
            engine.board,
            depth=3,
            alpha=-float('inf'),
            beta=float('inf'),
            is_maximizing=engine.board.turn == chess.WHITE
        )
        score = score if ai_color == chess.WHITE else -score
        engine.board.pop()

        if score > best_score:
            best_score = score
            best_move = move_uci
    return best_move if best_move else random.choice(legal_moves)


def minimax(board: chess.Board, depth: int, alpha: float, beta: float, is_maximizing: bool) -> float:
    """Minimax with alpha-beta pruning

    Args:
        board: chess.Board object
        depth: Remaining search depth (0 = leaf node)
        alpha: Best score maximizer can guarantee
        beta: Best score minimizer can guarantee
        is_maximizing: True if maximizing player's turn, False if minimizing

    Returns:
        Evaluation score of the position
    """
    if depth == 0 or board.is_game_over():
        return evaluate_position(board)

    if is_maximizing:
        max_score = -float('inf')
        for move in board.legal_moves:
            board.push(move)
            score = minimax(board, depth - 1, alpha, beta, False)
            board.pop()
            max_score = max(max_score, score)
            alpha = max(alpha, max_score)
            if beta <= alpha:
                break  # Beta cutoff
        return max_score
    else:
        min_score = float('inf')
        for move in board.legal_moves:
            board.push(move)
            score = minimax(board, depth - 1, alpha, beta, True)
            board.pop()
            min_score = min(min_score, score)
            beta = min(beta, min_score)
            if beta <= alpha:
                break  # Alpha cutoff
        return min_score
