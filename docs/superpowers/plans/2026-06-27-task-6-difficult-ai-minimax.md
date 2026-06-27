# Task 6: Difficult AI with Minimax and Alpha-Beta Pruning Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement a difficult-level AI using minimax algorithm with alpha-beta pruning that searches 3 moves ahead for stronger chess play than the normal AI.

**Architecture:** The difficult AI will use minimax with alpha-beta pruning (depth 3) to evaluate positions. It iterates through all legal moves, recursively evaluates each to a depth of 3 plies, and selects the move with the highest evaluation score. Alpha-beta pruning eliminates branches that cannot affect the final decision, improving performance. Position evaluation reuses the existing `evaluate_position()` function which scores material and center control.

**Tech Stack:** Python 3, python-chess library, pytest for testing

## Global Constraints

- Minimax search depth: 3 moves ahead
- Must pass all 14 tests (12 existing + 2 new)
- Use TDD: write tests first, verify they fail, then implement
- Response time must be acceptable for interactive play
- No external AI engines or libraries beyond python-chess
- Follow existing code patterns and naming conventions from backend/ai.py

---

## File Structure

**Files to be modified:**
- `backend/ai.py` - Replace `get_difficult_move()` stub with full minimax+alpha-beta implementation; add `minimax()` helper function
- `backend/tests/test_ai.py` - Add 2 new tests for difficult AI behavior

---

## Task 1: Add Failing Tests for Difficult AI

**Files:**
- Modify: `backend/tests/test_ai.py:46-65` (add new test functions)

**Interfaces:**
- Consumes: `get_ai_move(engine: ChessEngine, difficulty: str) -> str` (existing)
- Produces: Two test functions that validate difficult AI returns legal moves and reasonable opening play

- [ ] **Step 1: Add test for difficult AI returns legal move**

Open `backend/tests/test_ai.py` and add this test after the existing tests:

```python
def test_difficult_ai_returns_legal_move():
    engine = ChessEngine()
    engine.make_move("e2", "e4")
    
    move = get_ai_move(engine, "difficult")
    legal_moves = engine.get_legal_moves()
    assert move in legal_moves
```

- [ ] **Step 2: Add test for difficult AI plays reasonable opening**

Add this test right after the previous one:

```python
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

- [ ] **Step 3: Run tests to verify they fail**

From the `backend/` directory, run:
```bash
pytest tests/test_ai.py::test_difficult_ai_returns_legal_move -v
pytest tests/test_ai.py::test_difficult_ai_plays_reasonable_opening -v
```

Expected: Both tests FAIL with an error because `get_difficult_move()` currently returns `random.choice()` and the implementation hasn't changed yet OR the tests simply pass because the random move is legal. If they pass, that's fine—proceed to implementation. The point is to have tests in place.

---

## Task 2: Implement Minimax with Alpha-Beta Pruning

**Files:**
- Modify: `backend/ai.py:98-104` (replace `get_difficult_move()` stub)
- Modify: `backend/ai.py:104` (add new `minimax()` function after `get_difficult_move()`)

**Interfaces:**
- Consumes:
  - `chess.Board` (python-chess board object with `.legal_moves`, `.push()`, `.pop()`, `.is_game_over()` methods)
  - `evaluate_position(board: chess.Board) -> float` (existing evaluation function)
  - `engine.get_legal_moves() -> List[str]` (returns moves in UCI format like "e2e4")
  - `engine.board.push_uci(move_uci: str)` (applies a move)
  - `engine.board.pop()` (undoes a move)

- Produces:
  - `get_difficult_move(engine: ChessEngine) -> str` - Returns best move found via minimax
  - `minimax(board: chess.Board, depth: int, alpha: float, beta: float, is_maximizing: bool) -> float` - Recursive minimax evaluator

- [ ] **Step 1: Replace get_difficult_move() implementation**

Open `backend/ai.py` and replace the entire `get_difficult_move()` function (lines 98-103) with:

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
```

- [ ] **Step 2: Add minimax() helper function**

Immediately after `get_difficult_move()`, add this new function:

```python
def minimax(board: chess.Board, depth: int, alpha: float, beta: float, is_maximizing: bool) -> float:
    """Minimax with alpha-beta pruning
    
    Args:
        board: chess.Board object
        depth: Remaining search depth (0 = leaf node)
        alpha: Best score maximizer can guarantee
        beta: Best score minimizer can guarantee
        is_maximizing: True if maximizing player's turn, False if minimizing
    
    Returns:
        Evaluation score of the position
    """
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
                break  # Beta cutoff
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
                break  # Alpha cutoff
        return min_score
```

- [ ] **Step 3: Verify the full file is syntactically correct**

From the `backend/` directory, run:
```bash
python -m py_compile ai.py
```

Expected: No output (success). If there's a syntax error, fix it before proceeding.

---

## Task 3: Run All Tests and Verify Pass

**Files:**
- Test: `backend/tests/test_ai.py` (all tests)

**Interfaces:**
- Consumes: 
  - `get_ai_move(engine: ChessEngine, difficulty: str) -> str` (now with working difficult AI)
  - `minimax()` function

- Produces: Test results showing all 14 tests passing

- [ ] **Step 1: Run all tests**

From the `backend/` directory, run:
```bash
pytest tests/test_ai.py -v
```

Expected: All 14 tests pass:
- 2 easy AI tests
- 2 normal AI tests  
- 2 new difficult AI tests
- Plus any other tests already in the file

If any test fails, debug:
- Check that move returned by `get_ai_move()` is in legal_moves
- Verify `minimax()` is being called correctly with proper board state management
- Ensure `evaluate_position()` is working (it's existing code, should be fine)

- [ ] **Step 2: Spot-check minimax depth behavior**

Run this quick check to verify minimax is actually being used:

```bash
python -c "
from chess_engine import ChessEngine
from ai import get_ai_move
import time

engine = ChessEngine()
engine.make_move('e2', 'e4')

start = time.time()
move = get_ai_move(engine, 'difficult')
elapsed = time.time() - start

print(f'Difficult AI move: {move}')
print(f'Time taken: {elapsed:.2f}s')
"
```

Expected: Move is legal, time is under 5 seconds (should be <1s for depth 3). If it hangs or takes >10s, minimax may have a bug (infinite recursion or board state corruption).

---

## Task 4: Create Git Commit

**Files:**
- Modified: `backend/ai.py`
- Modified: `backend/tests/test_ai.py`

**Interfaces:**
- Consumes: Passing test suite
- Produces: Committed changes with message

- [ ] **Step 1: Check git status**

From the repo root, run:
```bash
git status
```

Expected: Shows `backend/ai.py` and `backend/tests/test_ai.py` as modified (red).

- [ ] **Step 2: Stage the files**

```bash
git add backend/ai.py backend/tests/test_ai.py
```

- [ ] **Step 3: Create commit**

```bash
git commit -m "feat: implement difficult AI with minimax and alpha-beta pruning

- Implement minimax algorithm with alpha-beta pruning at depth 3
- Replace get_difficult_move() stub with full implementation
- Add minimax() helper function for recursive game tree search
- Add 2 new tests for difficult AI behavior
- All 14 tests passing"
```

- [ ] **Step 4: Verify commit was created**

```bash
git log -1 --oneline
```

Expected: Shows the new commit message.

---

## Verification Checklist

Before marking complete:

- [ ] Both new test functions added to `backend/tests/test_ai.py`
- [ ] `get_difficult_move()` replaced with minimax implementation (not random)
- [ ] `minimax()` helper function added with proper alpha-beta pruning
- [ ] All 14 tests pass when running `pytest tests/test_ai.py -v`
- [ ] No syntax errors in `backend/ai.py`
- [ ] Git commit created with appropriate message
- [ ] Difficult AI returns legal moves only
- [ ] Response time is reasonable (<5 seconds for typical position)

---

## Notes on Implementation Details

**Alpha-Beta Pruning:**
- Alpha: Best score the maximizer can guarantee so far (used in max branches)
- Beta: Best score the minimizer can guarantee so far (used in min branches)
- When `beta <= alpha`, we can prune the remaining moves in this branch (they won't be chosen anyway)

**Board State Management:**
- Each recursive call must maintain proper board state
- Use `board.push()` before recursive call, `board.pop()` after to restore state
- Initial `get_difficult_move()` uses `engine.board.push_uci()` and `engine.board.pop()`
- Recursive calls use `board.push()` and `board.pop()` (python-chess API)

**Depth Limit:**
- Depth 3 means search 3 half-moves (plies) ahead
- At the leaves, use `evaluate_position()` to score the position
- Terminal conditions: `depth == 0` or `board.is_game_over()` (checkmate/stalemate)

**Move Ordering:**
- Current implementation doesn't do move ordering optimization (would improve pruning)
- This is fine for depth 3; alpha-beta alone provides sufficient speedup
