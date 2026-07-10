import type { AgentProfile, GameMode } from './chess'

export interface NewGameResponse {
  game_id: string
  board_fen: string
  player_color: 'white'
  message: string
  mode: GameMode
  white_agent: AgentProfile
  black_agent: AgentProfile
}

export interface MoveRequest {
  game_id?: string
  from_square: string
  to_square: string
  promotion?: 'Q' | 'R' | 'B' | 'N'
  auto_reply?: boolean
}

export interface MoveResponse {
  player_move: string
  ai_move: string | null
  board_fen: string
  game_status: 'ongoing' | 'checkmate' | 'stalemate' | 'draw'
  legal_moves: string[]
  player_in_check: boolean
  turn: 'white' | 'black'
  move_history: string[]
}

export interface AgentTurnResponse {
  agent_move: string | null
  agent_color: 'white' | 'black'
  agent_name: string
  agent_profile: AgentProfile
  a2a_message_id: string
  board_fen: string
  game_status: 'ongoing' | 'checkmate' | 'stalemate' | 'draw'
  legal_moves: string[]
  player_in_check: boolean
  turn: 'white' | 'black'
  move_history: string[]
}

export interface GameStateResponse {
  board_fen: string
  game_status: 'ongoing' | 'checkmate' | 'stalemate' | 'draw'
  turn: 'white' | 'black'
  mode: GameMode
  white_agent: AgentProfile
  black_agent: AgentProfile
  move_history: string[]
}
