import json
import os
import re
from pathlib import Path
from typing import Optional

import httpx

from chess_engine import ChessEngine


OPENAI_RESPONSES_URL = "https://api.openai.com/v1/responses"
DEEPSEEK_CHAT_URL = "https://api.deepseek.com/chat/completions"


def choose_llm_move(engine: ChessEngine, profile: dict) -> str:
    provider = profile.get("provider", "local")
    legal_moves = engine.get_legal_moves()
    if not legal_moves:
        return ""

    _load_env_file()
    if provider == "openai":
        return _choose_openai_move(engine, profile, legal_moves)
    if provider == "deepseek":
        return _choose_deepseek_move(engine, profile, legal_moves)
    return ""


def _choose_openai_move(engine: ChessEngine, profile: dict, legal_moves: list[str]) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return ""

    model = profile.get("model") or "o4-mini"
    payload = {
        "model": model,
        "input": _build_prompt(engine, profile, legal_moves),
        "text": {
            "format": {
                "type": "json_schema",
                "name": "chess_move_decision",
                "schema": _decision_schema(),
                "strict": True,
            }
        },
    }

    try:
        with httpx.Client(timeout=30) as client:
            response = client.post(
                OPENAI_RESPONSES_URL,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )
            response.raise_for_status()
        decision = _extract_openai_json(response.json())
        move = decision.get("move", "")
        return move if move in legal_moves else ""
    except Exception:
        return ""


def _choose_deepseek_move(engine: ChessEngine, profile: dict, legal_moves: list[str]) -> str:
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        return ""

    model = profile.get("model") or "deepseek-reasoner"
    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": "You are a chess agent. Return only compact JSON with keys move, plan, reason.",
            },
            {"role": "user", "content": _build_prompt(engine, profile, legal_moves)},
        ],
        "temperature": 0.2,
    }

    try:
        with httpx.Client(timeout=30) as client:
            response = client.post(
                DEEPSEEK_CHAT_URL,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )
            response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"]
        decision = _parse_json_text(content)
        move = decision.get("move", "")
        return move if move in legal_moves else ""
    except Exception:
        return ""


def _build_prompt(engine: ChessEngine, profile: dict, legal_moves: list[str]) -> str:
    color = "white" if engine.board.turn else "black"
    return (
        "Choose exactly one legal chess move for the current position.\n"
        f"Agent name: {profile.get('name', 'Agent')}\n"
        f"Agent color: {color}\n"
        f"Persona: {profile.get('persona', 'balanced')}\n"
        f"Expertise: {profile.get('expertise', 'normal')}\n"
        f"FEN: {engine.get_fen()}\n"
        f"Move history: {engine.get_move_history()}\n"
        f"Legal moves in UCI: {legal_moves}\n"
        "Return JSON only: {\"move\":\"e2e4\",\"plan\":\"...\",\"reason\":\"...\"}.\n"
        "The move value must be copied exactly from the legal moves list."
    )


def _decision_schema() -> dict:
    return {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "move": {"type": "string"},
            "plan": {"type": "string"},
            "reason": {"type": "string"},
        },
        "required": ["move", "plan", "reason"],
    }


def _extract_openai_json(data: dict) -> dict:
    if "output_text" in data:
        return _parse_json_text(data["output_text"])

    for item in data.get("output", []):
        for content in item.get("content", []):
            if content.get("type") in {"output_text", "text"} and "text" in content:
                return _parse_json_text(content["text"])
    return {}


def _parse_json_text(text: str) -> dict:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, flags=re.DOTALL)
        if not match:
            return {}
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            return {}


def _load_env_file() -> None:
    env_path = Path(__file__).resolve().parent.parent / ".env"
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value

