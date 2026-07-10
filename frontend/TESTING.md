# Testing Report

Reporte de pruebas automatizadas y checks manuales para **Chexs IA vs IA**.

## Backend

Comando:

```powershell
cd backend
venv\Scripts\activate
python -m pytest tests -q
```

Resultado actual:

```text
35 passed, 1 warning
```

### Cobertura Backend

| Area | Tests | Estado |
| --- | ---: | --- |
| Motor de ajedrez | 9 | Passing |
| IA local | 8 | Passing |
| API endpoints | 18 | Passing |
| **Total** | **35** | **Passing** |

Incluye validacion de:

- Posicion inicial.
- Jugadas validas e invalidas.
- Castling.
- En passant.
- Promocion.
- Jaque mate.
- Ahogado.
- IAs `easy`, `normal`, `difficult`.
- Creacion de partidas.
- Jugadas con `game_id`.
- Estado de partida.
- Endpoint `health`.

## Frontend

Comando:

```powershell
cd frontend
npm run test -- --run
```

Resultado actual:

```text
Test Files  2 passed (2)
Tests       6 passed (6)
```

### Cobertura Frontend

| Area | Tests | Estado |
| --- | ---: | --- |
| Board | 3 | Passing |
| MoveHistory | 3 | Passing |
| **Total** | **6** | **Passing** |

Incluye validacion de:

- Render de 64 casillas.
- Render del tablero.
- Captura legal con caballo.
- Historial de jugadas por pares.
- Numeracion de movimientos.
- Estado vacio del historial.

## Build

Comando:

```powershell
cd frontend
npm run build
```

Resultado actual:

```text
vite build: success
```

## Checks Manuales

Checklist recomendado antes de publicar:

- [ ] Backend responde en <http://127.0.0.1:8000/health>.
- [ ] Frontend responde en <http://localhost:5173>.
- [ ] Se puede iniciar `Humano vs IA`.
- [ ] Se puede iniciar `IA vs IA`.
- [ ] Blancas muestran `openai/o4-mini` por defecto.
- [ ] Negras muestran `deepseek/deepseek-reasoner` por defecto.
- [ ] El tablero se actualiza despues de cada jugada.
- [ ] Las jugadas automaticas esperan al menos 2 segundos.
- [ ] Si falta una API key, el juego continua con fallback local.
- [ ] El historial de movimientos se actualiza.
- [ ] La UI no muestra API keys.

## Nota Sobre LLMs

Las pruebas automatizadas no llaman a OpenAI ni a DeepSeek. Esto evita consumo de tokens y hace que la suite sea deterministica. La integracion LLM se valida manualmente con API keys locales en `.env` o variables de entorno.
