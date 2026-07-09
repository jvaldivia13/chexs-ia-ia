import pytest
from chess_engine import ChessEngine

def test_init_board_is_start_position():
    engine = ChessEngine()
    assert engine.get_fen() == "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

def test_make_valid_move():
    engine = ChessEngine()
    result = engine.make_move("e2", "e4")
    assert result is True
    # Verify the pawn is now at e4 (shown as 4P in the FEN rank)
    assert engine.get_fen() == "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1"

def test_make_invalid_move():
    engine = ChessEngine()
    result = engine.make_move("e1", "e4")
    assert result is False

def test_get_legal_moves_from_start():
    engine = ChessEngine()
    moves = engine.get_legal_moves()
    assert len(moves) == 20  # 16 pawn moves + 4 knight moves

def test_detect_checkmate():
    engine = ChessEngine()
    # Fool's mate: 1.f3 e5 2.g4 Qh4#
    engine.make_move("f2", "f3")
    engine.make_move("e7", "e5")
    engine.make_move("g2", "g4")
    engine.make_move("d8", "h4")
    assert engine.is_checkmate() is True

def test_detect_stalemate():
    engine = ChessEngine()
    # Load a stalemate position (black king on h8, white queen on f7, white king on g6)
    engine.set_fen("7k/5Q2/6K1/8/8/8/8/8 b - - 0 1")
    assert engine.is_stalemate() is True

def test_castling():
    engine = ChessEngine()
    engine.set_fen("r3k2r/pppppppp/8/8/8/8/PPPPPPPP/R3K2R w KQkq - 0 1")
    assert engine.make_move("e1", "g1") is True  # kingside castling

def test_en_passant():
    engine = ChessEngine()
    # Black pawn on d4, white pawn just moved e2-e4, en passant square is e3
    engine.set_fen("rnbqkbnr/pppppppp/8/8/3pP3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1")
    assert engine.make_move("d4", "e3") is True  # en passant capture

def test_pawn_promotion_keeps_full_uci_move():
    engine = ChessEngine()
    engine.set_fen("4k3/P7/8/8/8/8/8/4K3 w - - 0 1")
    assert "a7a8q" in engine.get_legal_moves()
    assert engine.make_move("a7", "a8", "Q") is True
    assert engine.get_move_history()[-1] == "a7a8q"
