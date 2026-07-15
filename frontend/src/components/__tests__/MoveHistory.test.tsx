import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MoveHistory } from '../MoveHistory'

describe('MoveHistory Component', () => {
  it('displays move pairs converted to standard algebraic notation', () => {
    render(<MoveHistory moves={['e2e4', 'e7e5', 'g1f3']} />)
    expect(screen.getByText('e4')).toBeInTheDocument()
    expect(screen.getByText('e5')).toBeInTheDocument()
    expect(screen.getByText('Nf3')).toBeInTheDocument()
  })

  it('displays move numbers', () => {
    render(<MoveHistory moves={['e2e4', 'e7e5']} />)
    expect(screen.getByText('1.')).toBeInTheDocument()
  })

  it('handles empty move list', () => {
    render(<MoveHistory moves={[]} />)
    expect(screen.getByText('Move History')).toBeInTheDocument()
  })

  it('marks captures with "x"', () => {
    render(<MoveHistory moves={['e2e4', 'd7d5', 'e4d5']} />)
    expect(screen.getByText('exd5')).toBeInTheDocument()
  })

  it('marks checks and checkmate', () => {
    // Fool's mate
    render(<MoveHistory moves={['f2f3', 'e7e5', 'g2g4', 'd8h4']} />)
    expect(screen.getByText('Qh4#')).toBeInTheDocument()
  })

  it('formats kingside castling as O-O', () => {
    render(<MoveHistory moves={['e2e4', 'e7e5', 'g1f3', 'b8c6', 'f1c4', 'g8f6', 'e1g1']} />)
    expect(screen.getByText('O-O')).toBeInTheDocument()
  })

  it('falls back to the raw UCI string for an unreplayable move', () => {
    render(<MoveHistory moves={['e2e4', 'a1a1']} />)
    expect(screen.getByText('e4')).toBeInTheDocument()
    expect(screen.getByText('a1a1')).toBeInTheDocument()
  })
})
