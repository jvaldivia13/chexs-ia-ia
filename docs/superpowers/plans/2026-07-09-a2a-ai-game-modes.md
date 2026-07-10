# A2A AI Game Modes Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans style execution. Track each task with checkbox syntax and update as implementation progresses.

**Goal:** Add selectable game modes for Human vs AI and AI vs AI, configurable AI player profiles, an A2A-inspired local agent communication layer, optional LLM-backed move selection, and frontend playback that shows each move with at least a 2-second pause.

## Tasks

- [x] Backend models and game state support mode plus white/black AI profiles.
- [x] Backend A2A agent service accepts a message envelope, selects one AI move, applies it, and returns metadata.
- [x] API endpoints support starting configured games, human moves without bundled AI replies, and one-agent turns.
- [x] Frontend start screen supports Human vs AI and AI vs AI with per-agent profile/expertise selectors.
- [x] Frontend game loop displays each board position and waits at least 2 seconds between automated moves.
- [x] Validate with backend tests/build checks and frontend build.

## LLM Extension

- [x] Agent profiles support `provider` and `model`.
- [x] OpenAI provider uses `o4-mini` by default.
- [x] DeepSeek provider uses `deepseek-reasoner` by default.
- [x] Backend reads `OPENAI_API_KEY` and `DEEPSEEK_API_KEY` from environment or root `.env`.
- [x] LLMs receive FEN, move history, persona, expertise, and legal moves.
- [x] Backend validates LLM output against legal moves before applying it.
- [x] Backend falls back to local AI when a provider key is missing, the API call fails, or the LLM returns an invalid move.
- [x] Frontend defaults white agent to OpenAI `o4-mini`.
- [x] Frontend defaults black agent to DeepSeek `deepseek-reasoner`.

## Verification

- Backend: `35 passed`.
- Frontend: `6 passed`.
- Frontend build: successful.
