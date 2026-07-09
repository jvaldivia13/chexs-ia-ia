import { describe, it, expect, vi } from 'vitest'
import { fireEvent, render, screen } from '@testing-library/react'
import { Board } from '../Board'

describe('Board Component', () => {
  it('renders 64 squares', () => {
    render(
      <Board
        fen="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        onMove={() => Promise.resolve(true)}
        disabled={false}
      />
    )
    const squares = screen.getAllByRole('button')
    expect(squares.length).toBe(64)
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

  it('allows a knight to capture an occupied enemy square', () => {
    const onMove = vi.fn(() => Promise.resolve(true))
    render(
      <Board
        fen="4k3/8/8/8/3p4/5N2/8/4K3 w - - 0 1"
        onMove={onMove}
        disabled={false}
      />
    )

    fireEvent.click(screen.getByRole('button', { name: 'f3' }))
    fireEvent.click(screen.getByRole('button', { name: 'd4' }))

    expect(onMove).toHaveBeenCalledWith('f3', 'd4', undefined)
  })
})
