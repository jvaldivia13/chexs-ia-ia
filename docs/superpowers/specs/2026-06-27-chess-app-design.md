# Chess Application - Design Specification

## Overview

A web-based chess application where users can play against an AI opponent at three difficulty levels (Easy, Normal, Difficult). The game features an interactive 8x8 board, move validation, and a complete move history in algebraic notation.

## Architecture

The application uses a **frontend/backend separation** approach:

- **Frontend:** React + TypeScript + Vite (runs in browser)
- **Backend:** FastAPI + Python (REST API)
- **Chess Engine:** python-chess library

The frontend handles UI rendering and user interaction. The backend manages game state, validates moves, and calculates AI decisions. This separation ensures a responsive UI and enables future multiplayer features.

## Tech Stack

- **Frontend:** React 18, TypeScript, Vite, axios
- **Backend:** FastAPI, python-chess, Uvicorn
- **AI:** Custom minimax implementation (difficulty levels) using python-chess
- **Development:** Node.js 18+, Python 3.9+

## Global Constraints

- No database or persistence (each game is independent)
- AI response time target: <500ms for all difficulty levels
- Supports standard chess rules including castling, en passant, pawn promotion
- Browser: Modern browsers (Chrome 90+, Firefox 88+, Safari 14+)

---

# Design Details

## 1. Frontend Architecture (React)

### Component Structure

```
src/
├── components/
│   ├── Board.tsx               # 8x8 chessboard with drag/click interaction
│   ├── PieceSquare.tsx         # Individual square with piece rendering
│   ├── MoveHistory.tsx         # Move list in algebraic notation
│   ├── GameControls.tsx        # New Game, Undo, Reset buttons
│   └── DifficultySelect.tsx    # Level selection (Easy/Normal/Difficult)
├── pages/
│   └── GamePage.tsx            # Main page container
├── hooks/
│   └── useGameState.ts         # Centralized game state management
├── services/
│   └── api.ts                  # Backend API client
├── types/
│   └── chess.ts                # TypeScript interfaces
├── styles/
│   └── Board.module.css        # Styling
└── App.tsx
```

### Key Components

**Board.tsx:**
- Renders 64 squares in alternating colors
- Detects user clicks to select pieces and destination squares
- Highlights legal moves when piece is selected
- Displays pieces as Unicode symbols or images
- Sends selected move to backend via API
- Displays current turn and game status

**MoveHistory.tsx:**
- Lists all moves in standard algebraic notation (e.g., "e4", "Nf3", "Bxc6")
- Scrollable list updated after each move
- Supports optional click-to-review (optional feature for later)

**DifficultySelect.tsx:**
- Radio or dropdown to select difficulty before game starts
- Options: Easy, Normal, Difficult
- Sends selection to backend when game initializes

**GameControls.tsx:**
- "New Game" button: resets everything, returns to difficulty selection
- "Undo" button: goes back one full turn (player + AI move)
- "Reset" button: starts fresh game at current difficulty

**useGameState Hook:**
- Manages: current board position, whose turn, move history, game status
- Syncs with backend state
- Provides functions: `makeMove()`, `initGame()`, `undoMove()`

### Game Flow

1. User selects difficulty → `POST /game/new` with difficulty
2. Backend initializes game, returns FEN position
3. Frontend renders board with pieces
4. User clicks piece → highlights legal moves
5. User clicks destination → Frontend validates with python-chess library
6. `POST /game/move` sent to backend
7. Backend validates, applies move, calculates AI response
8. Response includes board state, AI move, game status
9. Frontend updates board, adds moves to history
10. Loop continues until game ends (checkmate, stalemate, draw)

## 2. Backend Architecture (FastAPI)

### Directory Structure

```
backend/
├── main.py                 # FastAPI app initialization, routes
├── models.py               # Pydantic models for request/response validation
├── chess_engine.py         # Wraps python-chess, game logic
├── ai.py                   # AI decision logic for 3 difficulty levels
├── game_state.py           # In-memory game state management
├── requirements.txt        # Dependencies
└── tests/
    ├── test_ai.py          # AI algorithm tests
    ├── test_chess_logic.py # Move validation, edge cases
    └── test_endpoints.py   # API endpoint tests
```

### API Endpoints

**POST /game/new**
- Request: `{ "difficulty": "normal" }`
- Response: `{ "game_id": "uuid", "board_fen": "...", "player_color": "white", "message": "Game started" }`
- Creates new game instance, player is always white

**POST /game/move**
- Request: `{ "from_square": "e2", "to_square": "e4" }`
- Response:
  ```json
  {
    "player_move": "e2e4",
    "ai_move": "e7e5",
    "board_fen": "rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq e6 0 2",
    "game_status": "ongoing",
    "legal_moves": ["e5", "f3", ...],
    "player_in_check": false
  }
  ```
- Validates player move, applies it, calculates AI response, returns new state

**GET /game/state**
- Returns current board state (useful for sync/debugging)
- Response: `{ "board_fen": "...", "game_status": "...", "turn": "white"|"black" }`

### Game State Management

- Each game instance stored in memory (dict keyed by game_id)
- Contains: board position (python-chess Board object), move history, difficulty level, game status
- No persistence between server restarts

### Chess Logic (chess_engine.py)

- Wraps `python-chess` library to:
  - Validate moves (legal according to FIDE rules)
  - Detect check, checkmate, stalemate
  - Handle special moves: castling, en passant, pawn promotion
  - Generate all legal moves for a position

### AI Implementation (ai.py)

**Easy Level:**
- Generate all legal moves
- Pick one at random
- Near-instant response

**Normal Level:**
- Evaluates board position based on:
  - Material count (Pawn=1, Knight=3, Bishop=3, Rook=5, Queen=9)
  - Piece positioning (control of center, safety)
  - Simple heuristics (avoid hanging pieces, capture if possible)
- Searches 2 moves ahead (1 full turn)
- Returns move with highest evaluation

**Difficult Level:**
- Minimax algorithm with alpha-beta pruning
- Search depth: 3-4 moves ahead (1.5-2 full turns)
- Evaluation function combines:
  - Material advantage
  - King safety
  - Piece activity
  - Tactical patterns (forks, pins, skewers)
- Response time: <500ms for typical positions

### Error Handling

| Scenario | Response | Status |
|----------|----------|--------|
| Invalid move (illegal) | `{ "error": "Illegal move: e1 to e5" }` | 400 |
| Move in wrong format | `{ "error": "Invalid format" }` | 422 |
| Game already ended | `{ "error": "Game is over" }` | 400 |
| Promotion requires choice | `{ "promotion": "required", "legal_promotions": ["Q", "R", "B", "N"] }` | 400 |

## 3. Data Flow and Integration

### Complete Move Cycle

1. **User Action:**
   - Clicks piece on Board
   - Selects destination square
   - Frontend calculates `from_square` and `to_square` in algebraic notation

2. **Validation (Frontend):**
   - Checks move is in list of legal moves from backend
   - Provides visual feedback (highlights legal moves)

3. **Submission:**
   - `POST /game/move` with `{ "from_square": "e2", "to_square": "e4" }`

4. **Backend Processing:**
   - `chess_engine.validate_move(from, to)` → True/False
   - If valid: Apply move to position
   - Check game status: ongoing/checkmate/stalemate/draw
   - If ongoing: `ai.get_move(board, difficulty)` → calculate next move
   - Return new board state + AI move

5. **Frontend Update:**
   - Receives response
   - Updates board position from FEN
   - Adds both moves to history
   - Re-renders with new position

### State Consistency

- Backend is source of truth for position validity
- Frontend mirrors backend state for display
- After each move, frontend receives authoritative board state from backend
- No optimistic updates (frontend always waits for backend confirmation)

## 4. Edge Cases and Special Moves

**Castling:**
- Valid if: King in starting position, Rook in corner, no pieces between, King not in check, path not under attack
- Rendered as King moving 2 squares, Rook moves automatically

**En Passant:**
- Valid if: Enemy pawn just moved 2 squares forward on adjacent file
- Backend tracks this automatically via `python-chess`

**Pawn Promotion:**
- When pawn reaches 8th rank, backend returns `promotion_required: true`
- Frontend prompts user to choose: Queen, Rook, Bishop, Knight
- User sends `POST /game/move` with `promotion: "Q"` (or other piece)

**Checkmate:**
- Detected automatically after AI move
- Backend returns `game_status: "checkmate"`, `winner: "ai"` or `"player"`

**Stalemate / Draws:**
- Stalemate: player to move has no legal moves and is not in check
- Insufficient material: King vs King, King+Knight vs King, etc.
- 50-move rule: 50 moves without capture or pawn move
- Backend detects all, returns `game_status: "draw"`, `reason: "stalemate|material|50move"`

## 5. Testing Strategy

### Backend Tests (pytest)

**test_chess_logic.py:**
- Validate legal move detection
- Test castling: valid castling, blocked, after king/rook moved
- Test en passant: capture, invalid en passant
- Test pawn promotion: all 4 promotion choices
- Test checkmate: fool's mate, various checkmate patterns
- Test stalemate and draw conditions

**test_ai.py:**
- Easy: random moves are legal
- Normal: moves avoid hanging pieces, capture if advantageous
- Difficult: avoids blunders, plays reasonable positions

**test_endpoints.py:**
- POST /game/new: returns valid FEN
- POST /game/move: invalid moves rejected, valid moves accepted
- Move sequence: full game to checkmate
- Error cases: malformed requests, impossible positions

### Frontend Tests (Vitest + React Testing Library)

**Board.tsx:**
- Renders 64 squares
- Clicking piece highlights legal moves
- Clicking destination sends move to backend

**MoveHistory.tsx:**
- Displays moves in correct algebraic notation
- Updates after each move

**Integration:**
- Full game cycle: select difficulty → make moves → checkmate → new game

## 6. Future Extensions (Not in MVP)

- Save/load games (database required)
- Online multiplayer (WebSocket + session management)
- Move analysis and suggestions
- Opening book database
- Endgame tablebases for perfect play
- Game replay with navigation
- Multiple AI strategies (e.g., trap-oriented, defensive)

---

## Summary

This is a clean, modular chess application with clear separation of concerns:

- **Frontend** handles rendering and user interaction
- **Backend** enforces correctness and calculates AI moves
- **python-chess** provides bulletproof chess logic
- **No database** keeps initial scope tight
- **Testable design** with clear component boundaries

Each piece can be tested independently, and the API contract is simple and well-defined.
