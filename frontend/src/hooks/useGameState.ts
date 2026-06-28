import { useState, useCallback } from 'react'
import type { GameState, Difficulty } from '../types/chess'
import { api } from '../services/api'

export function useGameState() {
  const [gameState, setGameState] = useState<GameState | null>(null)
  const [difficulty, setDifficulty] = useState<Difficulty>('normal')
  const [moveHistory, setMoveHistory] = useState<string[]>([])
  const [loading, setLoading] = useState(false)

  const newGame = useCallback(async (selectedDifficulty: Difficulty) => {
    setLoading(true)
    try {
      const response = await api.newGame(selectedDifficulty)
      setDifficulty(selectedDifficulty)
      setGameState({
        fen: response.board_fen,
        turn: 'white',
        status: 'ongoing',
        legalMoves: [],
        playerInCheck: false
      })
      setMoveHistory([])
    } catch (error) {
      console.error('Failed to start new game:', error)
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
    try {
      console.log('Making move:', { from, to, promotion })
      const response = await api.makeMove(from, to, promotion)
      console.log('Move response:', response)

      setGameState({
        fen: response.board_fen,
        turn: response.game_status === 'ongoing' ? 'white' : 'black',
        status: response.game_status as any,
        legalMoves: response.legal_moves,
        playerInCheck: response.player_in_check
      })

      const newMoves = [...moveHistory]
      if (response.player_move) newMoves.push(response.player_move)
      if (response.ai_move) newMoves.push(response.ai_move)
      setMoveHistory(newMoves)

      return true
    } catch (error) {
      console.error('Move failed:', error)
      return false
    } finally {
      setLoading(false)
    }
  }, [gameState, moveHistory])

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
    newGame,
    makeMove,
    undoMove
  }
}
