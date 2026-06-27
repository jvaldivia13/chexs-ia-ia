import React from 'react'
import styles from '../styles/Board.module.css'

const PIECE_SYMBOLS: Record<string, string> = {
  'K': '♔', 'Q': '♕', 'R': '♖', 'B': '♗', 'N': '♘', 'P': '♙',
  'k': '♚', 'q': '♛', 'r': '♜', 'b': '♝', 'n': '♞', 'p': '♟'
}

interface Props {
  square: string
  piece: string | null
  isLight: boolean
  isSelected: boolean
  isLegal: boolean
  onClick: (square: string) => void
}

export const PieceSquare: React.FC<Props> = ({
  square,
  piece,
  isLight,
  isSelected,
  isLegal,
  onClick
}) => {
  return (
    <div
      className={`
        ${styles.square}
        ${isLight ? styles.light : styles.dark}
        ${isSelected ? styles.selected : ''}
        ${isLegal ? styles.legal : ''}
      `}
      onClick={() => onClick(square)}
    >
      {piece && <span className={styles.piece}>{PIECE_SYMBOLS[piece]}</span>}
    </div>
  )
}
