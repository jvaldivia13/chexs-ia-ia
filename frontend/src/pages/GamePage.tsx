import React, { useEffect, useRef, useState } from 'react'
import { Board } from '../components/Board'
import { MoveHistory } from '../components/MoveHistory'
import { GameControls } from '../components/GameControls'
import { DifficultySelect } from '../components/DifficultySelect'
import { GameStatusDisplay } from '../components/GameStatus'
import { TurnTimers, type PlayerTiming } from '../components/TurnTimers'
import { useGameState } from '../hooks/useGameState'
import type { NewGameConfig } from '../types/chess'

export const GamePage: React.FC = () => {
  const { gameState, moveHistory, loading, error, newGame, makeMove, playAgentTurn, undoMove } = useGameState()
  const [showDifficultySelect, setShowDifficultySelect] = useState(true)
  const [agentThinking, setAgentThinking] = useState(false)
  const turnTimer = useRef<number | null>(null)
  const turnStarted = useRef<{ gameId: string; color: 'white' | 'black'; at: number; moveCount: number } | null>(null)
  const [currentTurnMs, setCurrentTurnMs] = useState(0)
  const [timings, setTimings] = useState<Record<'white' | 'black', PlayerTiming>>({
    white: { lastMs: null, totalMs: 0, moves: 0 },
    black: { lastMs: null, totalMs: 0, moves: 0 },
  })

  const resetTimings = () => {
    turnStarted.current = null
    setCurrentTurnMs(0)
    setTimings({
      white: { lastMs: null, totalMs: 0, moves: 0 },
      black: { lastMs: null, totalMs: 0, moves: 0 },
    })
  }

  const handleSelectDifficulty = async (config: NewGameConfig) => {
    resetTimings()
    await newGame(config)
    setShowDifficultySelect(false)
  }

  const handleNewGame = () => {
    if (turnTimer.current) {
      window.clearTimeout(turnTimer.current)
      turnTimer.current = null
    }
    setAgentThinking(false)
    resetTimings()
    setShowDifficultySelect(true)
  }

  const handleMove = async (from: string, to: string, promotion?: string) => {
    return await makeMove(from, to, promotion)
  }

  useEffect(() => {
    if (!gameState || showDifficultySelect) return

    const now = performance.now()
    const previous = turnStarted.current
    const isNewGame = !previous || previous.gameId !== gameState.gameId

    if (!isNewGame && previous.color !== gameState.turn && moveHistory.length > previous.moveCount) {
      const elapsed = now - previous.at
      setTimings(current => ({
        ...current,
        [previous.color]: {
          lastMs: elapsed,
          totalMs: current[previous.color].totalMs + elapsed,
          moves: current[previous.color].moves + 1,
        },
      }))
    }

    if (isNewGame || previous.color !== gameState.turn) {
      turnStarted.current = {
        gameId: gameState.gameId,
        color: gameState.turn,
        at: now,
        moveCount: moveHistory.length,
      }
      setCurrentTurnMs(0)
    }
  }, [gameState, moveHistory.length, showDifficultySelect])

  useEffect(() => {
    if (!gameState || showDifficultySelect || gameState.status !== 'ongoing') return
    const interval = window.setInterval(() => {
      if (turnStarted.current) {
        setCurrentTurnMs(performance.now() - turnStarted.current.at)
      }
    }, 100)
    return () => window.clearInterval(interval)
  }, [gameState, gameState?.turn, gameState?.status, showDifficultySelect])

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
      {error && <div className="error-banner" role="alert">{error}</div>}
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
            lastMove={moveHistory[moveHistory.length - 1]}
            disabled={
              loading ||
              agentThinking ||
              gameState.status !== 'ongoing' ||
              gameState.mode === 'ai_vs_ai' ||
              gameState.turn !== 'white'
            }
          />
          <TurnTimers
            activeColor={gameState.turn}
            currentMs={currentTurnMs}
            white={timings.white}
            black={timings.black}
            whiteName={gameState.whiteAgent?.name || 'Jugador'}
            blackName={gameState.blackAgent?.name || 'IA'}
            running={gameState.status === 'ongoing'}
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
