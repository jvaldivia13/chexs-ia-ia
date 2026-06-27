import React, { useState } from 'react'
import { Board } from '../components/Board'
import { MoveHistory } from '../components/MoveHistory'
import { GameControls } from '../components/GameControls'
import { DifficultySelect } from '../components/DifficultySelect'
import { GameStatusDisplay } from '../components/GameStatus'
import { useGameState } from '../hooks/useGameState'
import type { Difficulty } from '../types/chess'

export const GamePage: React.FC = () => {
  const { gameState, moveHistory, loading, newGame, makeMove, undoMove } = useGameState()
  const [showDifficultySelect, setShowDifficultySelect] = useState(true)

  const handleSelectDifficulty = async (selectedDifficulty: Difficulty) => {
    await newGame(selectedDifficulty)
    setShowDifficultySelect(false)
  }

  const handleNewGame = () => {
    setShowDifficultySelect(true)
  }

  const handleMove = async (from: string, to: string) => {
    return await makeMove(from, to)
  }

  if (showDifficultySelect) {
    return <DifficultySelect onSelect={handleSelectDifficulty} />
  }

  if (!gameState) {
    return <div>Loading...</div>
  }

  return (
    <div className="game-container">
      <h1>Chess vs AI</h1>
      <div className="game-layout">
        <div className="board-section">
          <Board
            fen={gameState.fen}
            onMove={handleMove}
            disabled={loading || gameState.status !== 'ongoing'}
          />
          <GameStatusDisplay
            status={gameState.status}
            playerInCheck={gameState.playerInCheck}
          />
          <GameControls
            onNewGame={handleNewGame}
            onUndo={undoMove}
            disabled={loading}
          />
        </div>
        <div className="history-section">
          <MoveHistory moves={moveHistory} />
        </div>
      </div>
    </div>
  )
}
