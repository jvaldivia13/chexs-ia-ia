import React, { useState, useEffect } from 'react'
import { Chess, type Square } from 'chess.js'
import { PieceSquare } from './PieceSquare'
import styles from '../styles/Board.module.css'

interface BoardProps {
  fen: string
  onMove: (from: string, to: string) => Promise<boolean>
  disabled: boolean
}

export const Board: React.FC<BoardProps> = ({ fen, onMove, disabled }) => {
  const [chess, setChess] = useState(new Chess(fen))
  const [selectedSquare, setSelectedSquare] = useState<string | null>(null)
  const [legalMoves, setLegalMoves] = useState<string[]>([])

  useEffect(() => {
    const newChess = new Chess(fen)
    setChess(newChess)
    setSelectedSquare(null)
    setLegalMoves([])
  }, [fen])

  const handleSquareClick = async (square: string) => {
    if (disabled) return

    if (selectedSquare === null) {
      // Select piece
      const moves = chess.moves({ square: square as Square, verbose: true })
      if (moves.length > 0) {
        setSelectedSquare(square)
        setLegalMoves(moves.map((m) => m.to))
      }
    } else if (selectedSquare === square) {
      // Deselect
      setSelectedSquare(null)
      setLegalMoves([])
    } else {
      // Try move
      const success = await onMove(selectedSquare, square)
      if (success) {
        setSelectedSquare(null)
        setLegalMoves([])
      }
    }
  }

  const squares: Array<string> = []
  for (let rank = 8; rank >= 1; rank--) {
    for (let file = 0; file < 8; file++) {
      const square = String.fromCharCode(97 + file) + rank
      squares.push(square)
    }
  }

  return (
    <div className={styles.board}>
      {squares.map((square) => {
        const squareIndex = (8 - parseInt(square[1])) * 8 + (square.charCodeAt(0) - 97)
        const isLight = (squareIndex % 2 === 0 && Math.floor(squareIndex / 8) % 2 === 0) ||
                        (squareIndex % 2 === 1 && Math.floor(squareIndex / 8) % 2 === 1)
        const piece = chess.get(square as Square)

        return (
          <PieceSquare
            key={square}
            square={square}
            piece={piece ? piece.color + piece.type.toUpperCase() : null}
            isLight={isLight}
            isSelected={selectedSquare === square}
            isLegal={legalMoves.includes(square)}
            onClick={handleSquareClick}
          />
        )
      })}
    </div>
  )
}
