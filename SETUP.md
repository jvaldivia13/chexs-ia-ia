# Guia de Setup

Esta guia explica como instalar, ejecutar, probar y depurar el proyecto en desarrollo.

## 1. Requisitos

Instala:

- Python 3.9 o superior.
- Node.js 18 o superior.
- npm.
- Git, opcional pero recomendado.

Verifica versiones:

```powershell
python --version
node --version
npm --version
```

## 2. Backend

Desde la raiz del proyecto:

```powershell
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Verifica dependencias:

```powershell
python -c "import fastapi, chess, httpx; print('Backend dependencies OK')"
```

Ejecuta el backend:

```powershell
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

URLs:

- API: <http://127.0.0.1:8000>
- Docs Swagger: <http://127.0.0.1:8000/docs>
- Health check: <http://127.0.0.1:8000/health>

## 3. Frontend

En otra terminal:

```powershell
cd frontend
npm install
npm run dev
```

URL:

- App: <http://localhost:5173>

El frontend usa Vite y proxya `/api/*` hacia el backend en el puerto `8000`.

## 4. Configuracion LLM

El juego puede funcionar sin claves usando el motor `local`. Para usar OpenAI y DeepSeek, crea un archivo `.env` en la raiz:

```env
OPENAI_API_KEY=tu_api_key_openai
DEEPSEEK_API_KEY=tu_api_key_deepseek
```

Tambien puedes usar variables del sistema:

```powershell
setx OPENAI_API_KEY "tu_api_key_openai"
setx DEEPSEEK_API_KEY "tu_api_key_deepseek"
```

Notas:

- Despues de `setx`, reinicia terminal o VS Code.
- No subas `.env`; ya esta en `.gitignore`.
- Si una API key se expone, revocala y genera una nueva.

## 5. Modos de Juego

### Humano vs IA

- El humano juega con blancas.
- La IA juega con negras.
- La respuesta IA se ejecuta como turno separado para que pueda visualizarse.

### IA vs IA

- Ambos agentes juegan automaticamente.
- Hay una pausa minima de 2 segundos entre jugadas automaticas.
- Cada agente puede usar motor local, OpenAI o DeepSeek.

## 6. Motores de IA

| Motor | Requiere key | Modelo default | Descripcion |
| --- | --- | --- | --- |
| `local` | No | N/A | Algoritmos internos: random, evaluacion, minimax. |
| `openai` | Si | `o4-mini` | Razonamiento sobre posicion y jugadas legales. |
| `deepseek` | Si | `deepseek-reasoner` | Razonamiento via DeepSeek Chat API. |

El backend siempre valida que la jugada elegida por un LLM este en la lista legal antes de aplicarla.

## 7. Tests

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

Build:

```powershell
cd frontend
npm run build
```

Resultados actuales esperados:

- Backend: 35 tests pasando.
- Frontend: 6 tests pasando.
- Build frontend: exitoso.

## 8. API

### Crear Partida

```http
POST /api/game/new
```

Ejemplo:

```json
{
  "difficulty": "normal",
  "mode": "ai_vs_ai",
  "white_agent": {
    "name": "Atlas",
    "persona": "balanced",
    "expertise": "normal",
    "provider": "openai",
    "model": "o4-mini"
  },
  "black_agent": {
    "name": "Nyx",
    "persona": "tactical",
    "expertise": "normal",
    "provider": "deepseek",
    "model": "deepseek-reasoner"
  }
}
```

### Jugada Humana

```http
POST /api/game/move
```

```json
{
  "game_id": "uuid",
  "from_square": "e2",
  "to_square": "e4",
  "promotion": null,
  "auto_reply": false
}
```

### Turno de Agente

```http
POST /api/game/agent-turn
```

```json
{
  "game_id": "uuid"
}
```

### Estado

```http
GET /api/game/state?game_id=uuid
```

## 9. Troubleshooting

### `npm` no se reconoce

Instala Node.js LTS desde <https://nodejs.org/>. En Windows, reinicia la terminal despues de instalar.

### PowerShell bloquea `npm.ps1`

Usa `npm.cmd`:

```powershell
& "C:\Program Files\nodejs\npm.cmd" run dev
```

### Puerto ocupado

```powershell
netstat -ano | findstr ":5173 :8000"
taskkill /PID <PID> /F
```

### El LLM no juega

Revisa:

- `.env` existe en la raiz.
- `OPENAI_API_KEY` o `DEEPSEEK_API_KEY` estan configuradas.
- Reiniciaste terminal/VS Code si usaste `setx`.
- El backend fue reiniciado despues de cambiar `.env`.

Si la llamada LLM falla, el juego usara fallback local.

## 10. Comandos Utiles

Detener servidores en Windows:

```powershell
netstat -ano | findstr ":5173 :8000"
taskkill /PID <PID> /F
```

Ver estado de Git:

```powershell
git status --short
```

Limpiar caches de tests:

```powershell
Remove-Item -Recurse -Force backend\.pytest_cache, frontend\dist
```
