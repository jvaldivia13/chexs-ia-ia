import { useState, useCallback } from 'react'
import { GameState, Difficulty, Move } from '../types/chess'
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
        fen: response.boardFen,
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
    if (!gameState) return false

    setLoading(true)
    try {
      const response = await api.makeMove(from, to, promotion)

      setGameState({
        fen: response.boardFen,
        turn: response.gameStatus === 'ongoing' ? 'white' : 'black',
        status: response.gameStatus as any,
        legalMoves: response.legalMoves,
        playerInCheck: response.playerInCheck
      })

      const newMoves = [...moveHistory]
      if (response.playerMove) newMoves.push(response.playerMove)
      if (response.aiMove) newMoves.push(response.aiMove)
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
