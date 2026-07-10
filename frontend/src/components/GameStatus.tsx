import React from 'react'
import type { GameStatus } from '../types/chess'
import styles from '../styles/Status.module.css'

interface Props {
  status: GameStatus
  playerInCheck: boolean
}

export const GameStatusDisplay: React.FC<Props> = ({ status, playerInCheck }) => {
  const getStatusText = () => {
    if (playerInCheck) return 'Blancas en jaque'
    if (status === 'checkmate') return 'Jaque mate'
    if (status === 'stalemate') return 'Ahogado. Tablas.'
    if (status === 'draw') return 'Tablas.'
    return 'Partida en curso'
  }

  return (
    <div className={`${styles.status} ${status === 'ongoing' ? '' : styles.ended}`}>
      {getStatusText()}
    </div>
  )
}
