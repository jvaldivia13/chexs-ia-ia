import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MoveHistory } from '../MoveHistory'

describe('MoveHistory Component', () => {
  it('displays move pairs correctly', () => {
    render(<MoveHistory moves={['e2e4', 'e7e5', 'g1f3']} />)
    expect(screen.getByText('e2e4')).toBeInTheDocument()
    expect(screen.getByText('e7e5')).toBeInTheDocument()
  })

  it('displays move numbers', () => {
    render(<MoveHistory moves={['e2e4', 'e7e5']} />)
    expect(screen.getByText('1.')).toBeInTheDocument()
  })

  it('handles empty move list', () => {
    render(<MoveHistory moves={[]} />)
    expect(screen.getByText('Move History')).toBeInTheDocument()
  })
})
