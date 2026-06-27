import random
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


def get_normal_move(engine: ChessEngine) -> str:
    """
    Placeholder for normal difficulty AI.
    Currently returns a random legal move.
    """
    return random.choice(engine.get_legal_moves())


def get_difficult_move(engine: ChessEngine) -> str:
    """
    Placeholder for difficult difficulty AI.
    Currently returns a random legal move.
    """
    return random.choice(engine.get_legal_moves())
