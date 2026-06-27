export type Piece = 'K' | 'Q' | 'R' | 'B' | 'N' | 'P' | 'k' | 'q' | 'r' | 'b' | 'n' | 'p' | null
export type Square = string // "a1", "e4", etc.
export type Difficulty = 'easy' | 'normal' | 'difficult'
export type GameStatus = 'ongoing' | 'checkmate' | 'stalemate' | 'draw'
export type Color = 'white' | 'black'

export interface Move {
  from: Square
  to: Square
  promotion?: 'Q' | 'R' | 'B' | 'N'
}

export interface GameState {
  fen: string
  turn: Color
  status: GameStatus
  legalMoves: Square[]
  playerInCheck: boolean
  lastMove?: Move
}

export interface MoveRecord {
  moveNumber: number
  white: string
  black?: string
}
