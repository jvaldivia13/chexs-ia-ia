import React from 'react'
import type { GameStatus } from '../types/chess'
import styles from '../styles/Status.module.css'

interface Props {
  status: GameStatus
  playerInCheck: boolean
}

export const GameStatusDisplay: React.FC<Props> = ({ status, playerInCheck }) => {
  const getStatusText = () => {
    if (playerInCheck) return 'You are in check!'
    if (status === 'checkmate') return 'Checkmate! AI wins.'
    if (status === 'stalemate') return 'Stalemate. Draw.'
    if (status === 'draw') return 'Draw.'
    return 'Game in progress'
  }

  return (
    <div className={`${styles.status} ${status === 'ongoing' ? '' : styles.ended}`}>
      {getStatusText()}
    </div>
  )
}
