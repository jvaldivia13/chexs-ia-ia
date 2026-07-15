import chess

from chess_engine import ChessEngine
import a2a_agents
from a2a_agents import _is_blunder, analyze_move_candidates, apply_agent_turn, select_agent_move
from llm_chess import _build_prompt


class FakeGame:
    """Minimal stand-in for game_state.Game exposing only what apply_agent_turn reads."""

    def __init__(self, engine):
        self.engine = engine
        self.move_history = []
        agent = {"name": "Test", "persona": "balanced", "expertise": "normal", "provider": "local"}
        self.white_agent = agent
        self.black_agent = agent


def test_is_blunder_detects_hanging_queen_for_defended_pawn():
    engine = ChessEngine()
    # White queen on d1 can take a pawn on d7, but a black rook on a7
    # covers d7 through the open rank, so d1d7 just gives the queen away.
    engine.set_fen("4k3/r2p4/8/8/8/8/8/3QK3 w - - 0 1")
    assert _is_blunder(engine, "d1d7") is True


def test_is_blunder_allows_a_safe_capture():
    engine = ChessEngine()
    engine.set_fen("4k3/8/5n2/8/5Q2/8/8/4K3 w - - 0 1")
    assert _is_blunder(engine, "f4f6") is False  # queen takes an undefended knight


def test_is_blunder_false_for_checkmating_move():
    engine = ChessEngine()
    # Corner back-rank mate: Ra8# gives away nothing, it ends the game.
    engine.set_fen("7k/6pp/8/8/8/8/R7/6K1 w - - 0 1")
    assert _is_blunder(engine, "a2a8") is False


def test_select_agent_move_rejects_llm_blunder_and_falls_back(monkeypatch):
    engine = ChessEngine()
    engine.set_fen("4k3/r2p4/8/8/8/8/8/3QK3 w - - 0 1")

    monkeypatch.setattr(a2a_agents, "choose_llm_move", lambda engine, profile: "d1d7")

    profile = {"provider": "openai", "persona": "balanced", "expertise": "normal"}
    move = select_agent_move(engine, profile)

    assert move != "d1d7"
    assert move in engine.get_legal_moves()


def test_candidate_analysis_returns_ranked_moves_with_variations():
    engine = ChessEngine()
    engine.set_fen("4k3/8/5n2/8/4Q3/8/8/4K3 b - - 0 1")

    candidates = analyze_move_candidates(engine, "normal")

    assert 1 <= len(candidates) <= 3
    assert candidates[0]["move"] == "f6e4"
    assert candidates[0]["principal_variation"][0] == "f6e4"
    assert candidates[0]["features"]["is_capture"] is True
    assert [item["score"] for item in candidates] == sorted(
        [item["score"] for item in candidates], reverse=True
    )


def test_llm_prompt_uses_engine_candidates_instead_of_all_legal_moves():
    engine = ChessEngine()
    candidates = [{
        "move": "e2e4",
        "score": 0.3,
        "principal_variation": ["e2e4", "e7e5"],
        "features": {"material_delta": 0, "is_capture": False, "gives_check": False},
    }]

    prompt = _build_prompt(engine, {"_candidates": candidates}, engine.get_legal_moves())

    assert "Engine-analyzed candidates" in prompt
    assert '"principal_variation": ["e2e4", "e7e5"]' in prompt
    assert "Choose only one supplied candidate" in prompt


def test_select_agent_move_rejects_candidate_outside_persona_tolerance(monkeypatch):
    engine = ChessEngine()
    candidates = [
        {"move": "e2e4", "score": 0.5},
        {"move": "a2a3", "score": 0.0},
    ]
    monkeypatch.setattr(a2a_agents, "analyze_move_candidates", lambda *args: candidates)
    monkeypatch.setattr(a2a_agents, "choose_llm_move", lambda engine, profile: "a2a3")

    move = select_agent_move(
        engine,
        {"provider": "openai", "persona": "balanced", "expertise": "normal"},
    )

    assert move == "e2e4"


def test_apply_agent_turn_does_not_pollute_history_when_make_move_fails(monkeypatch):
    engine = ChessEngine()
    game = FakeGame(engine)

    monkeypatch.setattr(a2a_agents, "select_agent_move", lambda engine, profile: "e2e4")
    monkeypatch.setattr(ChessEngine, "make_move", lambda self, *a, **k: False)

    result = apply_agent_turn(game)

    assert result["agent_move"] is None
    assert game.move_history == []


def test_apply_agent_turn_records_history_when_move_succeeds(monkeypatch):
    engine = ChessEngine()
    game = FakeGame(engine)

    monkeypatch.setattr(a2a_agents, "select_agent_move", lambda engine, profile: "e2e4")

    result = apply_agent_turn(game)

    assert result["agent_move"] == "e2e4"
    assert game.move_history == ["e2e4"]
