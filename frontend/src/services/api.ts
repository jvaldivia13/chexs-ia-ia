import axios from 'axios'
import type { AgentTurnResponse, NewGameResponse, MoveResponse, GameStateResponse } from '../types/api'
import type { NewGameConfig } from '../types/chess'

const API_BASE = '/api'

export const api = {
  async newGame(config: NewGameConfig): Promise<NewGameResponse> {
    const response = await axios.post(`${API_BASE}/game/new`, {
      difficulty: config.difficulty,
      mode: config.mode,
      white_agent: config.whiteAgent,
      black_agent: config.blackAgent
    })
    return response.data
  },

  async makeMove(
    gameId: string,
    fromSquare: string,
    toSquare: string,
    promotion?: string,
    autoReply = false
  ): Promise<MoveResponse> {
    const response = await axios.post(`${API_BASE}/game/move`, {
      game_id: gameId,
      from_square: fromSquare,
      to_square: toSquare,
      promotion: promotion || null,
      auto_reply: autoReply
    })
    return response.data
  },

  async playAgentTurn(gameId: string): Promise<AgentTurnResponse> {
    const response = await axios.post(`${API_BASE}/game/agent-turn`, { game_id: gameId })
    return response.data
  },

  async getGameState(gameId?: string): Promise<GameStateResponse> {
    const response = await axios.get(`${API_BASE}/game/state`, {
      params: gameId ? { game_id: gameId } : undefined
    })
    return response.data
  }
}
