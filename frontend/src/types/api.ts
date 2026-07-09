export interface NewGameResponse {
  game_id: string
  board_fen: string
  player_color: 'white'
  message: string
}

export interface MoveRequest {
  game_id?: string
  from_square: string
  to_square: string
  promotion?: 'Q' | 'R' | 'B' | 'N'
}

export interface MoveResponse {
  player_move: string
  ai_move: string | null
  board_fen: string
  game_status: 'ongoing' | 'checkmate' | 'stalemate' | 'draw'
  legal_moves: string[]
  player_in_check: boolean
}

export interface GameStateResponse {
  board_fen: string
  game_status: 'ongoing' | 'checkmate' | 'stalemate' | 'draw'
  turn: 'white' | 'black'
}
