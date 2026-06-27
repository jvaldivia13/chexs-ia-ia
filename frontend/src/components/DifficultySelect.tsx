import React, { useState } from 'react'
import type { Difficulty } from '../types/chess'
import styles from '../styles/Difficulty.module.css'

interface Props {
  onSelect: (difficulty: Difficulty) => void
}

export const DifficultySelect: React.FC<Props> = ({ onSelect }) => {
  const [selected, setSelected] = useState<Difficulty>('normal')

  const handleStart = () => {
    onSelect(selected)
  }

  return (
    <div className={styles.modal}>
      <div className={styles.container}>
        <h2>Choose Difficulty</h2>
        <div className={styles.options}>
          {(['easy', 'normal', 'difficult'] as Difficulty[]).map((level) => (
            <label key={level}>
              <input
                type="radio"
                name="difficulty"
                value={level}
                checked={selected === level}
                onChange={(e) => setSelected(e.target.value as Difficulty)}
              />
              {level.charAt(0).toUpperCase() + level.slice(1)}
            </label>
          ))}
        </div>
        <button onClick={handleStart} className={styles.startButton}>
          Start Game
        </button>
      </div>
    </div>
  )
}
