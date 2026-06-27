import pytest
from chess_engine import ChessEngine
from ai import get_ai_move


def test_easy_ai_returns_legal_move():
    engine = ChessEngine()
    engine.make_move("e2", "e4")  # white moves
    move = get_ai_move(engine, "easy")

    legal_moves = engine.get_legal_moves()
    assert move in legal_moves


def test_easy_ai_consistent_with_board():
    engine = ChessEngine()
    engine.make_move("e2", "e4")

    move = get_ai_move(engine, "easy")
    # Move should be a valid square notation
    assert len(move) == 4
    assert move in engine.get_legal_moves()
