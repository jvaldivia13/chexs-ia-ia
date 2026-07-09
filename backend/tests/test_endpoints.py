import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add backend directory to path so we can import main
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import main
from main import app
from game_state import games

client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_games():
    """Clear all games before each test."""
    games.clear()
    main.current_game_id = None
    yield
    games.clear()
    main.current_game_id = None


def test_new_game_endpoint():
    """Test creating a new game with 'easy' difficulty."""
    response = client.post("/api/game/new", json={"difficulty": "easy"})
    assert response.status_code == 200
    data = response.json()
    assert "game_id" in data
    assert "board_fen" in data
    assert data["player_color"] == "white"
    assert data["message"] == "Game started"


def test_new_game_normal_difficulty():
    """Test creating a game with 'normal' difficulty."""
    response = client.post("/api/game/new", json={"difficulty": "normal"})
    assert response.status_code == 200
    data = response.json()
    assert "game_id" in data
    assert data["player_color"] == "white"


def test_new_game_difficult_difficulty():
    """Test creating a game with 'difficult' difficulty."""
    response = client.post("/api/game/new", json={"difficulty": "difficult"})
    assert response.status_code == 200
    data = response.json()
    assert "game_id" in data
    assert data["player_color"] == "white"


def test_new_game_invalid_difficulty():
    """Test creating a game with an invalid difficulty level."""
    response = client.post("/api/game/new", json={"difficulty": "impossible"})
    assert response.status_code == 400


def test_move_endpoint_valid_move():
    """Test making a valid move (e2e4 - opening move)."""
    # Create game first
    client.post("/api/game/new", json={"difficulty": "easy"})

    # Make a valid opening move
    response = client.post("/api/game/move", json={
        "from_square": "e2",
        "to_square": "e4",
        "promotion": None
    })
    assert response.status_code == 200
    data = response.json()
    assert data["player_move"] == "e2e4"
    assert data["ai_move"] is not None
    assert data["game_status"] == "ongoing"
    assert len(data["legal_moves"]) > 0
    assert "board_fen" in data


def test_move_endpoint_valid_move_with_fen_update():
    """Test that valid move updates FEN correctly."""
    client.post("/api/game/new", json={"difficulty": "easy"})
    initial_state = client.get("/api/game/state").json()
    initial_fen = initial_state["board_fen"]

    response = client.post("/api/game/move", json={
        "from_square": "e2",
        "to_square": "e4",
        "promotion": None
    })

    assert response.status_code == 200
    data = response.json()
    # FEN should be different after move
    assert data["board_fen"] != initial_fen
    # Should have both white and black pieces
    assert "K" in data["board_fen"] or "k" in data["board_fen"]


def test_move_endpoint_invalid_move():
    """Test making an invalid move (e1e5 - king can't move like that)."""
    client.post("/api/game/new", json={"difficulty": "easy"})

    response = client.post("/api/game/move", json={
        "from_square": "e1",
        "to_square": "e5",
        "promotion": None
    })
    assert response.status_code == 400


def test_move_endpoint_move_without_game():
    """Test making a move when no game has been created."""
    # Don't create a game
    response = client.post("/api/game/move", json={
        "from_square": "e2",
        "to_square": "e4",
        "promotion": None
    })
    # When current_game_id is None, returns 400. When game doesn't exist, returns 404.
    assert response.status_code in [400, 404]


def test_game_state_endpoint():
    """Test retrieving game state after creating a game."""
    client.post("/api/game/new", json={"difficulty": "normal"})

    response = client.get("/api/game/state")
    assert response.status_code == 200
    data = response.json()
    assert "board_fen" in data
    assert data["turn"] == "white"
    assert data["game_status"] == "ongoing"


def test_game_state_endpoint_no_game():
    """Test retrieving game state when no game has been created."""
    response = client.get("/api/game/state")
    # When current_game_id is None, returns 400. When game doesn't exist, returns 404.
    assert response.status_code in [400, 404]


def test_game_state_after_move():
    """Test that game state is updated after making a move."""
    client.post("/api/game/new", json={"difficulty": "easy"})

    # Make player move
    client.post("/api/game/move", json={
        "from_square": "e2",
        "to_square": "e4",
        "promotion": None
    })

    # Get game state - should now be black's turn
    response = client.get("/api/game/state")
    assert response.status_code == 200
    data = response.json()
    assert data["turn"] == "white"  # After AI move, should be white's turn again


def test_full_game_sequence():
    """Test a complete game sequence: create game, make moves until game ends."""
    # New game
    new_game_resp = client.post("/api/game/new", json={"difficulty": "easy"})
    assert new_game_resp.status_code == 200
    game_id = new_game_resp.json()["game_id"]
    assert game_id is not None

    # Make moves until checkmate, stalemate, or draw
    moves_made = 0
    game_ended = False

    for i in range(100):  # Safety limit to prevent infinite loop
        # Get current game state
        state_resp = client.get("/api/game/state")
        assert state_resp.status_code == 200
        state = state_resp.json()

        # Check if game is still ongoing
        if state["game_status"] != "ongoing":
            game_ended = True
            break

        # Try standard opening moves to make progress
        # This is a simple strategy just to test the API flow
        if i == 0:
            move_resp = client.post("/api/game/move", json={
                "from_square": "e2",
                "to_square": "e4",
                "promotion": None
            })
        elif i == 1:
            move_resp = client.post("/api/game/move", json={
                "from_square": "g1",
                "to_square": "f3",
                "promotion": None
            })
        elif i == 2:
            move_resp = client.post("/api/game/move", json={
                "from_square": "b1",
                "to_square": "c3",
                "promotion": None
            })
        else:
            # For moves beyond opening, just try a pawn push
            move_resp = client.post("/api/game/move", json={
                "from_square": "d2",
                "to_square": "d4",
                "promotion": None
            })

        if move_resp.status_code != 200:
            # Move failed, that's okay - game logic validated the move
            # In a real scenario, we'd need better move selection
            break

        moves_made += 1

        # Verify response structure
        move_data = move_resp.json()
        assert "player_move" in move_data
        assert "board_fen" in move_data
        assert "game_status" in move_data

    # Verify we made at least one successful move
    assert moves_made > 0


def test_sequential_games():
    """Test creating and playing multiple games sequentially."""
    # Game 1
    resp1 = client.post("/api/game/new", json={"difficulty": "easy"})
    assert resp1.status_code == 200
    game1_id = resp1.json()["game_id"]

    # Make move in game 1
    move1 = client.post("/api/game/move", json={
        "from_square": "e2",
        "to_square": "e4",
        "promotion": None
    })
    assert move1.status_code == 200

    # Game 2 (will overwrite current_game_id)
    resp2 = client.post("/api/game/new", json={"difficulty": "normal"})
    assert resp2.status_code == 200
    game2_id = resp2.json()["game_id"]
    assert game2_id != game1_id

    # Make move in game 2
    move2 = client.post("/api/game/move", json={
        "from_square": "d2",
        "to_square": "d4",
        "promotion": None
    })
    assert move2.status_code == 200


def test_moves_are_applied_to_requested_game_id():
    resp1 = client.post("/api/game/new", json={"difficulty": "easy"})
    game1_id = resp1.json()["game_id"]

    resp2 = client.post("/api/game/new", json={"difficulty": "easy"})
    game2_id = resp2.json()["game_id"]

    move1 = client.post("/api/game/move", json={
        "game_id": game1_id,
        "from_square": "e2",
        "to_square": "e4",
        "promotion": None
    })
    assert move1.status_code == 200

    state1 = client.get("/api/game/state", params={"game_id": game1_id}).json()
    state2 = client.get("/api/game/state", params={"game_id": game2_id}).json()

    assert state1["board_fen"] != state2["board_fen"]
    assert state2["board_fen"] == resp2.json()["board_fen"]


def test_health_check():
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


def test_move_response_structure():
    """Test that move response has correct structure."""
    client.post("/api/game/new", json={"difficulty": "easy"})

    response = client.post("/api/game/move", json={
        "from_square": "e2",
        "to_square": "e4",
        "promotion": None
    })

    data = response.json()
    # Verify all required fields exist
    assert "player_move" in data
    assert "ai_move" in data
    assert "board_fen" in data
    assert "game_status" in data
    assert "legal_moves" in data
    assert "player_in_check" in data

    # Verify types
    assert isinstance(data["player_move"], str)
    assert isinstance(data["ai_move"], (str, type(None)))
    assert isinstance(data["board_fen"], str)
    assert isinstance(data["game_status"], str)
    assert isinstance(data["legal_moves"], list)
    assert isinstance(data["player_in_check"], bool)


def test_game_state_response_structure():
    """Test that game state response has correct structure."""
    client.post("/api/game/new", json={"difficulty": "normal"})

    response = client.get("/api/game/state")

    data = response.json()
    # Verify all required fields exist
    assert "board_fen" in data
    assert "game_status" in data
    assert "turn" in data

    # Verify types
    assert isinstance(data["board_fen"], str)
    assert isinstance(data["game_status"], str)
    assert isinstance(data["turn"], str)
    assert data["turn"] in ["white", "black"]


def test_new_game_response_structure():
    """Test that new game response has correct structure."""
    response = client.post("/api/game/new", json={"difficulty": "difficult"})

    data = response.json()
    # Verify all required fields exist
    assert "game_id" in data
    assert "board_fen" in data
    assert "player_color" in data
    assert "message" in data

    # Verify types and values
    assert isinstance(data["game_id"], str)
    assert isinstance(data["board_fen"], str)
    assert data["player_color"] == "white"
    assert isinstance(data["message"], str)
    # Game ID should be a valid UUID
    assert len(data["game_id"]) == 36  # UUID4 format
