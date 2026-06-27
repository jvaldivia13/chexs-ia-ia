import axios from 'axios'
import { NewGameResponse, MoveRequest, MoveResponse, GameStateResponse } from '../types/api'

const API_BASE = '/api'

export const api = {
  async newGame(difficulty: string): Promise<NewGameResponse> {
    const response = await axios.post(`${API_BASE}/game/new`, { difficulty })
    return response.data
  },

  async makeMove(fromSquare: string, toSquare: string, promotion?: string): Promise<MoveResponse> {
    const response = await axios.post(`${API_BASE}/game/move`, {
      from_square: fromSquare,
      to_square: toSquare,
      promotion: promotion || null
    })
    return response.data
  },

  async getGameState(): Promise<GameStateResponse> {
    const response = await axios.get(`${API_BASE}/game/state`)
    return response.data
  }
}
