import json
import logging
import os
import re
from pathlib import Path
from typing import Optional

import httpx
from dotenv import load_dotenv

from chess_engine import ChessEngine
from reasoning_guidelines import format_reasoning_guidelines

logger = logging.getLogger(__name__)

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

OPENAI_RESPONSES_URL = "https://api.openai.com/v1/responses"
DEEPSEEK_CHAT_URL = "https://api.deepseek.com/chat/completions"


def choose_llm_move(engine: ChessEngine, profile: dict) -> str:
    provider = profile.get("provider", "local")
    legal_moves = engine.get_legal_moves()
    if not legal_moves:
        return ""

    if provider == "openai":
        return _choose_openai_move(engine, profile, legal_moves)
    if provider == "deepseek":
        return _choose_deepseek_move(engine, profile, legal_moves)
    return ""


def _choose_openai_move(engine: ChessEngine, profile: dict, legal_moves: list[str]) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.warning("OPENAI_API_KEY not set; falling back to local engine for agent %s", profile.get("name"))
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
        if move in legal_moves:
            return move
        logger.warning("OpenAI returned a non-legal or empty move for agent %s: %r", profile.get("name"), move)
        return ""
    except Exception:
        logger.warning("OpenAI move request failed for agent %s; falling back to local engine", profile.get("name"), exc_info=True)
        return ""


def _choose_deepseek_move(engine: ChessEngine, profile: dict, legal_moves: list[str]) -> str:
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        logger.warning("DEEPSEEK_API_KEY not set; falling back to local engine for agent %s", profile.get("name"))
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
        if move in legal_moves:
            return move
        logger.warning("DeepSeek returned a non-legal or empty move for agent %s: %r", profile.get("name"), move)
        return ""
    except Exception:
        logger.warning("DeepSeek move request failed for agent %s; falling back to local engine", profile.get("name"), exc_info=True)
        return ""


def _build_prompt(engine: ChessEngine, profile: dict, legal_moves: list[str]) -> str:
    color = "white" if engine.board.turn else "black"
    candidates = profile.get("_candidates") or []
    configured_reasoning = format_reasoning_guidelines(profile)
    decision_context = (
        "Engine-analyzed candidates (score is from your perspective):\n"
        f"{json.dumps(candidates, ensure_ascii=False)}\n"
        "Choose only one supplied candidate after comparing its principal variation and features.\n"
        if candidates
        else f"Legal moves in UCI: {legal_moves}\n"
    )
    return (
        "Choose exactly one legal chess move for the current position.\n"
        f"Agent name: {profile.get('name', 'Agent')}\n"
        f"Agent color: {color}\n"
        f"Persona: {profile.get('persona', 'balanced')}\n"
        f"Expertise: {profile.get('expertise', 'normal')}\n"
        f"{configured_reasoning}"
        f"FEN: {engine.get_fen()}\n"
        f"Move history: {engine.get_move_history()}\n"
        f"{decision_context}"
        "Return JSON only: {\"move\":\"e2e4\",\"plan\":\"...\",\"reason\":\"...\"}.\n"
        "The move value must be copied exactly from the supplied move choices."
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
