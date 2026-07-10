import React, { useMemo, useState } from 'react'
import type { AgentPersona, AgentProfile, AgentProvider, Difficulty, GameMode, NewGameConfig } from '../types/chess'
import styles from '../styles/Difficulty.module.css'

interface Props {
  onSelect: (config: NewGameConfig) => void
}

const expertiseOptions: Difficulty[] = ['easy', 'normal', 'difficult']
const personaOptions: AgentPersona[] = ['balanced', 'aggressive', 'defensive', 'tactical']
const providerOptions: Array<{ label: string; value: AgentProvider; model: string | null }> = [
  { label: 'Local', value: 'local', model: null },
  { label: 'OpenAI o4-mini', value: 'openai', model: 'o4-mini' },
  { label: 'DeepSeek Reasoner', value: 'deepseek', model: 'deepseek-reasoner' }
]

export const DifficultySelect: React.FC<Props> = ({ onSelect }) => {
  const [mode, setMode] = useState<GameMode>('human_vs_ai')
  const [blackAgent, setBlackAgent] = useState<AgentProfile>({
    name: 'Nyx',
    persona: 'tactical',
    expertise: 'normal',
    provider: 'deepseek',
    model: 'deepseek-reasoner'
  })
  const [whiteAgent, setWhiteAgent] = useState<AgentProfile>({
    name: 'Atlas',
    persona: 'balanced',
    expertise: 'normal',
    provider: 'openai',
    model: 'o4-mini'
  })

  const title = useMemo(() => (
    mode === 'human_vs_ai' ? 'Humano vs IA' : 'IA vs IA'
  ), [mode])

  const updateAgent = (
    color: 'white' | 'black',
    field: keyof AgentProfile,
    value: string
  ) => {
    const setter = color === 'white' ? setWhiteAgent : setBlackAgent
    setter((agent) => ({ ...agent, [field]: value }))
  }

  const updateProvider = (color: 'white' | 'black', provider: AgentProvider) => {
    const selected = providerOptions.find((option) => option.value === provider)
    const setter = color === 'white' ? setWhiteAgent : setBlackAgent
    setter((agent) => ({
      ...agent,
      provider,
      model: selected?.model ?? null
    }))
  }

  const handleStart = () => {
    onSelect({
      mode,
      difficulty: blackAgent.expertise,
      whiteAgent,
      blackAgent
    })
  }

  return (
    <div className={styles.modal}>
      <div className={styles.container}>
        <h2>{title}</h2>
        <div className={styles.modeTabs}>
          <button
            className={mode === 'human_vs_ai' ? styles.activeTab : ''}
            onClick={() => setMode('human_vs_ai')}
          >
            Humano vs IA
          </button>
          <button
            className={mode === 'ai_vs_ai' ? styles.activeTab : ''}
            onClick={() => setMode('ai_vs_ai')}
          >
            IA vs IA
          </button>
        </div>

        <div className={styles.agentGrid}>
          {mode === 'ai_vs_ai' && (
            <AgentEditor
              title="IA blancas"
              color="white"
              agent={whiteAgent}
              onChange={updateAgent}
              onProviderChange={updateProvider}
            />
          )}
          <AgentEditor
            title="IA negras"
            color="black"
            agent={blackAgent}
            onChange={updateAgent}
            onProviderChange={updateProvider}
          />
        </div>

        <button onClick={handleStart} className={styles.startButton}>
          Iniciar partida
        </button>
      </div>
    </div>
  )
}

interface AgentEditorProps {
  title: string
  color: 'white' | 'black'
  agent: AgentProfile
  onChange: (color: 'white' | 'black', field: keyof AgentProfile, value: string) => void
  onProviderChange: (color: 'white' | 'black', provider: AgentProvider) => void
}

const AgentEditor: React.FC<AgentEditorProps> = ({ title, color, agent, onChange, onProviderChange }) => (
  <div className={styles.agentPanel}>
    <h3>{title}</h3>
    <label>
      Nombre
      <input
        value={agent.name}
        onChange={(event) => onChange(color, 'name', event.target.value)}
      />
    </label>
    <label>
      Perfil
      <select
        value={agent.persona}
        onChange={(event) => onChange(color, 'persona', event.target.value)}
      >
        {personaOptions.map((persona) => (
          <option key={persona} value={persona}>
            {persona}
          </option>
        ))}
      </select>
    </label>
    <label>
      Motor
      <select
        value={agent.provider}
        onChange={(event) => onProviderChange(color, event.target.value as AgentProvider)}
      >
        {providerOptions.map((provider) => (
          <option key={provider.value} value={provider.value}>
            {provider.label}
          </option>
        ))}
      </select>
    </label>
    <label>
      Expertise
      <select
        value={agent.expertise}
        onChange={(event) => onChange(color, 'expertise', event.target.value)}
      >
        {expertiseOptions.map((level) => (
          <option key={level} value={level}>
            {level}
          </option>
        ))}
      </select>
    </label>
    {agent.model && <div className={styles.modelName}>{agent.model}</div>}
  </div>
)
