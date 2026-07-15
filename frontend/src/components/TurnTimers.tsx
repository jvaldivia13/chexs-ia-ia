import React from 'react'
import type { Color } from '../types/chess'

export interface PlayerTiming {
  lastMs: number | null
  totalMs: number
  moves: number
}

interface Props {
  activeColor: Color
  currentMs: number
  white: PlayerTiming
  black: PlayerTiming
  whiteName: string
  blackName: string
  running: boolean
}

const formatTime = (milliseconds: number | null) => {
  if (milliseconds === null) return '—'
  return `${(milliseconds / 1000).toFixed(1)} s`
}

export const TurnTimers: React.FC<Props> = ({
  activeColor,
  currentMs,
  white,
  black,
  whiteName,
  blackName,
  running,
}) => {
  const renderPlayer = (color: Color, name: string, timing: PlayerTiming) => {
    const active = running && activeColor === color
    const average = timing.moves ? timing.totalMs / timing.moves : null

    return (
      <div className={`player-timer ${active ? 'player-timer--active' : ''}`}>
        <div className="player-timer__heading">
          <span className={`player-timer__piece player-timer__piece--${color}`} aria-hidden="true" />
          <strong>{name}</strong>
          {active && <span className="player-timer__live">pensando</span>}
        </div>
        <div className="player-timer__current">{active ? formatTime(currentMs) : formatTime(timing.lastMs)}</div>
        <div className="player-timer__stats">
          <span>Última: {formatTime(timing.lastMs)}</span>
          <span>Promedio: {formatTime(average)}</span>
          <span>Jugadas: {timing.moves}</span>
        </div>
      </div>
    )
  }

  return (
    <section className="turn-timers" aria-label="Tiempo de los oponentes">
      {renderPlayer('white', whiteName, white)}
      {renderPlayer('black', blackName, black)}
    </section>
  )
}
