import json

from reasoning_guidelines import load_reasoning_guidelines
from chess_engine import ChessEngine
from llm_chess import _build_prompt


def test_guidelines_merge_defaults_persona_and_named_agent(tmp_path):
    config = {
        "defaults": {
            "guidelines": ["default rule"],
            "skills": [{"name": "scan", "instruction": "scan tactics"}],
        },
        "personas": {
            "aggressive": {
                "guidelines": ["attack rule"],
                "skills": [{"name": "initiative", "instruction": "keep initiative"}],
            }
        },
        "agents": {
            "Alpha": {
                "guidelines": ["agent rule"],
                "skills": [{"name": "endgame", "instruction": "activate king"}],
            }
        },
    }
    path = tmp_path / "guidelines.json"
    path.write_text(json.dumps(config), encoding="utf-8")

    result = load_reasoning_guidelines({"name": "Alpha", "persona": "aggressive"}, path)

    assert result["guidelines"] == ["default rule", "attack rule", "agent rule"]
    assert [skill["name"] for skill in result["skills"]] == ["scan", "initiative", "endgame"]


def test_invalid_guidelines_file_has_safe_empty_fallback(tmp_path):
    path = tmp_path / "invalid.json"
    path.write_text("not-json", encoding="utf-8")

    assert load_reasoning_guidelines({}, path) == {"guidelines": [], "skills": [], "summary": ""}


def test_malformed_sections_are_ignored(tmp_path):
    path = tmp_path / "malformed.json"
    path.write_text(json.dumps({"defaults": {"guidelines": None, "skills": "wrong"}}), encoding="utf-8")

    assert load_reasoning_guidelines({}, path) == {"guidelines": [], "skills": [], "summary": ""}


def test_style_summary_and_guidelines_are_merged(tmp_path):
    config = {
        "defaults": {"guidelines": ["default rule"], "skills": []},
        "styles": {
            "kasparov": {
                "summary": "Eres un experto en ajedrez que aplica las técnicas de Kaspárov.",
                "guidelines": ["ataca con iniciativa"],
                "skills": [{"name": "dynamic_imbalance", "instruction": "busca desequilibrios"}],
            }
        },
    }
    path = tmp_path / "styles.json"
    path.write_text(json.dumps(config), encoding="utf-8")

    result = load_reasoning_guidelines({"style": "kasparov"}, path)

    assert result["summary"] == "Eres un experto en ajedrez que aplica las técnicas de Kaspárov."
    assert result["guidelines"] == ["default rule", "ataca con iniciativa"]
    assert [skill["name"] for skill in result["skills"]] == ["dynamic_imbalance"]


def test_missing_style_has_no_summary(tmp_path):
    config = {
        "defaults": {"guidelines": [], "skills": []},
        "styles": {"kasparov": {"summary": "x", "guidelines": [], "skills": []}},
    }
    path = tmp_path / "no_style.json"
    path.write_text(json.dumps(config), encoding="utf-8")

    result = load_reasoning_guidelines({}, path)

    assert result["summary"] == ""


def test_prompt_contains_configured_reasoning(monkeypatch):
    monkeypatch.setattr(
        "llm_chess.format_reasoning_guidelines",
        lambda profile: "Reasoning guidelines configured for this agent:\n- Skill [forks]: Find forks.\n",
    )

    prompt = _build_prompt(ChessEngine(), {"name": "Alpha"}, ["e2e4"])

    assert "Skill [forks]: Find forks." in prompt
