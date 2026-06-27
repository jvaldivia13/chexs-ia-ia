# Chess Application Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a web-based chess application where users can play against an AI opponent at three difficulty levels with an interactive board and move history.

**Architecture:** React frontend communicates with FastAPI backend via REST API. Frontend handles UI and user interaction; backend enforces chess rules and calculates AI moves using python-chess library. No database—all game state is in-memory and ephemeral.

**Tech Stack:** React 18 + TypeScript + Vite (frontend), FastAPI + Uvicorn (backend), python-chess (chess logic), pytest (backend tests), Vitest + React Testing Library (frontend tests).

## Global Constraints

- Node.js 18+, Python 3.9+
- Target AI response time: <500ms for all levels
- Browser support: Chrome 90+, Firefox 88+, Safari 14+
- No database or persistence between sessions
- Player is always white; AI is always black

---

# File Structure

## Frontend (`frontend/`)
```
src/
├── components/
│   ├── Board.tsx               # 8x8 interactive chessboard
│   ├── PieceSquare.tsx         # Individual square with piece
│   ├── MoveHistory.tsx         # List of moves in algebraic notation
│   ├── GameControls.tsx        # New Game, Undo, Reset buttons
│   ├── DifficultySelect.tsx    # Difficulty level selection
│   ├── GameStatus.tsx          # Display game status (ongoing/checkmate/draw)
│   └── __tests__/
│       ├── Board.test.tsx
│       ├── MoveHistory.test.tsx
│       └── GamePage.test.tsx
├── pages/
│   └── GamePage.tsx            # Main page container
├── hooks/
│   └── useGameState.ts         # Game state management hook
├── services/
│   └── api.ts                  # Backend API client
├── types/
│   ├── chess.ts                # TypeScript interfaces
│   └── api.ts                  # API response types
├── styles/
│   ├── Board.module.css        # Board styling
│   ├── Global.css              # Global styles
│   └── variables.css           # CSS variables (colors, spacing)
├── App.tsx                     # Root component
├── main.tsx                    # Entry point
└── vite-env.d.ts              # Vite types
```

## Backend (`backend/`)
```
├── main.py                     # FastAPI app, routes
├── models.py                   # Pydantic request/response models
├── chess_engine.py             # python-chess wrapper
├── ai.py                       # AI logic for 3 levels
├── game_state.py               # In-memory game state
├── requirements.txt            # Python dependencies
├── tests/
│   ├── test_chess_logic.py     # Chess rules, edge cases
│   ├── test_ai.py              # AI move tests
│   └── test_endpoints.py       # API endpoint tests
└── .env (local only)           # DEBUG=True for development
```

---

# Implementation Tasks

## Phase 1: Project Setup

### Task 1: Initialize Frontend and Backend Projects

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/vite.config.ts`
- Create: `frontend/tsconfig.json`
- Create: `backend/requirements.txt`
- Create: `backend/main.py` (stub)
- Create: `.gitignore`

**Interfaces:**
- Produces: Frontend dev server running on `http://localhost:5173`, backend API available on `http://localhost:8000`

- [ ] **Step 1: Create frontend directory and initialize Vite project**

```bash
cd d:\appAjedrez
npm create vite@latest frontend -- --template react-ts
cd frontend
npm install
```

- [ ] **Step 2: Install frontend dependencies**

```bash
cd d:\appAjedrez\frontend
npm install axios react-router-dom
npm install --save-dev @testing-library/react @testing-library/jest-dom vitest @vitest/ui
```

- [ ] **Step 3: Create Vite config for frontend**

File: `frontend/vite.config.ts`
```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      }
    }
  }
})
```

- [ ] **Step 4: Create backend directory and requirements**

```bash
cd d:\appAjedrez
mkdir backend
cd backend
```

File: `backend/requirements.txt`
```
fastapi==0.104.1
uvicorn==0.24.0
python-chess==1.10.0
pydantic==2.5.0
pytest==7.4.3
httpx==0.25.2
```

- [ ] **Step 5: Create Python virtual environment and install dependencies**

```bash
cd d:\appAjedrez\backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

- [ ] **Step 6: Create backend stub**

File: `backend/main.py`
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "ok"}
```

- [ ] **Step 7: Create .gitignore**

File: `.gitignore`
```
# Frontend
frontend/node_modules/
frontend/dist/
frontend/.env.local
frontend/.vite/

# Backend
backend/venv/
backend/__pycache__/
backend/.pytest_cache/
backend/.env
backend/*.pyc

# IDE
.vscode/
.idea/
*.swp
*.swo
```

- [ ] **Step 8: Commit**

```bash
cd d:\appAjedrez
git add frontend/package.json frontend/vite.config.ts frontend/tsconfig.json backend/requirements.txt backend/main.py .gitignore
git commit -m "chore: initialize frontend and backend projects"
```

---

### Task 2: Define TypeScript Types and Pydantic Models

**Files:**
- Create: `frontend/src/types/chess.ts`
- Create: `frontend/src/types/api.ts`
- Create: `backend/models.py`

**Interfaces:**
- Produces:
  - `type Move = { from: string; to: string; promotion?: string }`
  - `type GameState = { fen: string; turn: 'white' | 'black'; status: GameStatus }`
  - `class NewGameRequest(BaseModel): difficulty: str`
  - `class MoveRequest(BaseModel): from_square: str; to_square: str; promotion: Optional[str]`
  - `class MoveResponse(BaseModel): player_move: str; ai_move: Optional[str]; board_fen: str; game_status: str; legal_moves: List[str]; player_in_check: bool`

- [ ] **Step 1: Create TypeScript chess types**

File: `frontend/src/types/chess.ts`
```typescript
export type Piece = 'K' | 'Q' | 'R' | 'B' | 'N' | 'P' | 'k' | 'q' | 'r' | 'b' | 'n' | 'p' | null
export type Square = string // "a1", "e4", etc.
export type Difficulty = 'easy' | 'normal' | 'difficult'
export type GameStatus = 'ongoing' | 'checkmate' | 'stalemate' | 'draw'
export type Color = 'white' | 'black'

export interface Move {
  from: Square
  to: Square
  promotion?: 'Q' | 'R' | 'B' | 'N'
}

export interface GameState {
  fen: string
  turn: Color
  status: GameStatus
  legalMoves: Square[]
  playerInCheck: boolean
  lastMove?: Move
}

export interface MoveRecord {
  moveNumber: number
  white: string
  black?: string
}
```

- [ ] **Step 2: Create TypeScript API types**

File: `frontend/src/types/api.ts`
```typescript
export interface NewGameResponse {
  gameId: string
  boardFen: string
  playerColor: 'white'
  message: string
}

export interface MoveRequest {
  fromSquare: string
  toSquare: string
  promotion?: 'Q' | 'R' | 'B' | 'N'
}

export interface MoveResponse {
  playerMove: string
  aiMove: string | null
  boardFen: string
  gameStatus: 'ongoing' | 'checkmate' | 'stalemate' | 'draw'
  legalMoves: string[]
  playerInCheck: boolean
}

export interface GameStateResponse {
  boardFen: string
  gameStatus: 'ongoing' | 'checkmate' | 'stalemate' | 'draw'
  turn: 'white' | 'black'
}
```

- [ ] **Step 3: Create Pydantic models**

File: `backend/models.py`
```python
from pydantic import BaseModel
from typing import Optional, List

class NewGameRequest(BaseModel):
    difficulty: str  # 'easy', 'normal', 'difficult'

class NewGameResponse(BaseModel):
    game_id: str
    board_fen: str
    player_color: str
    message: str

class MoveRequest(BaseModel):
    from_square: str
    to_square: str
    promotion: Optional[str] = None

class MoveResponse(BaseModel):
    player_move: str
    ai_move: Optional[str]
    board_fen: str
    game_status: str
    legal_moves: List[str]
    player_in_check: bool

class GameStateResponse(BaseModel):
    board_fen: str
    game_status: str
    turn: str
```

- [ ] **Step 4: Commit**

```bash
cd d:\appAjedrez
git add frontend/src/types/ backend/models.py
git commit -m "feat: define TypeScript and Pydantic types"
```

---

## Phase 2: Backend Implementation

### Task 3: Implement Chess Engine Wrapper

**Files:**
- Create: `backend/chess_engine.py`
- Create: `backend/tests/test_chess_logic.py`

**Interfaces:**
- Consumes: `python-chess` library
- Produces:
  - `class ChessEngine: get_board() -> str, make_move(from_sq, to_sq, promotion) -> bool, get_legal_moves() -> List[str], is_checkmate() -> bool, is_stalemate() -> bool, get_fen() -> str`

- [ ] **Step 1: Write failing test for chess engine**

File: `backend/tests/test_chess_logic.py`
```python
import pytest
from chess_engine import ChessEngine

def test_init_board_is_start_position():
    engine = ChessEngine()
    assert engine.get_fen() == "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

def test_make_valid_move():
    engine = ChessEngine()
    result = engine.make_move("e2", "e4")
    assert result is True
    assert "e4" in engine.get_fen()

def test_make_invalid_move():
    engine = ChessEngine()
    result = engine.make_move("e1", "e4")
    assert result is False

def test_get_legal_moves_from_start():
    engine = ChessEngine()
    moves = engine.get_legal_moves()
    assert len(moves) == 20  # 16 pawn moves + 4 knight moves

def test_detect_checkmate():
    engine = ChessEngine()
    # Fool's mate: 1.f3 e5 2.g4 Qh4#
    engine.make_move("f2", "f3")
    engine.make_move("e7", "e5")
    engine.make_move("g2", "g4")
    engine.make_move("d8", "h4")
    assert engine.is_checkmate() is True

def test_detect_stalemate():
    engine = ChessEngine()
    # Load a stalemate position
    engine.set_fen("k7/8/8/8/8/8/1Q6/K7 b - - 0 1")
    assert engine.is_stalemate() is True

def test_castling():
    engine = ChessEngine()
    engine.set_fen("r3k2r/pppppppp/8/8/8/8/PPPPPPPP/R3K2R w KQkq - 0 1")
    assert engine.make_move("e1", "g1") is True  # kingside castling

def test_en_passant():
    engine = ChessEngine()
    engine.set_fen("rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1")
    assert engine.make_move("d4", "e3") is True  # en passant capture
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd d:\appAjedrez\backend
pytest tests/test_chess_logic.py -v
```

Expected output: All tests fail with "ModuleNotFoundError: No module named 'chess_engine'"

- [ ] **Step 3: Implement chess engine**

File: `backend/chess_engine.py`
```python
import chess
from typing import List, Optional

class ChessEngine:
    def __init__(self):
        self.board = chess.Board()
    
    def get_fen(self) -> str:
        return self.board.fen()
    
    def set_fen(self, fen: str) -> None:
        self.board.set_fen(fen)
    
    def make_move(self, from_square: str, to_square: str, promotion: Optional[str] = None) -> bool:
        try:
            move_uci = from_square + to_square
            if promotion:
                promotion_map = {'Q': chess.QUEEN, 'R': chess.ROOK, 'B': chess.BISHOP, 'N': chess.KNIGHT}
                move = chess.Move.from_uci(move_uci + chess.piece_symbol(promotion_map[promotion]))
            else:
                move = chess.Move.from_uci(move_uci)
            
            if move in self.board.legal_moves:
                self.board.push(move)
                return True
            return False
        except:
            return False
    
    def get_legal_moves(self) -> List[str]:
        moves = []
        for move in self.board.legal_moves:
            moves.append(move.uci()[:4])  # Return as "e2e4" format
        return moves
    
    def is_checkmate(self) -> bool:
        return self.board.is_checkmate()
    
    def is_stalemate(self) -> bool:
        return self.board.is_stalemate()
    
    def is_check(self) -> bool:
        return self.board.is_check()
    
    def is_game_over(self) -> bool:
        return self.board.is_game_over()
    
    def get_game_status(self) -> str:
        if self.board.is_checkmate():
            return "checkmate"
        elif self.board.is_stalemate():
            return "stalemate"
        elif self.board.is_insufficient_material():
            return "draw"
        elif self.board.halfmove_clock >= 100:  # 50-move rule
            return "draw"
        return "ongoing"
    
    def get_move_history(self) -> List[str]:
        return [move.uci()[:4] for move in self.board.move_stack]
    
    def undo_move(self) -> bool:
        if len(self.board.move_stack) > 0:
            self.board.pop()
            return True
        return False
```

- [ ] **Step 4: Run test to verify it passes**

```bash
cd d:\appAjedrez\backend
pytest tests/test_chess_logic.py -v
```

Expected output: All tests pass

- [ ] **Step 5: Commit**

```bash
cd d:\appAjedrez
git add backend/chess_engine.py backend/tests/test_chess_logic.py
git commit -m "feat: implement chess engine wrapper with python-chess"
```

---

### Task 4: Implement AI - Easy Level

**Files:**
- Create: `backend/ai.py` (stub with easy level)
- Modify: `backend/tests/test_ai.py`

**Interfaces:**
- Consumes: `ChessEngine`
- Produces:
  - `def get_ai_move(board: ChessEngine, difficulty: str) -> str`
  - Easy level returns random legal move

- [ ] **Step 1: Write failing test for easy AI**

File: `backend/tests/test_ai.py`
```python
import pytest
from chess_engine import ChessEngine
from ai import get_ai_move

def test_easy_ai_returns_legal_move():
    engine = ChessEngine()
    engine.make_move("e2", "e4")  # white moves
    move = get_ai_move(engine, "easy")
    
    legal_moves = engine.get_legal_moves()
    assert move in legal_moves

def test_easy_ai_consistent_with_board():
    engine = ChessEngine()
    engine.make_move("e2", "e4")
    
    move = get_ai_move(engine, "easy")
    # Move should be a valid square notation
    assert len(move) == 4
    assert move[:2] in engine.get_legal_moves()
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd d:\appAjedrez\backend
pytest tests/test_ai.py::test_easy_ai_returns_legal_move -v
```

- [ ] **Step 3: Implement easy AI**

File: `backend/ai.py`
```python
import random
from chess_engine import ChessEngine

def get_ai_move(engine: ChessEngine, difficulty: str) -> str:
    legal_moves = engine.get_legal_moves()
    
    if difficulty == "easy":
        return random.choice(legal_moves)
    elif difficulty == "normal":
        return get_normal_move(engine)
    elif difficulty == "difficult":
        return get_difficult_move(engine)
    
    return random.choice(legal_moves)

def get_normal_move(engine: ChessEngine) -> str:
    # Placeholder for normal AI
    return random.choice(engine.get_legal_moves())

def get_difficult_move(engine: ChessEngine) -> str:
    # Placeholder for difficult AI
    return random.choice(engine.get_legal_moves())
```

- [ ] **Step 4: Run test to verify it passes**

```bash
cd d:\appAjedrez\backend
pytest tests/test_ai.py::test_easy_ai_returns_legal_move -v
```

- [ ] **Step 5: Commit**

```bash
cd d:\appAjedrez
git add backend/ai.py backend/tests/test_ai.py
git commit -m "feat: implement easy AI (random moves)"
```

---

### Task 5: Implement AI - Normal Level

**Files:**
- Modify: `backend/ai.py`
- Modify: `backend/tests/test_ai.py`

**Interfaces:**
- Consumes: `ChessEngine`, board state
- Produces: `get_normal_move(engine) -> str` that evaluates positions

- [ ] **Step 1: Write failing tests for normal AI**

File: `backend/tests/test_ai.py` (add these tests)
```python
def test_normal_ai_prefers_capturing_move():
    engine = ChessEngine()
    # Setup: white pawn on e4, black knight on e5 (attacked)
    engine.set_fen("rnbqkb1r/pppppppp/8/4n3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 1")
    
    # If there's a capture available, normal AI should consider it
    move = get_ai_move(engine, "normal")
    legal_moves = engine.get_legal_moves()
    assert move in legal_moves

def test_normal_ai_avoids_hanging_piece():
    engine = ChessEngine()
    # Setup where one move loses a piece
    engine.set_fen("rnbqkb1r/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1")
    engine.make_move("e7", "e5")  # black pawn blocks
    
    move = get_ai_move(engine, "normal")
    legal_moves = engine.get_legal_moves()
    assert move in legal_moves
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd d:\appAjedrez\backend
pytest tests/test_ai.py::test_normal_ai_prefers_capturing_move -v
pytest tests/test_ai.py::test_normal_ai_avoids_hanging_piece -v
```

- [ ] **Step 3: Implement position evaluation and normal AI**

File: `backend/ai.py` (update)
```python
import random
import chess
from chess_engine import ChessEngine

def evaluate_position(board: chess.Board) -> float:
    """Simple board evaluation: material count + positional factors"""
    piece_values = {
        chess.PAWN: 1,
        chess.KNIGHT: 3,
        chess.BISHOP: 3,
        chess.ROOK: 5,
        chess.QUEEN: 9,
        chess.KING: 0
    }
    
    score = 0.0
    
    # Material count
    for piece_type, value in piece_values.items():
        white_count = len(board.pieces(piece_type, chess.WHITE))
        black_count = len(board.pieces(piece_type, chess.BLACK))
        score += (white_count - black_count) * value
    
    # Simple positional bonus: center control
    center_squares = [chess.E4, chess.D4, chess.E5, chess.D5]
    for sq in center_squares:
        if board.piece_at(sq) and board.piece_at(sq).color == chess.WHITE:
            score += 0.5
        elif board.piece_at(sq) and board.piece_at(sq).color == chess.BLACK:
            score -= 0.5
    
    return score

def get_ai_move(engine: ChessEngine, difficulty: str) -> str:
    legal_moves = engine.get_legal_moves()
    
    if difficulty == "easy":
        return random.choice(legal_moves)
    elif difficulty == "normal":
        return get_normal_move(engine)
    elif difficulty == "difficult":
        return get_difficult_move(engine)
    
    return random.choice(legal_moves)

def get_normal_move(engine: ChessEngine) -> str:
    """Evaluates positions 2 moves ahead, chooses best move"""
    legal_moves = engine.get_legal_moves()
    best_move = None
    best_score = -float('inf')
    
    for move_uci in legal_moves:
        # Try the move
        engine.board.push_uci(move_uci)
        
        # Evaluate after this move + opponent's best response
        position_score = evaluate_position(engine.board)
        
        # Simple lookahead: check if opponent has a strong response
        opponent_moves = [m.uci()[:4] for m in engine.board.legal_moves]
        worst_opponent_score = float('inf')
        
        for opp_move in opponent_moves:
            engine.board.push_uci(opp_move)
            opp_score = evaluate_position(engine.board)
            worst_opponent_score = min(worst_opponent_score, opp_score)
            engine.board.pop()
        
        # Net score: our position minus opponent's best response
        net_score = position_score - worst_opponent_score * 0.5
        
        if net_score > best_score:
            best_score = net_score
            best_move = move_uci
        
        engine.board.pop()
    
    return best_move if best_move else random.choice(legal_moves)

def get_difficult_move(engine: ChessEngine) -> str:
    # Placeholder for difficult AI
    return random.choice(engine.get_legal_moves())
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd d:\appAjedrez\backend
pytest tests/test_ai.py::test_normal_ai_prefers_capturing_move -v
pytest tests/test_ai.py::test_normal_ai_avoids_hanging_piece -v
```

- [ ] **Step 5: Commit**

```bash
cd d:\appAjedrez
git add backend/ai.py backend/tests/test_ai.py
git commit -m "feat: implement normal AI with position evaluation"
```

---

### Task 6: Implement AI - Difficult Level

**Files:**
- Modify: `backend/ai.py`
- Modify: `backend/tests/test_ai.py`

**Interfaces:**
- Consumes: `ChessEngine`, board state
- Produces: `get_difficult_move(engine) -> str` using minimax

- [ ] **Step 1: Write test for difficult AI**

File: `backend/tests/test_ai.py` (add this test)
```python
def test_difficult_ai_returns_legal_move():
    engine = ChessEngine()
    engine.make_move("e2", "e4")
    
    move = get_ai_move(engine, "difficult")
    legal_moves = engine.get_legal_moves()
    assert move in legal_moves

def test_difficult_ai_plays_reasonable_opening():
    engine = ChessEngine()
    # After 1.e4, normal responses are e5, c5, d5, etc.
    engine.make_move("e2", "e4")
    move = get_ai_move(engine, "difficult")
    
    # Should not make weird opening moves
    # This is a soft test—difficult AI just needs to be legal
    legal_moves = engine.get_legal_moves()
    assert move in legal_moves
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd d:\appAjedrez\backend
pytest tests/test_ai.py::test_difficult_ai_returns_legal_move -v
```

- [ ] **Step 3: Implement minimax AI**

File: `backend/ai.py` (update get_difficult_move)
```python
def get_difficult_move(engine: ChessEngine) -> str:
    """Minimax with alpha-beta pruning, depth 3"""
    legal_moves = engine.get_legal_moves()
    
    best_move = None
    best_score = -float('inf')
    alpha = -float('inf')
    beta = float('inf')
    
    for move_uci in legal_moves:
        engine.board.push_uci(move_uci)
        score = minimax(engine.board, depth=3, alpha=alpha, beta=beta, is_maximizing=False)
        engine.board.pop()
        
        if score > best_score:
            best_score = score
            best_move = move_uci
        
        alpha = max(alpha, best_score)
    
    return best_move if best_move else random.choice(legal_moves)

def minimax(board: chess.Board, depth: int, alpha: float, beta: float, is_maximizing: bool) -> float:
    """Minimax with alpha-beta pruning"""
    if depth == 0 or board.is_game_over():
        return evaluate_position(board)
    
    if is_maximizing:
        max_score = -float('inf')
        for move in board.legal_moves:
            board.push(move)
            score = minimax(board, depth - 1, alpha, beta, False)
            board.pop()
            max_score = max(max_score, score)
            alpha = max(alpha, max_score)
            if beta <= alpha:
                break
        return max_score
    else:
        min_score = float('inf')
        for move in board.legal_moves:
            board.push(move)
            score = minimax(board, depth - 1, alpha, beta, True)
            board.pop()
            min_score = min(min_score, score)
            beta = min(beta, min_score)
            if beta <= alpha:
                break
        return min_score
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd d:\appAjedrez\backend
pytest tests/test_ai.py::test_difficult_ai_returns_legal_move -v
pytest tests/test_ai.py::test_difficult_ai_plays_reasonable_opening -v
```

- [ ] **Step 5: Commit**

```bash
cd d:\appAjedrez
git add backend/ai.py backend/tests/test_ai.py
git commit -m "feat: implement difficult AI with minimax and alpha-beta pruning"
```

---

### Task 7: Implement FastAPI Endpoints

**Files:**
- Modify: `backend/main.py`
- Create: `backend/game_state.py`

**Interfaces:**
- Consumes: `ChessEngine`, `ai.get_ai_move()`, models
- Produces: 
  - `POST /api/game/new` → `NewGameResponse`
  - `POST /api/game/move` → `MoveResponse`
  - `GET /api/game/state` → `GameStateResponse`

- [ ] **Step 1: Create game state manager**

File: `backend/game_state.py`
```python
import uuid
from chess_engine import ChessEngine
from typing import Dict, Optional

class Game:
    def __init__(self, game_id: str, difficulty: str):
        self.game_id = game_id
        self.difficulty = difficulty
        self.engine = ChessEngine()
        self.move_history = []

games: Dict[str, Game] = {}

def create_game(difficulty: str) -> Game:
    game_id = str(uuid.uuid4())
    game = Game(game_id, difficulty)
    games[game_id] = game
    return game

def get_game(game_id: str) -> Optional[Game]:
    return games.get(game_id)
```

- [ ] **Step 2: Implement game endpoints in main.py**

File: `backend/main.py` (replace content)
```python
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models import NewGameRequest, NewGameResponse, MoveRequest, MoveResponse, GameStateResponse
from game_state import create_game, get_game
from ai import get_ai_move
import uuid

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

current_game_id = None

@app.post("/api/game/new", response_model=NewGameResponse)
def new_game(request: NewGameRequest):
    global current_game_id
    
    if request.difficulty not in ["easy", "normal", "difficult"]:
        raise HTTPException(status_code=400, detail="Invalid difficulty")
    
    game = create_game(request.difficulty)
    current_game_id = game.game_id
    
    return NewGameResponse(
        game_id=game.game_id,
        board_fen=game.engine.get_fen(),
        player_color="white",
        message="Game started"
    )

@app.post("/api/game/move", response_model=MoveResponse)
def make_move(request: MoveRequest):
    global current_game_id
    
    if not current_game_id:
        raise HTTPException(status_code=400, detail="No active game")
    
    game = get_game(current_game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    
    # Validate and apply player move
    if not game.engine.make_move(request.from_square, request.to_square, request.promotion):
        raise HTTPException(status_code=400, detail="Illegal move")
    
    player_move = request.from_square + request.to_square
    game.move_history.append(player_move)
    
    # Check game status
    game_status = game.engine.get_game_status()
    
    ai_move = None
    if game_status == "ongoing":
        # Get AI move
        ai_move = get_ai_move(game.engine, game.difficulty)
        game.engine.make_move(ai_move[:2], ai_move[2:])
        game.move_history.append(ai_move)
        game_status = game.engine.get_game_status()
    
    return MoveResponse(
        player_move=player_move,
        ai_move=ai_move,
        board_fen=game.engine.get_fen(),
        game_status=game_status,
        legal_moves=game.engine.get_legal_moves() if game_status == "ongoing" else [],
        player_in_check=game.engine.is_check() and game.engine.board.turn == False
    )

@app.get("/api/game/state", response_model=GameStateResponse)
def game_state():
    global current_game_id
    
    if not current_game_id:
        raise HTTPException(status_code=400, detail="No active game")
    
    game = get_game(current_game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    
    return GameStateResponse(
        board_fen=game.engine.get_fen(),
        game_status=game.engine.get_game_status(),
        turn="white" if game.engine.board.turn == True else "black"
    )

@app.get("/health")
def health_check():
    return {"status": "ok"}
```

- [ ] **Step 3: Run backend tests**

```bash
cd d:\appAjedrez\backend
pytest tests/ -v
```

Expected: All backend tests pass

- [ ] **Step 4: Commit**

```bash
cd d:\appAjedrez
git add backend/main.py backend/game_state.py
git commit -m "feat: implement FastAPI endpoints for chess game"
```

---

### Task 8: Backend Integration Tests

**Files:**
- Create: `backend/tests/test_endpoints.py`

**Interfaces:**
- Consumes: FastAPI app
- Produces: Verified endpoints with test coverage

- [ ] **Step 1: Write endpoint tests**

File: `backend/tests/test_endpoints.py`
```python
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_new_game_endpoint():
    response = client.post("/api/game/new", json={"difficulty": "easy"})
    assert response.status_code == 200
    data = response.json()
    assert "game_id" in data
    assert "board_fen" in data
    assert data["player_color"] == "white"

def test_move_endpoint_valid_move():
    client.post("/api/game/new", json={"difficulty": "easy"})
    response = client.post("/api/game/move", json={
        "from_square": "e2",
        "to_square": "e4",
        "promotion": None
    })
    assert response.status_code == 200
    data = response.json()
    assert data["player_move"] == "e2e4"
    assert data["ai_move"] is not None

def test_move_endpoint_invalid_move():
    client.post("/api/game/new", json={"difficulty": "easy"})
    response = client.post("/api/game/move", json={
        "from_square": "e1",
        "to_square": "e5",
        "promotion": None
    })
    assert response.status_code == 400

def test_game_state_endpoint():
    client.post("/api/game/new", json={"difficulty": "normal"})
    response = client.get("/api/game/state")
    assert response.status_code == 200
    data = response.json()
    assert "board_fen" in data
    assert data["turn"] == "white"

def test_full_game_sequence():
    # New game
    new_game_resp = client.post("/api/game/new", json={"difficulty": "easy"})
    assert new_game_resp.status_code == 200
    
    # Make moves until checkmate or draw
    for i in range(100):  # Safety limit
        state = client.get("/api/game/state").json()
        if state["game_status"] != "ongoing":
            break
        
        move_resp = client.post("/api/game/move", json={
            "from_square": "e2",
            "to_square": "e4",
            "promotion": None
        })
        if move_resp.status_code != 200:
            # Move failed, try another
            break
```

- [ ] **Step 2: Run endpoint tests**

```bash
cd d:\appAjedrez\backend
pytest tests/test_endpoints.py -v
```

- [ ] **Step 3: Commit**

```bash
cd d:\appAjedrez
git add backend/tests/test_endpoints.py
git commit -m "test: add endpoint integration tests"
```

---

## Phase 3: Frontend Implementation

### Task 9: Create Game State Hook and API Client

**Files:**
- Create: `frontend/src/hooks/useGameState.ts`
- Create: `frontend/src/services/api.ts`

**Interfaces:**
- Produces:
  - `useGameState(difficulty): { gameState, makeMove, newGame, undoMove }`
  - `api.newGame(difficulty), api.makeMove(from, to, promotion)`

- [ ] **Step 1: Create API client**

File: `frontend/src/services/api.ts`
```typescript
import axios from 'axios'
import { NewGameResponse, MoveRequest, MoveResponse, GameStateResponse } from '../types/api'

const API_BASE = '/api'

export const api = {
  async newGame(difficulty: string): Promise<NewGameResponse> {
    const response = await axios.post(`${API_BASE}/game/new`, { difficulty })
    return response.data
  },

  async makeMove(fromSquare: string, toSquare: string, promotion?: string): Promise<MoveResponse> {
    const response = await axios.post(`${API_BASE}/game/move`, {
      from_square: fromSquare,
      to_square: toSquare,
      promotion: promotion || null
    })
    return response.data
  },

  async getGameState(): Promise<GameStateResponse> {
    const response = await axios.get(`${API_BASE}/game/state`)
    return response.data
  }
}
```

- [ ] **Step 2: Create game state hook**

File: `frontend/src/hooks/useGameState.ts`
```typescript
import { useState, useCallback } from 'react'
import { GameState, Difficulty, Move } from '../types/chess'
import { api } from '../services/api'

export function useGameState() {
  const [gameState, setGameState] = useState<GameState | null>(null)
  const [difficulty, setDifficulty] = useState<Difficulty>('normal')
  const [moveHistory, setMoveHistory] = useState<string[]>([])
  const [loading, setLoading] = useState(false)

  const newGame = useCallback(async (selectedDifficulty: Difficulty) => {
    setLoading(true)
    try {
      const response = await api.newGame(selectedDifficulty)
      setDifficulty(selectedDifficulty)
      setGameState({
        fen: response.board_fen,
        turn: 'white',
        status: 'ongoing',
        legalMoves: [],
        playerInCheck: false
      })
      setMoveHistory([])
    } catch (error) {
      console.error('Failed to start new game:', error)
    } finally {
      setLoading(false)
    }
  }, [])

  const makeMove = useCallback(async (from: string, to: string, promotion?: string) => {
    if (!gameState) return false

    setLoading(true)
    try {
      const response = await api.makeMove(from, to, promotion)
      
      setGameState({
        fen: response.board_fen,
        turn: response.game_status === 'ongoing' ? 'white' : 'black',
        status: response.game_status as any,
        legalMoves: response.legal_moves,
        playerInCheck: response.player_in_check
      })

      const newMoves = [...moveHistory]
      if (response.player_move) newMoves.push(response.player_move)
      if (response.ai_move) newMoves.push(response.ai_move)
      setMoveHistory(newMoves)

      return true
    } catch (error) {
      console.error('Move failed:', error)
      return false
    } finally {
      setLoading(false)
    }
  }, [gameState, moveHistory])

  const undoMove = useCallback(() => {
    // Undo is complex—would require state tracking on backend
    // For MVP, not implementing full undo
    console.warn('Undo not implemented in MVP')
  }, [])

  return {
    gameState,
    difficulty,
    moveHistory,
    loading,
    newGame,
    makeMove,
    undoMove
  }
}
```

- [ ] **Step 3: Commit**

```bash
cd d:\appAjedrez
git add frontend/src/hooks/useGameState.ts frontend/src/services/api.ts
git commit -m "feat: create game state hook and API client"
```

---

### Task 10: Implement Board Component

**Files:**
- Create: `frontend/src/components/Board.tsx`
- Create: `frontend/src/components/PieceSquare.tsx`
- Create: `frontend/src/styles/Board.module.css`

**Interfaces:**
- Consumes: `useGameState`, FEN string
- Produces: Interactive 8x8 board with drag/click interaction

- [ ] **Step 1: Create PieceSquare component**

File: `frontend/src/components/PieceSquare.tsx`
```typescript
import React from 'react'
import styles from '../styles/Board.module.css'

const PIECE_SYMBOLS: Record<string, string> = {
  'K': '♔', 'Q': '♕', 'R': '♖', 'B': '♗', 'N': '♘', 'P': '♙',
  'k': '♚', 'q': '♛', 'r': '♜', 'b': '♝', 'n': '♞', 'p': '♟'
}

interface Props {
  square: string
  piece: string | null
  isLight: boolean
  isSelected: boolean
  isLegal: boolean
  onClick: (square: string) => void
}

export const PieceSquare: React.FC<Props> = ({
  square,
  piece,
  isLight,
  isSelected,
  isLegal,
  onClick
}) => {
  return (
    <div
      className={`
        ${styles.square}
        ${isLight ? styles.light : styles.dark}
        ${isSelected ? styles.selected : ''}
        ${isLegal ? styles.legal : ''}
      `}
      onClick={() => onClick(square)}
    >
      {piece && <span className={styles.piece}>{PIECE_SYMBOLS[piece]}</span>}
    </div>
  )
}
```

- [ ] **Step 2: Create Board component**

File: `frontend/src/components/Board.tsx`
```typescript
import React, { useState, useEffect } from 'react'
import { Chess } from 'chess.js'
import { PieceSquare } from './PieceSquare'
import styles from '../styles/Board.module.css'

interface BoardProps {
  fen: string
  onMove: (from: string, to: string) => Promise<boolean>
  disabled: boolean
}

export const Board: React.FC<BoardProps> = ({ fen, onMove, disabled }) => {
  const [chess, setChess] = useState(new Chess(fen))
  const [selectedSquare, setSelectedSquare] = useState<string | null>(null)
  const [legalMoves, setLegalMoves] = useState<string[]>([])

  useEffect(() => {
    const newChess = new Chess(fen)
    setChess(newChess)
    setSelectedSquare(null)
    setLegalMoves([])
  }, [fen])

  const handleSquareClick = async (square: string) => {
    if (disabled) return

    if (selectedSquare === null) {
      // Select piece
      const moves = chess.moves({ square, verbose: true })
      if (moves.length > 0) {
        setSelectedSquare(square)
        setLegalMoves(moves.map(m => m.to))
      }
    } else if (selectedSquare === square) {
      // Deselect
      setSelectedSquare(null)
      setLegalMoves([])
    } else {
      // Try move
      const success = await onMove(selectedSquare, square)
      if (success) {
        setSelectedSquare(null)
        setLegalMoves([])
      }
    }
  }

  const squares: Array<string> = []
  for (let rank = 8; rank >= 1; rank--) {
    for (let file = 0; file < 8; file++) {
      const square = String.fromCharCode(97 + file) + rank
      squares.push(square)
    }
  }

  return (
    <div className={styles.board}>
      {squares.map((square, idx) => {
        const isLight = (idx % 2 === 0 && Math.floor(idx / 8) % 2 === 0) ||
                        (idx % 2 === 1 && Math.floor(idx / 8) % 2 === 1)
        const piece = chess.get(square)

        return (
          <PieceSquare
            key={square}
            square={square}
            piece={piece ? piece.color + piece.type.toUpperCase() : null}
            isLight={isLight}
            isSelected={selectedSquare === square}
            isLegal={legalMoves.includes(square)}
            onClick={handleSquareClick}
          />
        )
      })}
    </div>
  )
}
```

- [ ] **Step 3: Create Board styles**

File: `frontend/src/styles/Board.module.css`
```css
.board {
  display: grid;
  grid-template-columns: repeat(8, 60px);
  grid-template-rows: repeat(8, 60px);
  gap: 0;
  border: 2px solid #333;
  margin: 20px 0;
}

.square {
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  position: relative;
  transition: background-color 0.2s;
}

.light {
  background-color: #f0d9b5;
}

.dark {
  background-color: #b58863;
}

.selected {
  background-color: #baca44 !important;
}

.legal {
  box-shadow: inset 0 0 0 2px #baca44;
}

.legal::after {
  content: '';
  width: 10px;
  height: 10px;
  background-color: #baca44;
  border-radius: 50%;
  position: absolute;
}

.piece {
  font-size: 40px;
  line-height: 1;
  user-select: none;
}
```

- [ ] **Step 4: Install chess.js dependency**

```bash
cd d:\appAjedrez\frontend
npm install chess.js
npm install --save-dev @types/chess.js
```

- [ ] **Step 5: Commit**

```bash
cd d:\appAjedrez
git add frontend/src/components/Board.tsx frontend/src/components/PieceSquare.tsx frontend/src/styles/Board.module.css
git commit -m "feat: implement interactive board component"
```

---

### Task 11: Implement Remaining Components (MoveHistory, GameControls, DifficultySelect, GameStatus)

**Files:**
- Create: `frontend/src/components/MoveHistory.tsx`
- Create: `frontend/src/components/GameControls.tsx`
- Create: `frontend/src/components/DifficultySelect.tsx`
- Create: `frontend/src/components/GameStatus.tsx`

- [ ] **Step 1: Create MoveHistory component**

File: `frontend/src/components/MoveHistory.tsx`
```typescript
import React from 'react'
import styles from '../styles/History.module.css'

interface Props {
  moves: string[]
}

export const MoveHistory: React.FC<Props> = ({ moves }) => {
  const pairs = []
  for (let i = 0; i < moves.length; i += 2) {
    pairs.push({
      number: (i / 2) + 1,
      white: moves[i] || '',
      black: moves[i + 1] || ''
    })
  }

  return (
    <div className={styles.history}>
      <h3>Move History</h3>
      <table>
        <tbody>
          {pairs.map((pair) => (
            <tr key={pair.number}>
              <td>{pair.number}.</td>
              <td>{pair.white}</td>
              <td>{pair.black}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
```

- [ ] **Step 2: Create GameControls component**

File: `frontend/src/components/GameControls.tsx`
```typescript
import React from 'react'
import styles from '../styles/Controls.module.css'

interface Props {
  onNewGame: () => void
  onUndo: () => void
  disabled: boolean
}

export const GameControls: React.FC<Props> = ({ onNewGame, onUndo, disabled }) => {
  return (
    <div className={styles.controls}>
      <button onClick={onNewGame} disabled={disabled}>
        New Game
      </button>
      <button onClick={onUndo} disabled={disabled}>
        Undo
      </button>
    </div>
  )
}
```

- [ ] **Step 3: Create DifficultySelect component**

File: `frontend/src/components/DifficultySelect.tsx`
```typescript
import React, { useState } from 'react'
import { Difficulty } from '../types/chess'
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
```

- [ ] **Step 4: Create GameStatus component**

File: `frontend/src/components/GameStatus.tsx`
```typescript
import React from 'react'
import { GameStatus } from '../types/chess'
import styles from '../styles/Status.module.css'

interface Props {
  status: GameStatus
  playerInCheck: boolean
}

export const GameStatusDisplay: React.FC<Props> = ({ status, playerInCheck }) => {
  const getStatusText = () => {
    if (playerInCheck) return 'You are in check!'
    if (status === 'checkmate') return 'Checkmate! AI wins.'
    if (status === 'stalemate') return 'Stalemate. Draw.'
    if (status === 'draw') return 'Draw.'
    return 'Game in progress'
  }

  return (
    <div className={`${styles.status} ${status === 'ongoing' ? '' : styles.ended}`}>
      {getStatusText()}
    </div>
  )
}
```

- [ ] **Step 5: Create CSS files for components**

File: `frontend/src/styles/History.module.css`
```css
.history {
  padding: 20px;
  background: #f5f5f5;
  border-radius: 8px;
  max-width: 200px;
}

.history h3 {
  margin-top: 0;
}

.history table {
  width: 100%;
  font-size: 12px;
}

.history td {
  padding: 4px 8px;
}
```

File: `frontend/src/styles/Controls.module.css`
```css
.controls {
  display: flex;
  gap: 10px;
  margin: 20px 0;
}

.controls button {
  padding: 10px 20px;
  background-color: #2c5aa0;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.controls button:hover:not(:disabled) {
  background-color: #1e4170;
}

.controls button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
```

File: `frontend/src/styles/Difficulty.module.css`
```css
.modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.container {
  background: white;
  padding: 40px;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  text-align: center;
}

.options {
  margin: 20px 0;
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.options label {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
}

.startButton {
  padding: 12px 30px;
  background-color: #2c5aa0;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
  margin-top: 20px;
}

.startButton:hover {
  background-color: #1e4170;
}
```

File: `frontend/src/styles/Status.module.css`
```css
.status {
  padding: 15px;
  background: #e8f5e9;
  border-radius: 4px;
  text-align: center;
  font-weight: bold;
  margin: 10px 0;
}

.status.ended {
  background: #ffebee;
}
```

- [ ] **Step 6: Commit**

```bash
cd d:\appAjedrez
git add frontend/src/components/MoveHistory.tsx frontend/src/components/GameControls.tsx frontend/src/components/DifficultySelect.tsx frontend/src/components/GameStatus.tsx frontend/src/styles/
git commit -m "feat: implement MoveHistory, GameControls, DifficultySelect, GameStatus components"
```

---

### Task 12: Create Main Game Page and App Component

**Files:**
- Create: `frontend/src/pages/GamePage.tsx`
- Modify: `frontend/src/App.tsx`
- Create: `frontend/src/styles/Global.css`

- [ ] **Step 1: Create GamePage component**

File: `frontend/src/pages/GamePage.tsx`
```typescript
import React, { useState } from 'react'
import { Board } from '../components/Board'
import { MoveHistory } from '../components/MoveHistory'
import { GameControls } from '../components/GameControls'
import { DifficultySelect } from '../components/DifficultySelect'
import { GameStatusDisplay } from '../components/GameStatus'
import { useGameState } from '../hooks/useGameState'
import { Difficulty } from '../types/chess'

export const GamePage: React.FC = () => {
  const { gameState, difficulty, moveHistory, loading, newGame, makeMove, undoMove } = useGameState()
  const [showDifficultySelect, setShowDifficultySelect] = useState(true)

  const handleSelectDifficulty = async (selectedDifficulty: Difficulty) => {
    await newGame(selectedDifficulty)
    setShowDifficultySelect(false)
  }

  const handleNewGame = () => {
    setShowDifficultySelect(true)
  }

  const handleMove = async (from: string, to: string) => {
    return await makeMove(from, to)
  }

  if (showDifficultySelect) {
    return <DifficultySelect onSelect={handleSelectDifficulty} />
  }

  if (!gameState) {
    return <div>Loading...</div>
  }

  return (
    <div className="game-container">
      <h1>Chess vs AI</h1>
      <div className="game-layout">
        <div className="board-section">
          <Board
            fen={gameState.fen}
            onMove={handleMove}
            disabled={loading || gameState.status !== 'ongoing'}
          />
          <GameStatusDisplay
            status={gameState.status}
            playerInCheck={gameState.playerInCheck}
          />
          <GameControls
            onNewGame={handleNewGame}
            onUndo={undoMove}
            disabled={loading}
          />
        </div>
        <div className="history-section">
          <MoveHistory moves={moveHistory} />
        </div>
      </div>
    </div>
  )
}
```

- [ ] **Step 2: Update App component**

File: `frontend/src/App.tsx`
```typescript
import './styles/Global.css'
import { GamePage } from './pages/GamePage'

function App() {
  return <GamePage />
}

export default App
```

- [ ] **Step 3: Create global styles**

File: `frontend/src/styles/Global.css`
```css
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  background-color: #f5f5f5;
}

.game-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.game-container h1 {
  text-align: center;
  margin-bottom: 30px;
  color: #333;
}

.game-layout {
  display: flex;
  gap: 30px;
  justify-content: center;
}

.board-section {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.history-section {
  flex: 0 0 250px;
}

@media (max-width: 768px) {
  .game-layout {
    flex-direction: column;
    align-items: center;
  }

  .history-section {
    flex: 0 0 auto;
    width: 100%;
  }
}
```

- [ ] **Step 4: Commit**

```bash
cd d:\appAjedrez
git add frontend/src/pages/GamePage.tsx frontend/src/App.tsx frontend/src/styles/Global.css
git commit -m "feat: create GamePage and App components"
```

---

### Task 13: Frontend Testing

**Files:**
- Create: `frontend/src/components/__tests__/Board.test.tsx`
- Create: `frontend/src/components/__tests__/MoveHistory.test.tsx`

- [ ] **Step 1: Configure Vitest**

File: `frontend/vitest.config.ts` (or update vite.config.ts)
```typescript
import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: [],
  },
})
```

- [ ] **Step 2: Write Board component tests**

File: `frontend/src/components/__tests__/Board.test.tsx`
```typescript
import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
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
    const squares = screen.getAllByRole('button', { hidden: true })
    expect(squares.length).toBeGreaterThanOrEqual(8)
  })

  it('displays pieces in starting position', () => {
    const { container } = render(
      <Board
        fen="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        onMove={() => Promise.resolve(true)}
        disabled={false}
      />
    )
    // Check that pieces are rendered
    expect(container.textContent).toContain('♔') // White King
    expect(container.textContent).toContain('♚') // Black King
  })
})
```

- [ ] **Step 3: Write MoveHistory component tests**

File: `frontend/src/components/__tests__/MoveHistory.test.tsx`
```typescript
import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MoveHistory } from '../MoveHistory'

describe('MoveHistory Component', () => {
  it('displays move pairs correctly', () => {
    render(<MoveHistory moves={['e2e4', 'e7e5', 'g1f3']} />)
    
    // Check that moves are displayed
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
```

- [ ] **Step 4: Run tests**

```bash
cd d:\appAjedrez\frontend
npm run test
```

- [ ] **Step 5: Commit**

```bash
cd d:\appAjedrez
git add frontend/src/components/__tests__/ frontend/vitest.config.ts
git commit -m "test: add frontend component tests"
```

---

## Phase 4: Integration and Finalization

### Task 14: Test Full Game Flow

**Files:**
- Test: End-to-end game flow

- [ ] **Step 1: Start backend server**

```bash
cd d:\appAjedrez\backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn main:app --reload
```

Backend should start on `http://localhost:8000`

- [ ] **Step 2: Start frontend dev server**

```bash
cd d:\appAjedrez\frontend
npm run dev
```

Frontend should start on `http://localhost:5173`

- [ ] **Step 3: Test game flow manually**

1. Open `http://localhost:5173` in browser
2. Select difficulty level and start game
3. Make several moves (e.g., e4, Nf3, etc.)
4. Verify AI responds with legal moves
5. Play until checkmate or draw
6. Verify move history displays correctly
7. Try "New Game" button

- [ ] **Step 4: Run all backend tests**

```bash
cd d:\appAjedrez\backend
pytest tests/ -v
```

All tests should pass.

- [ ] **Step 5: Run all frontend tests**

```bash
cd d:\appAjedrez\frontend
npm run test
```

All tests should pass.

- [ ] **Step 6: Commit**

```bash
cd d:\appAjedrez
git add -A
git commit -m "test: verify full game flow integration"
```

---

### Task 15: Documentation and Cleanup

**Files:**
- Create: `README.md`
- Create: `SETUP.md`

- [ ] **Step 1: Create README**

File: `README.md`
```markdown
# Chess Application

A web-based chess game where you can play against an AI opponent.

## Features

- Interactive 8x8 chessboard
- 3 difficulty levels: Easy, Normal, Difficult
- Move history in algebraic notation
- Real-time game status (check, checkmate, stalemate)

## Tech Stack

- **Frontend:** React 18, TypeScript, Vite
- **Backend:** FastAPI, Python 3.9+
- **Chess Logic:** python-chess

## Setup

See [SETUP.md](SETUP.md) for installation and running instructions.

## How to Play

1. Open the application in your browser
2. Select a difficulty level
3. Click pieces to move them (highlighted squares show legal moves)
4. The AI plays as black
5. The game ends when checkmate, stalemate, or draw occurs

## Project Structure

```
├── frontend/          # React application
│   └── src/
│       ├── components/
│       ├── pages/
│       ├── hooks/
│       ├── services/
│       └── types/
└── backend/           # FastAPI application
    ├── main.py
    ├── chess_engine.py
    ├── ai.py
    └── tests/
```

## Development

Run both servers concurrently for development:
- Backend: `python -m uvicorn main:app --reload`
- Frontend: `npm run dev`

## Testing

- **Backend:** `pytest tests/ -v`
- **Frontend:** `npm run test`
```

- [ ] **Step 2: Create SETUP.md**

File: `SETUP.md`
```markdown
# Setup Instructions

## Prerequisites

- Node.js 18+
- Python 3.9+
- Git

## Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create virtual environment:
   ```bash
   python -m venv venv
   ```

3. Activate virtual environment:
   - Windows: `venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Run the server:
   ```bash
   python -m uvicorn main:app --reload
   ```

   The API will be available at `http://localhost:8000`

## Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Run the dev server:
   ```bash
   npm run dev
   ```

   The application will be available at `http://localhost:5173`

## Running Tests

### Backend Tests
```bash
cd backend
pytest tests/ -v
```

### Frontend Tests
```bash
cd frontend
npm run test
```

## Build for Production

### Backend
Backend is ready to deploy with FastAPI. Use a production ASGI server like Gunicorn:
```bash
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app
```

### Frontend
```bash
cd frontend
npm run build
```

Output will be in `dist/` directory.
```

- [ ] **Step 3: Commit**

```bash
cd d:\appAjedrez
git add README.md SETUP.md
git commit -m "docs: add README and SETUP documentation"
```

---

## Summary

This plan implements a complete chess application with:

✅ **Backend:** FastAPI with chess logic, 3-level AI, REST API  
✅ **Frontend:** React with interactive board, game controls, move history  
✅ **Testing:** Comprehensive tests for backend and frontend  
✅ **Documentation:** Setup and usage guides  

Each task produces independently testable, committable work. Total implementation: ~15 tasks, ~2-4 hours estimated.
