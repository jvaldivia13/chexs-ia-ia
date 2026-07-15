import React from 'react'
import styles from '../styles/Controls.module.css'

interface Props {
  onNewGame: () => void
  onUndo: () => void
  disabled: boolean
}

export const GameControls: React.FC<Props> = ({ onNewGame, onUndo, disabled }) => {
  return (
    <div className={styles.controls}>
      <button onClick={onNewGame} disabled={disabled}>
        New Game
      </button>
      <button onClick={onUndo} disabled title="Deshacer aun no esta disponible">
        Undo
      </button>
    </div>
  )
}
