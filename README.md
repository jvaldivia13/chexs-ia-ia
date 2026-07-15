# Chexs IA vs IA

Aplicacion web de ajedrez con modos **Humano vs IA** e **IA vs IA**. El tablero se renderiza en React y el backend valida todas las jugadas con `python-chess`. Los agentes pueden jugar con motor local o con LLMs externos, siempre limitados a jugadas legales.

## Caracteristicas

- Tablero interactivo 8x8 con validacion legal de movimientos.
- Modos de juego:
  - **Humano vs IA**: el jugador usa blancas y la IA responde con negras.
  - **IA vs IA**: dos agentes juegan automaticamente.
- Configuracion por agente:
  - Nombre.
  - Perfil: `balanced`, `aggressive`, `defensive`, `tactical`.
  - Expertise: `easy`, `normal`, `difficult`.
  - Motor: `local`, `openai`, `deepseek`.
- Integracion A2A local para turnos de agentes.
- Visualizacion de cada jugada en el tablero con pausa de al menos 2 segundos entre movimientos automaticos.
- Historial de jugadas.
- Soporte de reglas completas de ajedrez: castling, en passant, promocion, jaque mate, ahogado y tablas.

## IAs Disponibles

| Motor | Modelo | Uso |
| --- | --- | --- |
| `local` | Motor interno | No consume tokens. Usa aleatorio, evaluacion o minimax segun expertise. |
| `openai` | `o4-mini` | Razona sobre FEN, historial, perfil y lista de jugadas legales. |
| `deepseek` | `deepseek-reasoner` | Razona sobre la posicion usando la API de DeepSeek. |

Configuracion por defecto del frontend:

- Blancas: `Atlas` con `openai/o4-mini`.
- Negras: `Nyx` con `deepseek/deepseek-reasoner`.

Si un LLM no tiene API key configurada, falla la llamada o devuelve una jugada invalida, el backend usa fallback local para mantener la partida funcionando.

## Arquitectura

```text
appAjedrez/
+-- backend/
|   +-- main.py           # API FastAPI
|   +-- chess_engine.py   # Wrapper de python-chess
|   +-- ai.py             # Motor local: easy, normal, difficult
|   +-- a2a_agents.py     # Mensajes A2A locales y turnos de agentes
|   +-- llm_chess.py      # Clientes OpenAI y DeepSeek
|   +-- game_state.py     # Estado de partidas y perfiles default
|   +-- models.py         # Modelos Pydantic
|   +-- tests/            # Tests backend
+-- frontend/
|   +-- src/
|   |   +-- components/   # Board, PieceSquare, controles, historial
|   |   +-- hooks/        # useGameState
|   |   +-- pages/        # GamePage
|   |   +-- services/     # Cliente API
|   |   +-- styles/       # CSS modules y estilos globales
|   +-- TESTING.md
+-- docs/
|   +-- superpowers/      # Planes y especificaciones de desarrollo
+-- README.md
+-- SETUP.md
```

## Requisitos

- Python 3.9+
- Node.js 18+
- npm

## Variables de Entorno

Crea un archivo `.env` en la raiz del proyecto si vas a usar LLMs:

```env
OPENAI_API_KEY=tu_api_key_openai
DEEPSEEK_API_KEY=tu_api_key_deepseek
```

El archivo `.env` esta incluido en `.gitignore` y no debe subirse al repositorio.

Tambien puedes usar variables de entorno del sistema:

```powershell
setx OPENAI_API_KEY "tu_api_key_openai"
setx DEEPSEEK_API_KEY "tu_api_key_deepseek"
```

Despues de usar `setx`, cierra y vuelve a abrir la terminal o VS Code.

Variables opcionales del backend:

```env
ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
LOG_LEVEL=INFO
```

`ALLOWED_ORIGINS` controla los origenes permitidos por CORS (por defecto, solo el frontend local). `LOG_LEVEL` controla el nivel de logging del backend (por ejemplo `DEBUG` para ver mas detalle de los fallos de LLM).

## Inicio Rapido

### Backend

```powershell
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn main:app --reload
```

Backend: <http://127.0.0.1:8000>

Docs API: <http://127.0.0.1:8000/docs>

### Frontend

```powershell
cd frontend
npm install
npm run dev
```

Frontend: <http://localhost:5173>

## Como Jugar

1. Abre <http://localhost:5173>.
2. Elige `Humano vs IA` o `IA vs IA`.
3. Configura nombre, perfil, expertise y motor de cada agente.
4. Inicia la partida.
5. En `IA vs IA`, los agentes se alternan automaticamente y cada jugada se muestra en el tablero con una pausa.
6. En `Humano vs IA`, juega con blancas; la IA responde con negras.

## API Principal

| Metodo | Ruta | Descripcion |
| --- | --- | --- |
| `GET` | `/health` | Estado del backend. |
| `POST` | `/api/game/new` | Crea una partida con modo y agentes. |
| `POST` | `/api/game/move` | Aplica una jugada humana. |
| `POST` | `/api/game/agent-turn` | Ejecuta un turno de agente IA. |
| `GET` | `/api/game/state` | Devuelve el estado actual de la partida. |

Las rutas tambien existen sin prefijo `/api` para compatibilidad: `/game/new`, `/game/move`, `/game/agent-turn`, `/game/state`.

## Testing

Backend:

```powershell
cd backend
venv\Scripts\activate
python -m pytest tests -q
```

Frontend:

```powershell
cd frontend
npm run test -- --run
```

Build frontend:

```powershell
cd frontend
npm run build
```

Estado actual verificado:

- Backend: 35 tests pasando.
- Frontend: 6 tests pasando.
- Build frontend: correcto.

## Seguridad

- No pegues API keys en commits, issues, pull requests ni chats.
- Si una key se expone, revocala y genera una nueva.
- El backend valida que toda jugada de LLM este dentro de la lista de jugadas legales antes de aplicarla.

## Licencia

Proyecto educativo para explorar ajedrez, React, FastAPI, agentes A2A y LLMs aplicados a decisiones de juego.
