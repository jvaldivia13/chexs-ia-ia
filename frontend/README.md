# Frontend

Frontend React + TypeScript + Vite para la aplicacion **Chexs IA vs IA**.

## Responsabilidades

- Renderizar el tablero de ajedrez.
- Permitir seleccion de modo:
  - `Humano vs IA`
  - `IA vs IA`
- Configurar agentes:
  - Nombre.
  - Perfil.
  - Expertise.
  - Motor/modelo.
- Mostrar historial de jugadas.
- Deshabilitar el tablero cuando corresponde:
  - Mientras carga.
  - Durante turnos automaticos.
  - En modo `IA vs IA`.
- Ejecutar el loop visual de agentes con pausa minima de 2 segundos entre jugadas.

## Estructura

```text
frontend/
+-- src/
|   +-- components/
|   |   +-- Board.tsx
|   |   +-- PieceSquare.tsx
|   |   +-- DifficultySelect.tsx
|   |   +-- GameControls.tsx
|   |   +-- GameStatus.tsx
|   |   +-- MoveHistory.tsx
|   +-- hooks/
|   |   +-- useGameState.ts
|   +-- pages/
|   |   +-- GamePage.tsx
|   +-- services/
|   |   +-- api.ts
|   +-- styles/
|   +-- types/
|   +-- App.tsx
|   +-- main.tsx
+-- package.json
+-- vite.config.ts
+-- vitest.config.ts
```

## Scripts

```powershell
npm install
npm run dev
npm run build
npm run test -- --run
```

## Desarrollo

El servidor Vite corre en:

<http://localhost:5173>

El proxy de Vite envia `/api/*` al backend:

<http://localhost:8000>

Configuracion relevante en `vite.config.ts`:

```ts
server: {
  port: 5173,
  proxy: {
    '^/api/': {
      target: 'http://localhost:8000',
      rewrite: (path) => path.replace(/^\/api/, '')
    }
  }
}
```

## Motores Mostrados en UI

El selector de agentes permite:

| Label | Provider | Model |
| --- | --- | --- |
| Local | `local` | `null` |
| OpenAI o4-mini | `openai` | `o4-mini` |
| DeepSeek Reasoner | `deepseek` | `deepseek-reasoner` |

Defaults actuales:

- Blancas: OpenAI `o4-mini`.
- Negras: DeepSeek `deepseek-reasoner`.

## Tests

```powershell
npm run test -- --run
```

Estado actual:

- 2 archivos de test.
- 6 tests pasando.

## Build

```powershell
npm run build
```

El output queda en `frontend/dist/`, que esta ignorado por Git.
