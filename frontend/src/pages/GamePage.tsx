import React, { useEffect, useRef, useState } from 'react'
import { Board } from '../components/Board'
import { MoveHistory } from '../components/MoveHistory'
import { GameControls } from '../components/GameControls'
import { DifficultySelect } from '../components/DifficultySelect'
import { GameStatusDisplay } from '../components/GameStatus'
import { useGameState } from '../hooks/useGameState'
import type { NewGameConfig } from '../types/chess'

export const GamePage: React.FC = () => {
  const { gameState, moveHistory, loading, newGame, makeMove, playAgentTurn, undoMove } = useGameState()
  const [showDifficultySelect, setShowDifficultySelect] = useState(true)
  const [agentThinking, setAgentThinking] = useState(false)
  const turnTimer = useRef<number | null>(null)

  const handleSelectDifficulty = async (config: NewGameConfig) => {
    await newGame(config)
    setShowDifficultySelect(false)
  }

  const handleNewGame = () => {
    if (turnTimer.current) {
      window.clearTimeout(turnTimer.current)
      turnTimer.current = null
    }
    setAgentThinking(false)
    setShowDifficultySelect(true)
  }

  const handleMove = async (from: string, to: string, promotion?: string) => {
    return await makeMove(from, to, promotion)
  }

  useEffect(() => {
    return () => {
      if (turnTimer.current) {
        window.clearTimeout(turnTimer.current)
        turnTimer.current = null
      }
    }
  }, [])

  useEffect(() => {
    if (!gameState || showDifficultySelect || loading || gameState.status !== 'ongoing') {
      return
    }

    const shouldPlayAgent =
      gameState.mode === 'ai_vs_ai' ||
      (gameState.mode === 'human_vs_ai' && gameState.turn === 'black')

    if (!shouldPlayAgent || turnTimer.current) {
      return
    }

    setAgentThinking(true)
    turnTimer.current = window.setTimeout(async () => {
      turnTimer.current = null
      await playAgentTurn()
      setAgentThinking(false)
    }, 2000)
  }, [gameState, loading, playAgentTurn, showDifficultySelect])

  if (showDifficultySelect) {
    return <DifficultySelect onSelect={handleSelectDifficulty} />
  }

  if (!gameState) {
    return <div>Loading...</div>
  }

  return (
    <div className="game-container">
      <h1>{gameState.mode === 'ai_vs_ai' ? 'IA vs IA' : 'Humano vs IA'}</h1>
      <div className="game-layout">
        <div className="board-section">
          <div className="agent-summary">
            {gameState.mode === 'ai_vs_ai' && gameState.whiteAgent && (
              <span>
                Blancas: {gameState.whiteAgent.name} · {gameState.whiteAgent.provider} · {gameState.whiteAgent.model || 'local'} · {gameState.whiteAgent.persona}
              </span>
            )}
            {gameState.blackAgent && (
              <span>
                Negras: {gameState.blackAgent.name} · {gameState.blackAgent.provider} · {gameState.blackAgent.model || 'local'} · {gameState.blackAgent.persona}
              </span>
            )}
          </div>
          <Board
            fen={gameState.fen}
            onMove={handleMove}
            disabled={
              loading ||
              agentThinking ||
              gameState.status !== 'ongoing' ||
              gameState.mode === 'ai_vs_ai' ||
              gameState.turn !== 'white'
            }
          />
          <div className="turn-indicator">
            Turno: {gameState.turn === 'white' ? 'blancas' : 'negras'}
            {agentThinking ? ' · IA pensando' : ''}
          </div>
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
