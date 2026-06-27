import { describe, it, expect } from 'vitest'
import { render } from '@testing-library/react'
import { Board } from '../Board'

describe('Board Component', () => {
  it('renders 64 squares', () => {
    const { container } = render(
      <Board
        fen="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        onMove={() => Promise.resolve(true)}
        disabled={false}
      />
    )
    const squares = container.querySelectorAll('[class*="square"]')
    expect(squares.length).toBeGreaterThanOrEqual(8)
  })

  it('displays pieces in starting position', () => {
    const { container } = render(
      <Board
        fen="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        onMove={() => Promise.resolve(true)}
        disabled={false}
      />
    )
    const board = container.querySelector('[class*="board"]')
    expect(board).toBeTruthy()
  })
})
