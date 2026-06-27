import React from 'react'
import styles from '../styles/History.module.css'

interface Props {
  moves: string[]
}

export const MoveHistory: React.FC<Props> = ({ moves }) => {
  const pairs = []
  for (let i = 0; i < moves.length; i += 2) {
    pairs.push({
      number: (i / 2) + 1,
      white: moves[i] || '',
      black: moves[i + 1] || ''
    })
  }

  return (
    <div className={styles.history}>
      <h3>Move History</h3>
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
  )
}
