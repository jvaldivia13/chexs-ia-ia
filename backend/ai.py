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



# Chebyshev distance from the 4 center squares to each square (0 = center, 3 = edge).
# Used to reward driving a lone/outmatched king toward the edge, which is required
# technique to actually deliver mate rather than just holding a material lead.
_CENTER_DISTANCE = [
    3, 3, 3, 3, 3, 3, 3, 3,
    3, 2, 2, 2, 2, 2, 2, 3,
    3, 2, 1, 1, 1, 1, 2, 3,
    3, 2, 1, 0, 0, 1, 2, 3,
    3, 2, 1, 0, 0, 1, 2, 3,
    3, 2, 1, 1, 1, 1, 2, 3,
    3, 2, 2, 2, 2, 2, 2, 3,
    3, 3, 3, 3, 3, 3, 3, 3,
]

# Roughly a rook's worth of material lead -- below this, chasing the enemy king
# is premature and the bonus stays off so it never outweighs tactical decisions.
_ENDGAME_MATERIAL_THRESHOLD = 5.0
_KING_HUNT_WEIGHT = 0.15
_KING_PROXIMITY_WEIGHT = 0.1


def _king_hunt_bonus(board: chess.Board, material_score: float) -> float:
    """
    Once one side has a decisive material lead, reward pushing the weaker
    king toward the edge and bringing the stronger king closer to it.

    Without this, every move that keeps the material lead scores identically,
    so the AI has no signal to make progress and shuffles pieces instead of
    finishing the game.
    """
    if abs(material_score) < _ENDGAME_MATERIAL_THRESHOLD:
        return 0.0

    stronger_color = chess.WHITE if material_score > 0 else chess.BLACK
    weaker_color = not stronger_color

    strong_king = board.king(stronger_color)
    weak_king = board.king(weaker_color)
    if strong_king is None or weak_king is None:
        return 0.0

    push_to_edge = _CENTER_DISTANCE[weak_king] * _KING_HUNT_WEIGHT
    bring_kings_together = (7 - chess.square_distance(strong_king, weak_king)) * _KING_PROXIMITY_WEIGHT

    bonus = push_to_edge + bring_kings_together
    return bonus if stronger_color == chess.WHITE else -bonus


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

    material_score = 0.0

    # Material count
    for piece_type, value in piece_values.items():
        white_count = len(board.pieces(piece_type, chess.WHITE))
        black_count = len(board.pieces(piece_type, chess.BLACK))
        material_score += (white_count - black_count) * value

    score = material_score

    # Simple positional bonus: center control
    center_squares = [chess.E4, chess.D4, chess.E5, chess.D5]
    for sq in center_squares:
        if board.piece_at(sq) and board.piece_at(sq).color == chess.WHITE:
            score += 0.5
        elif board.piece_at(sq) and board.piece_at(sq).color == chess.BLACK:
            score -= 0.5

    score += _king_hunt_bonus(board, material_score)

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
