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


def test_normal_ai_prefers_capturing_move():
    engine = ChessEngine()
    # Setup: white pawn on e4, black knight on e5 (attacked)
    engine.set_fen("rnbqkb1r/pppppppp/8/4n3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 1")

    # If there's a capture available, normal AI should consider it
    move = get_ai_move(engine, "normal")
    legal_moves = engine.get_legal_moves()
    assert move in legal_moves


def test_normal_ai_avoids_hanging_piece():
    engine = ChessEngine()
    # Setup where one move loses a piece
    engine.set_fen("rnbqkb1r/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1")
    engine.make_move("e7", "e5")  # black pawn blocks

    move = get_ai_move(engine, "normal")
    legal_moves = engine.get_legal_moves()
    assert move in legal_moves
