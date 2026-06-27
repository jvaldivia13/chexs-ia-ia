export interface NewGameResponse {
  gameId: string
  boardFen: string
  playerColor: 'white'
  message: string
}

export interface MoveRequest {
  fromSquare: string
  toSquare: string
  promotion?: 'Q' | 'R' | 'B' | 'N'
}

export interface MoveResponse {
  playerMove: string
  aiMove: string | null
  boardFen: string
  gameStatus: 'ongoing' | 'checkmate' | 'stalemate' | 'draw'
  legalMoves: string[]
  playerInCheck: boolean
}

export interface GameStateResponse {
  boardFen: string
  gameStatus: 'ongoing' | 'checkmate' | 'stalemate' | 'draw'
  turn: 'white' | 'black'
}
