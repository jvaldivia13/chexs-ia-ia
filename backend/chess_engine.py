import chess
from typing import List, Optional


class ChessEngine:
    def __init__(self):
        self.board = chess.Board()

    def get_fen(self) -> str:
        return self.board.fen()

    def set_fen(self, fen: str) -> None:
        self.board.set_fen(fen)

    def make_move(self, from_square: str, to_square: str, promotion: Optional[str] = None) -> bool:
        try:
            move_uci = from_square + to_square
            if promotion:
                promotion_map = {'Q': chess.QUEEN, 'R': chess.ROOK, 'B': chess.BISHOP, 'N': chess.KNIGHT}
                move = chess.Move.from_uci(move_uci + chess.piece_symbol(promotion_map[promotion]))
            else:
                move = chess.Move.from_uci(move_uci)

            if move in self.board.legal_moves:
                self.board.push(move)
                return True
            return False
        except:
            return False

    def get_legal_moves(self) -> List[str]:
        moves = []
        for move in self.board.legal_moves:
            moves.append(move.uci()[:4])  # Return as "e2e4" format
        return moves

    def is_checkmate(self) -> bool:
        return self.board.is_checkmate()

    def is_stalemate(self) -> bool:
        return self.board.is_stalemate()

    def is_check(self) -> bool:
        return self.board.is_check()

    def is_game_over(self) -> bool:
        return self.board.is_game_over()

    def get_game_status(self) -> str:
        if self.board.is_checkmate():
            return "checkmate"
        elif self.board.is_stalemate():
            return "stalemate"
        elif self.board.is_insufficient_material():
            return "draw"
        elif self.board.halfmove_clock >= 100:  # 50-move rule
            return "draw"
        return "ongoing"

    def get_move_history(self) -> List[str]:
        return [move.uci()[:4] for move in self.board.move_stack]

    def undo_move(self) -> bool:
        if len(self.board.move_stack) > 0:
            self.board.pop()
            return True
        return False
