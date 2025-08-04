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
    app.secret_key = 'test-secret-key'

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

def test_create_tournament_success(client):
    with patch('app.routes.tournaments.TournamentService.create_tournament') as mock_create:
        mock_tournament = MagicMock()
        mock_tournament.id = 1
        mock_tournament.question = "What's better?"
        mock_tournament.prompts = json.dumps(["Option A", "Option B", "Option C"])
        mock_tournament.responses = json.dumps(["Response A", "Response B", "Response C"])
        mock_tournament.bracket_template = json.dumps([
            [{"participant1": 0, "participant2": 1, "winner": None}],
            [{"participant1": None, "participant2": None, "winner": None}]
        ])
        mock_create.return_value = mock_tournament

        payload = {
            "question": "What's better?",
            "prompts": ["Option A", "Option B", "Option C"]
        }
        
        response = client.post('/api/tournaments', json=payload)
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['id'] == 1
        assert data['question'] == "What's better?"
        assert len(data['prompts']) == 3

def test_create_tournament_missing_question(client):
    payload = {"prompts": ["Option A", "Option B"]}
    
    response = client.post('/api/tournaments', json=payload)
    
    assert response.status_code == 400
    assert "error" in response.get_json()

def test_create_tournament_not_enough_prompts(client):
    payload = {
        "question": "What's better?",
        "prompts": ["Only one option"]
    }
    
    response = client.post('/api/tournaments', json=payload)
    
    assert response.status_code == 400
    assert "Need at least 2 prompts" in response.get_json()['error']

def test_create_tournament_llm_failure(client):
    with patch('app.routes.tournaments.TournamentService.create_tournament') as mock_create:
        mock_create.side_effect = RuntimeError("Failed to generate responses")
        
        payload = {
            "question": "What's better?",
            "prompts": ["Option A", "Option B"]
        }
        
        response = client.post('/api/tournaments', json=payload)
        
        assert response.status_code == 502
        assert "Failed to generate responses" in response.get_json()['error']

def test_get_tournament_new_user(client):
    with patch('app.routes.tournaments.TournamentService.get_tournament_with_user_state') as mock_get:
        mock_tournament = MagicMock()
        mock_tournament.id = 1
        mock_tournament.question = "Test question?"
        mock_tournament.prompts = json.dumps(["A", "B"])
        mock_tournament.responses = json.dumps(["Response A", "Response B"])  
        mock_tournament.bracket_template = json.dumps([
            [{"participant1": 0, "participant2": 1, "winner": None}]
        ])
        
        mock_get.return_value = (mock_tournament, None, [
            [{"participant1": 0, "participant2": 1, "winner": None}]
        ])
        
        response = client.get('/api/tournaments/1')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['id'] == 1
        assert data['user_state']['current_round'] == 0
        assert data['user_state']['completed'] is False

def test_get_tournament_existing_user(client):
    with patch('app.routes.tournaments.TournamentService.get_tournament_with_user_state') as mock_get:
        mock_tournament = MagicMock()
        mock_tournament.id = 1
        mock_tournament.question = "Test question?"
        mock_tournament.prompts = json.dumps(["A", "B"])
        mock_tournament.responses = json.dumps(["Response A", "Response B"])
        mock_tournament.bracket_template = json.dumps([
            [{"participant1": 0, "participant2": 1, "winner": None}]
        ])
        
        mock_user_tournament = MagicMock()
        mock_user_tournament.current_round = 0
        mock_user_tournament.current_match = 0
        mock_user_tournament.completed = True
        mock_user_tournament.winner_prompt_index = 1
        
        mock_get.return_value = (mock_tournament, mock_user_tournament, [
            [{"participant1": 0, "participant2": 1, "winner": 1}]
        ])
        
        response = client.get('/api/tournaments/1')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['user_state']['completed'] is True
        assert data['user_state']['winner_prompt_index'] == 1

def test_get_tournament_status_new_user(client):
    with patch('app.routes.tournaments.TournamentService.get_tournament_with_user_state') as mock_get:
        mock_get.return_value = (MagicMock(), None, [])
        
        response = client.get('/api/tournaments/1/status')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['participated'] is False
        assert data['completed'] is False
        assert data['started_at'] is None

def test_vote_success(client):
    with patch('app.routes.tournaments.TournamentService.get_tournament_with_user_state') as mock_get:
        with patch('app.routes.tournaments.TournamentService.record_vote') as mock_vote:
            mock_tournament = MagicMock()
            mock_get.return_value = (mock_tournament, None, [])
            
            mock_vote.return_value = (
                [{"participant1": 0, "participant2": 1, "winner": 0}],
                False,
                None
            )
            
            payload = {
                "round": 0,
                "match": 0, 
                "winner": 0
            }
            
            response = client.post('/api/tournaments/1/vote', json=payload)
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['completed'] is False
            assert 'user_bracket' in data

def test_vote_missing_fields(client):
    payload = {"round": 0}  # Missing match and winner
    
    response = client.post('/api/tournaments/1/vote', json=payload)
    
    assert response.status_code == 400
    assert "Missing round, match or winner fields" in response.get_json()['error']

def test_vote_invalid_match(client):
    with patch('app.routes.tournaments.TournamentService.get_tournament_with_user_state') as mock_get:
        with patch('app.routes.tournaments.TournamentService.record_vote') as mock_vote:
            mock_tournament = MagicMock()
            mock_get.return_value = (mock_tournament, None, [])
            
            mock_vote.side_effect = ValueError("Invalid match number")
            
            payload = {
                "round": 0,
                "match": 99,
                "winner": 0
            }
            
            response = client.post('/api/tournaments/1/vote', json=payload)
            
            assert response.status_code == 400
            assert "Invalid match number" in response.get_json()['error']

def test_get_tournament_results(client):
    with patch('app.routes.tournaments.TournamentService.get_tournament_results') as mock_results:
        with patch('app.routes.tournaments.TournamentService.get_tournament_stats') as mock_stats:
            mock_results.return_value = [
                {
                    'prompt': 'Best option',
                    'prompt_index': 0,
                    'win_count': 5,
                    'total_participants': 10,
                    'win_percentage': 50.0
                }
            ]
            
            mock_stats.return_value = {
                'total_participants': 10,
                'completed_participants': 8,
                'completion_rate': 80.0
            }
            
            response = client.get('/api/tournaments/1/results')
            
            assert response.status_code == 200
            data = response.get_json()
            assert 'results' in data
            assert 'stats' in data
            assert len(data['results']) == 1
            assert data['stats']['completion_rate'] == 80.0

def test_get_tournament_participants(client):
    with patch('app.routes.tournaments.TournamentService.get_tournament_participants') as mock_participants:
        mock_participants.return_value = [
            {
                'user_id': 'abc123...',
                'completed': True,
                'current_round': 1,
                'current_match': 0,
                'started_at': '2024-01-01T00:00:00',
                'completed_at': '2024-01-01T00:05:00'
            },
            {
                'user_id': 'def456...',
                'completed': False,
                'current_round': 0,
                'current_match': 1,
                'started_at': '2024-01-01T00:02:00',
                'completed_at': None
            }
        ]
        
        response = client.get('/api/tournaments/1/participants')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'participants' in data
        assert 'total_count' in data
        assert data['total_count'] == 2
        assert len(data['participants']) == 2

def test_get_tournaments_list(client):
    with patch('app.routes.tournaments.TournamentService.get_tournaments_list') as mock_list:
        mock_list.return_value = [
            {
                'id': 1,
                'question': 'Short question?',
                'num_prompts': 4,
                'created_at': '2024-01-01T00:00:00',
                'total_participants': 15,
                'completed_participants': 12,
                'completion_rate': 80.0
            },
            {
                'id': 2,
                'question': 'Very long question that gets truncated...',
                'num_prompts': 3,
                'created_at': '2024-01-02T00:00:00', 
                'total_participants': 5,
                'completed_participants': 3,
                'completion_rate': 60.0
            }
        ]
        
        response = client.get('/api/tournaments')
        
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 2
        assert data[0]['id'] == 1
        assert data[1]['completion_rate'] == 60.0

def test_session_user_id_generation(client):
    # Test that user ID is generated and persisted in session
    with client.session_transaction() as sess:
        assert 'user_id' not in sess
    
    # Make a request that triggers get_user_id()
    with patch('app.routes.tournaments.TournamentService.get_tournament_with_user_state') as mock_get:
        mock_get.return_value = (MagicMock(), None, [])
        client.get('/api/tournaments/1/status')
    
    with client.session_transaction() as sess:
        assert 'user_id' in sess
        assert len(sess['user_id']) > 0

def test_error_handling_in_routes(client):
    # Test generic error handling
    with patch('app.routes.tournaments.TournamentService.get_tournament_with_user_state') as mock_get:
        mock_get.side_effect = Exception("Database connection failed")
        
        response = client.get('/api/tournaments/1')
        
        assert response.status_code == 500
        assert "Database connection failed" in response.get_json()['error']