export type Piece = 'K' | 'Q' | 'R' | 'B' | 'N' | 'P' | 'k' | 'q' | 'r' | 'b' | 'n' | 'p' | null
export type Square = string // "a1", "e4", etc.
export type Difficulty = 'easy' | 'normal' | 'difficult'
export type GameStatus = 'ongoing' | 'checkmate' | 'stalemate' | 'draw'
export type Color = 'white' | 'black'
export type GameMode = 'human_vs_ai' | 'ai_vs_ai'
export type AgentPersona = 'balanced' | 'aggressive' | 'defensive' | 'tactical'
export type AgentProvider = 'local' | 'openai' | 'deepseek'

export interface AgentProfile {
  name: string
  persona: AgentPersona
  expertise: Difficulty
  provider: AgentProvider
  model?: string | null
}

export interface NewGameConfig {
  mode: GameMode
  difficulty: Difficulty
  whiteAgent: AgentProfile
  blackAgent: AgentProfile
}

export interface Move {
  from: Square
  to: Square
  promotion?: 'Q' | 'R' | 'B' | 'N'
}

export interface GameState {
  gameId: string
  fen: string
  turn: Color
  status: GameStatus
  legalMoves: Square[]
  playerInCheck: boolean
  mode: GameMode
  whiteAgent?: AgentProfile
  blackAgent?: AgentProfile
  lastMove?: Move
}

export interface MoveRecord {
  moveNumber: number
  white: string
  black?: string
}
