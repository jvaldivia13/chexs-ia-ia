# Development Setup Guide

This guide provides step-by-step instructions for setting up and running the Chess Application in development mode.

## Prerequisites

Before you begin, ensure you have installed:
- **Node.js 18+** with npm (download from https://nodejs.org/)
- **Python 3.9+** (download from https://www.python.org/)
- **Git** (optional, for version control)

Verify installations:
```bash
node --version
npm --version
python --version
```

## Project Location

```bash
cd d:\appAjedrez
```

## Backend Setup

### 1. Navigate to Backend Directory
```bash
cd d:\appAjedrez\backend
```

### 2. Create Virtual Environment
```bash
python -m venv venv
```

### 3. Activate Virtual Environment

**Windows Command Prompt:**
```bash
venv\Scripts\activate
```

**Windows PowerShell:**
```bash
venv\Scripts\Activate.ps1
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Verify Installation
```bash
python -c "import fastapi; import chess; print('✓ Dependencies installed')"
```

## Frontend Setup

### 1. Navigate to Frontend Directory
```bash
cd d:\appAjedrez\frontend
```

### 2. Install Dependencies
```bash
npm install
```

### 3. Verify Installation
```bash
npm list react vite vitest
```

## Running Development Servers

### Start Backend (Port 8000)

**Terminal/Command Prompt 1:**
```bash
cd d:\appAjedrez\backend
venv\Scripts\activate
python -m uvicorn main:app --reload
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### Start Frontend (Port 5173)

**Terminal/Command Prompt 2:**
```bash
cd d:\appAjedrez\frontend
npm run dev
```

You should see:
```
VITE v8.x.x  ready in xxx ms
➜  Local:   http://localhost:5173/
```

### Access the Application

Open your browser and navigate to:
```
http://localhost:5173
```

## Testing

### Backend Tests

From the `backend` directory with venv activated:

```bash
pytest tests/ -v
```

Expected output:
```
======================== 31 passed, 1 warning in 1.08s ========================
```

### Frontend Tests

From the `frontend` directory:

```bash
npm run test
```

Expected output:
```
Test Files  2 passed (2)
Tests  5 passed (5)
```

### Run All Tests

To run both backend and frontend tests:

```bash
# Backend
cd d:\appAjedrez\backend
venv\Scripts\activate
pytest tests/ -v

# Frontend
cd d:\appAjedrez\frontend
npm run test
```

## Building for Production

### Frontend Build

```bash
cd d:\appAjedrez\frontend
npm run build
```

Output: `frontend/dist/` directory with optimized static files

### Backend Production Server

**Option 1: Using Gunicorn**
```bash
cd d:\appAjedrez\backend
venv\Scripts\activate
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app
```

**Option 2: Using Uvicorn with Production Settings**
```bash
cd d:\appAjedrez\backend
venv\Scripts\activate
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## Project Structure

```
d:\appAjedrez\
├── backend/
│   ├── main.py                    # FastAPI entry point
│   ├── chess_engine.py            # Chess logic wrapper around python-chess
│   ├── game_state.py              # Game state management
│   ├── ai.py                      # AI implementations (Easy, Normal, Difficult)
│   ├── models.py                  # Pydantic request/response models
│   ├── requirements.txt           # Python dependencies
│   ├── tests/
│   │   ├── test_chess_logic.py   # Chess engine tests (8 tests)
│   │   ├── test_ai.py            # AI algorithm tests (6 tests)
│   │   └── test_endpoints.py     # API endpoint tests (17 tests)
│   └── venv/                      # Virtual environment (created)
│
├── frontend/
│   ├── src/
│   │   ├── App.tsx                # Main application component
│   │   ├── main.tsx               # React entry point
│   │   ├── components/
│   │   │   ├── Board.tsx          # Chessboard component
│   │   │   ├── PieceSquare.tsx    # Individual square component
│   │   │   ├── MoveHistory.tsx    # Move history display
│   │   │   ├── GameStatus.tsx     # Game status display
│   │   │   ├── GameControls.tsx   # Control buttons
│   │   │   ├── DifficultySelect.tsx # Difficulty selector
│   │   │   └── __tests__/
│   │   │       ├── Board.test.tsx (2 tests)
│   │   │       └── MoveHistory.test.tsx (3 tests)
│   │   └── styles/
│   │       ├── Board.module.css
│   │       ├── History.module.css
│   │       └── other CSS modules
│   ├── package.json               # Node dependencies
│   ├── vite.config.ts             # Vite dev server config
│   ├── vitest.config.ts           # Vitest testing config
│   ├── TESTING.md                 # Test results report
│   └── node_modules/              # Dependencies (created)
│
├── README.md                      # Main documentation
├── SETUP.md                       # This file
└── .gitignore                     # Git configuration
```

## Common Tasks

### Add a New Backend Dependency
```bash
cd backend
venv\Scripts\activate
pip install package_name
pip freeze > requirements.txt
```

### Add a New Frontend Dependency
```bash
cd frontend
npm install package-name
```

### Clean Up Dependencies
```bash
# Backend
cd backend
venv\Scripts\activate
pip cache purge

# Frontend
cd frontend
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

### Debugging

**Backend Logs:**
- Uvicorn logs will appear in the terminal where you started it
- Check for errors in the terminal running `python -m uvicorn main:app --reload`

**Frontend Logs:**
- Check browser console (F12 > Console tab)
- Vite dev server logs appear in the terminal

**Python Debugging:**
```python
# In main.py or other files
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.debug(f"Message: {variable}")
```

## Stopping Servers

- Press `Ctrl+C` in each terminal running a server
- Both servers will gracefully shut down

## Environment Variables

Currently, the application uses default settings:
- Backend: localhost:8000
- Frontend: localhost:5173
- CORS: Enabled for localhost:5173

To modify settings, edit in `backend/main.py` (CORS configuration).

## Troubleshooting

### "Module not found" errors
```bash
# Backend
cd backend
venv\Scripts\activate
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

### Port already in use (8000 or 5173)
```bash
# Find process using port 8000
netstat -ano | findstr :8000

# Kill process (replace PID with actual process ID)
taskkill /PID <PID> /F

# Or change Vite port in venv/vite.config.ts
```

### Virtual environment not activating
```bash
# Recreate it
rmdir /s /q venv
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### Tests failing
1. Ensure all dependencies are installed
2. Check that backend is running for API tests
3. Review error messages in test output
4. Run individual test files to isolate issues

## Additional Resources

- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **React Documentation**: https://react.dev/
- **Python Chess Documentation**: https://python-chess.readthedocs.io/
- **Vite Documentation**: https://vitejs.dev/
- **Vitest Documentation**: https://vitest.dev/

## Getting Help

If you encounter issues:

1. Check the troubleshooting section above
2. Review error messages in terminal/console
3. Verify all prerequisites are installed
4. Ensure you're in the correct directory
5. Try restarting the development servers

---

**Setup Date**: June 27, 2026
**Python Version**: 3.9+
**Node.js Version**: 18+
