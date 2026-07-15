import React, { useMemo } from 'react'
import { Chess } from 'chess.js'
import styles from '../styles/History.module.css'

interface Props {
  moves: string[]
}

function parseUci(uci: string) {
  return {
    from: uci.slice(0, 2),
    to: uci.slice(2, 4),
    promotion: uci.length > 4 ? uci.slice(4) : undefined
  }
}

// Backend sends moves as UCI coordinates (e.g. "e7e8q"); replay them through
// chess.js to recover standard algebraic notation (captures, checks/mate,
// castling, promotion, disambiguation) without changing the API contract.
function toSan(moves: string[]): string[] {
  const chess = new Chess()
  return moves.map((uci) => {
    try {
      const { from, to, promotion } = parseUci(uci)
      const move = chess.move({ from, to, promotion })
      return move.san
    } catch {
      return uci
    }
  })
}

export const MoveHistory: React.FC<Props> = ({ moves }) => {
  const sanMoves = useMemo(() => toSan(moves), [moves])

  const pairs = []
  for (let i = 0; i < sanMoves.length; i += 2) {
    pairs.push({
      number: (i / 2) + 1,
      white: sanMoves[i] || '',
      black: sanMoves[i + 1] || ''
    })
  }

  return (
    <div className={styles.history}>
      <h3>Move History</h3>
      <div className={styles.scroll}>
        <table>
          <tbody>
            {pairs.map((pair) => (
              <tr key={pair.number}>
                <td>{pair.number}.</td>
                <td>{pair.white}</td>
                <td>{pair.black}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
