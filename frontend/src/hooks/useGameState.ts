import { useState, useCallback } from 'react'
import axios from 'axios'
import type { Difficulty, GameState, NewGameConfig } from '../types/chess'
import { api } from '../services/api'

function describeError(error: unknown, fallback: string): string {
  if (axios.isAxiosError(error)) {
    const detail = error.response?.data?.detail
    if (typeof detail === 'string') return detail
    if (!error.response) return 'No se pudo conectar con el servidor.'
  }
  return fallback
}

export function useGameState() {
  const [gameState, setGameState] = useState<GameState | null>(null)
  const [difficulty, setDifficulty] = useState<Difficulty>('normal')
  const [moveHistory, setMoveHistory] = useState<string[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const newGame = useCallback(async (config: NewGameConfig) => {
    setLoading(true)
    setError(null)
    try {
      const response = await api.newGame(config)
      setDifficulty(config.difficulty)
      setGameState({
        gameId: response.game_id,
        fen: response.board_fen,
        turn: 'white',
        status: 'ongoing',
        legalMoves: [],
        playerInCheck: false,
        mode: response.mode,
        whiteAgent: response.white_agent,
        blackAgent: response.black_agent
      })
      setMoveHistory([])
    } catch (error) {
      console.error('Failed to start new game:', error)
      setError(describeError(error, 'No se pudo iniciar la partida.'))
    } finally {
      setLoading(false)
    }
  }, [])

  const makeMove = useCallback(async (from: string, to: string, promotion?: string) => {
    if (!gameState) {
      console.error('No game state')
      return false
    }

    setLoading(true)
    setError(null)
    try {
      const response = await api.makeMove(gameState.gameId, from, to, promotion, false)

      setGameState({
        gameId: gameState.gameId,
        fen: response.board_fen,
        turn: response.turn,
        status: response.game_status,
        legalMoves: response.legal_moves,
        playerInCheck: response.player_in_check,
        mode: gameState.mode,
        whiteAgent: gameState.whiteAgent,
        blackAgent: gameState.blackAgent
      })

      setMoveHistory(response.move_history)

      return true
    } catch (error) {
      console.error('Move failed:', error)
      setError(describeError(error, 'La jugada no pudo realizarse.'))
      return false
    } finally {
      setLoading(false)
    }
  }, [gameState])

  const playAgentTurn = useCallback(async () => {
    if (!gameState || gameState.status !== 'ongoing') {
      return false
    }

    setLoading(true)
    setError(null)
    try {
      const response = await api.playAgentTurn(gameState.gameId)
      setGameState({
        gameId: gameState.gameId,
        fen: response.board_fen,
        turn: response.turn,
        status: response.game_status,
        legalMoves: response.legal_moves,
        playerInCheck: response.player_in_check,
        mode: gameState.mode,
        whiteAgent: gameState.whiteAgent,
        blackAgent: gameState.blackAgent
      })
      setMoveHistory(response.move_history)
      return Boolean(response.agent_move)
    } catch (error) {
      console.error('Agent turn failed:', error)
      setError(describeError(error, 'El turno del agente IA fallo.'))
      return false
    } finally {
      setLoading(false)
    }
  }, [gameState])

  const undoMove = useCallback(() => {
    // Undo is complex—would require state tracking on backend
    // For MVP, not implementing full undo
    console.warn('Undo not implemented in MVP')
  }, [])

  return {
    gameState,
    difficulty,
    moveHistory,
    loading,
    error,
    newGame,
    makeMove,
    playAgentTurn,
    undoMove
  }
}
