import json
import pytest
from unittest.mock import patch, MagicMock
from flask import Flask
from app.routes.tournaments import bp as tournaments_bp
from app import db

@pytest.fixture
def app():
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    app.register_blueprint(tournaments_bp, url_prefix='/api/tournaments')

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@patch('app.routes.tournaments.TournamentService.create_tournament')
def test_create_tournament_success(mock_create_tournament, client):
    mock_tournament = MagicMock()
    mock_tournament.id = 1
    mock_tournament.question = "Sample question?"
    mock_tournament.prompts = json.dumps(["p1", "p2"])
    mock_tournament.responses = json.dumps(["r1", "r2"])
    mock_tournament.bracket = json.dumps([{"some": "bracket"}])
    mock_create_tournament.return_value = mock_tournament

    payload = {
        "question": "Sample question?",
        "prompts": ["p1", "p2"]
    }
    response = client.post('/api/tournaments', json=payload)
    assert response.status_code == 201

    data = response.get_json()
    assert data['id'] == 1
    assert data['question'] == "Sample question?"
    assert data['prompts'] == ["p1", "p2"]
    assert data['responses'] == ["r1", "r2"]
    assert data['bracket'] == [{"some": "bracket"}]

def test_create_tournament_bad_request(client):
    response = client.post('/api/tournaments', json={"question": "Q", "prompts": ["only one"]})
    assert response.status_code == 400
    assert "error" in response.get_json()

@patch('app.routes.tournaments.Tournament.query')
def test_get_tournament_success(mock_query, client):
    mock_tournament = MagicMock()
    mock_tournament.id = 1
    mock_tournament.question = "Sample question?"
    mock_tournament.prompts = json.dumps(["p1", "p2"])
    mock_tournament.responses = json.dumps(["r1", "r2"])
    mock_tournament.bracket = json.dumps([{"rounds": "something"}])
    mock_tournament.winner_prompt = "p1"
    mock_tournament.completed = False

    mock_query.get_or_404.return_value = mock_tournament

    response = client.get('/api/tournaments/1')
    assert response.status_code == 200

    data = response.get_json()
    assert data['id'] == 1
    assert data['winner_prompt'] == "p1"
    assert data['completed'] is False

@patch('app.routes.tournaments.Tournament.query')
@patch('app.routes.tournaments.TournamentService.vote')
def test_vote_success(mock_vote, mock_query, client):
    mock_tournament = MagicMock()
    mock_tournament.id = 1
    mock_tournament.prompts = json.dumps(["p1", "p2"])
    mock_tournament.completed = False
    mock_tournament.winner_prompt = None
    mock_tournament.bracket = json.dumps([{}])

    mock_query.get_or_404.return_value = mock_tournament

    mock_vote.return_value = (
        [{"participant1": 0, "participant2": 1, "winner": 0}],  # bracket
        False,  # completed
        None  # winner_prompt
    )

    payload = {
        "round": 0,
        "match": 0,
        "winner": 0
    }
    response = client.post('/api/tournaments/1/vote', json=payload)
    assert response.status_code == 200

    data = response.get_json()
    assert "bracket" in data
    assert data['completed'] is False
    assert data['winner_prompt'] is None

def test_vote_bad_request_missing_fields(client):
    response = client.post('/api/tournaments/1/vote', json={})
    assert response.status_code == 404

@patch('app.routes.tournaments.Tournament.query')
@patch('app.routes.tournaments.TournamentService.vote')
def test_vote_service_raises_error(mock_vote, mock_query, client):
    mock_tournament = MagicMock()
    mock_tournament.id = 1
    mock_tournament.prompts = json.dumps(["p1", "p2"])
    mock_tournament.completed = False
    mock_tournament.winner_prompt = None
    mock_tournament.bracket = json.dumps([{}])

    mock_query.get_or_404.return_value = mock_tournament

    mock_vote.side_effect = ValueError("Invalid match number")

    payload = {
        "round": 0,
        "match": 5,
        "winner": 0
    }
    response = client.post('/api/tournaments/1/vote', json=payload)
    assert response.status_code == 400
    assert "Invalid match number" in response.get_json().get("error", "")

@patch('app.routes.tournaments.Tournament.query')
def test_get_tournaments_success(mock_query, client):
    mock_t1 = MagicMock()
    mock_t1.id = 1
    mock_t1.question = "Q1"
    mock_t1.prompts = json.dumps(["p1", "p2"])
    mock_t1.completed = False
    from datetime import datetime
    mock_t1.created_at = datetime.utcnow()

    mock_t2 = MagicMock()
    mock_t2.id = 2
    mock_t2.question = "Q2 with a very long question text that should be truncated when returned in the list view." * 5
    mock_t2.prompts = json.dumps(["p1", "p2", "p3"])
    mock_t2.completed = True
    mock_t2.created_at = datetime.utcnow()

    mock_query.order_by.return_value.all.return_value = [mock_t1, mock_t2]

    response = client.get('/api/tournaments')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 2

@patch('app.routes.tournaments.TournamentService.create_tournament')
def test_create_tournament_runtime_error(mock_create_tournament, client):
    mock_create_tournament.side_effect = RuntimeError("Failed to generate one or more LLM responses.")

    payload = {
        "question": "What is the best way to start a project?",
        "prompts": ["prompt1", "prompt2"]
    }

    response = client.post('/api/tournaments', json=payload)
    assert response.status_code == 502
    assert response.get_json() == {"error": "Failed to generate one or more LLM responses."}

@patch('app.routes.tournaments.TournamentService.create_tournament')
def test_create_tournament_unexpected_error(mock_create_tournament, client):
    mock_create_tournament.side_effect = Exception("Some unexpected issue")

    payload = {
        "question": "What is the best way to start a project?",
        "prompts": ["prompt1", "prompt2"]
    }

    response = client.post('/api/tournaments', json=payload)
    assert response.status_code == 500
    assert response.get_json() == {"error": "Unexpected error occurred."}
