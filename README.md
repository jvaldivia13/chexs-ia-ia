# Chess Application

A web-based chess game where you can play against an AI opponent at three difficulty levels.

## Features

- Interactive 8x8 chessboard with drag-and-click interface
- AI opponent with three difficulty levels:
  - **Easy**: Random legal moves
  - **Normal**: Piece value evaluation with basic tactics
  - **Difficult**: Minimax algorithm with alpha-beta pruning (4-ply depth)
- Move history displayed in algebraic notation
- Real-time game status (current player, game outcome)
- Responsive design with CSS Grid
- Full chess rules support:
  - Castling (kingside and queenside)
  - En passant
  - Pawn promotion
  - Checkmate/Stalemate detection
  - Move validation

## Tech Stack

- **Frontend**: React 18, TypeScript, Vite, Testing Library, Vitest
- **Backend**: FastAPI (Python), python-chess, Uvicorn
- **AI**: Minimax algorithm with alpha-beta pruning for difficulty levels

## Quick Start

### Prerequisites

- Node.js 18+
- Python 3.9+
- Git (optional)

### Installation

1. Clone or download the project:
```bash
cd d:\appAjedrez
```

2. Set up the backend:
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

3. Set up the frontend:
```bash
cd ../frontend
npm install
```

### Running the Application

**Terminal 1 - Backend:**
```bash
cd backend
venv\Scripts\activate
python -m uvicorn main:app --reload
```
Server runs on `http://localhost:8000`

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```
Application opens at `http://localhost:5173`

## How to Play

1. **Start Game**: Open the application and select your desired difficulty level
2. **Make Moves**: 
   - Click on a piece to select it (highlights legal moves in green)
   - Click on a highlighted square to move there
   - Click the same square again to deselect
3. **AI Response**: The AI automatically plays after your move
4. **Game End**: Game ends at checkmate, stalemate, or draw (50-move rule)
5. **New Game**: Click "New Game" button to start over with difficulty selection

## Development

### Running Tests

**Backend Tests:**
```bash
cd backend
pytest tests/ -v
```
Runs 31 tests covering chess logic, AI, and API endpoints.

**Frontend Tests:**
```bash
cd frontend
npm run test
```
Runs 5 unit tests for React components.

### Building for Production

**Frontend Build:**
```bash
cd frontend
npm run build
```
Creates optimized build in `frontend/dist/`

**Backend Production:**
```bash
cd backend
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app
```

## API Endpoints

- `POST /new_game/{difficulty}` - Start new game (difficulty: easy, normal, difficult)
- `POST /move/{from_square}/{to_square}` - Make a move
- `GET /game_state` - Get current game state and AI move
- `GET /health` - Health check endpoint

## Project Structure

```
appAjedrez/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── chess_engine.py      # Chess logic wrapper
│   ├── game_state.py        # Game state management
│   ├── ai.py                # AI implementation
│   ├── models.py            # Pydantic models
│   ├── requirements.txt      # Python dependencies
│   └── tests/               # Backend tests
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── styles/          # CSS modules
│   │   └── App.tsx          # Main app component
│   ├── package.json         # Node dependencies
│   ├── vite.config.ts       # Vite configuration
│   ├── vitest.config.ts     # Vitest configuration
│   └── TESTING.md           # Test report
├── README.md                # This file
└── SETUP.md                 # Development setup guide
```

## Testing Results

- Backend: 31/31 tests passing
- Frontend: 5/5 tests passing
- Total: 36/36 tests passing

See `frontend/TESTING.md` for detailed test results.

## License

This is an educational project for learning chess, web development, and AI algorithms.
