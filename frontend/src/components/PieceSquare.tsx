import React from 'react'
import styles from '../styles/Board.module.css'

const PIECE_SYMBOLS: Record<string, string> = {
  K: '\u2654',
  Q: '\u2655',
  R: '\u2656',
  B: '\u2657',
  N: '\u2658',
  P: '\u2659',
  k: '\u265A',
  q: '\u265B',
  r: '\u265C',
  b: '\u265D',
  n: '\u265E',
  p: '\u265F'
}

interface Props {
  square: string
  piece: string | null
  isLight: boolean
  isSelected: boolean
  isLegal: boolean
  isCapture: boolean
  onClick: (square: string) => void
}

export const PieceSquare: React.FC<Props> = ({
  square,
  piece,
  isLight,
  isSelected,
  isLegal,
  isCapture,
  onClick
}) => {
  const pieceClass = piece && piece === piece.toUpperCase() ? styles.whitePiece : styles.blackPiece

  return (
    <div
      role="button"
      aria-label={square}
      className={`
        ${styles.square}
        ${isLight ? styles.light : styles.dark}
        ${isSelected ? styles.selected : ''}
        ${isLegal ? styles.legal : ''}
        ${isCapture ? styles.capture : ''}
      `}
      onClick={() => onClick(square)}
    >
      {piece && <span className={`${styles.piece} ${pieceClass}`}>{PIECE_SYMBOLS[piece]}</span>}
    </div>
  )
}
