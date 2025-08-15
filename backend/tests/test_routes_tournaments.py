from unittest.mock import patch, MagicMock

def test_create_tournament_success(client, db_session):
    """Test successful tournament creation via API"""
    with patch('app.routes.tournaments.TournamentService.create_tournament') as mock_create:
        mock_tournament = MagicMock()
        mock_tournament.id = 1
        mock_tournament.question = "What's better?"
        mock_tournament.prompts = [
            MagicMock(text="Option A", response="Response A", model="test-model"),
            MagicMock(text="Option B", response="Response B", model="test-model"), 
            MagicMock(text="Option C", response="Response C", model="test-model")
        ]
        mock_tournament.bracket_template = [
            [{"participant1": 0, "participant2": 1, "winner": None}],
            [{"participant1": None, "participant2": None, "winner": None}]
        ]
        mock_create.return_value = mock_tournament

        payload = {
            "question": "What's better?",
            "prompts": [
                {"text": "Option A", "model": "test-model"},
                {"text": "Option B", "model": "test-model"},
                {"text": "Option C", "model": "test-model"}
            ]
        }
        
        response = client.post('/api/tournaments', json=payload)
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['id'] == 1
        assert data['question'] == "What's better?"
        assert len(data['prompts']) == 3
        assert len(data['responses']) == 3

def test_create_tournament_missing_question(client):
    """Test tournament creation with missing question"""
    payload = {
        "prompts": [
            {"text": "Option A", "model": "test-model"},
            {"text": "Option B", "model": "test-model"}
        ]
    }
    
    response = client.post('/api/tournaments', json=payload)
    
    assert response.status_code == 400
    assert "error" in response.get_json()

def test_create_tournament_not_enough_prompts(client):
    """Test tournament creation with insufficient prompts"""
    payload = {
        "question": "What's better?",
        "prompts": [{"text": "Only one option", "model": "test-model"}]
    }
    
    response = client.post('/api/tournaments', json=payload)
    
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data

def test_create_tournament_llm_failure(client):
    """Test tournament creation with LLM failure"""
    with patch('app.routes.tournaments.TournamentService.create_tournament') as mock_create:
        mock_create.side_effect = RuntimeError("Failed to generate responses")
        
        payload = {
            "question": "What's better?",
            "prompts": [
                {"text": "Option A", "model": "test-model"},
                {"text": "Option B", "model": "test-model"}
            ]
        }
        
        response = client.post('/api/tournaments', json=payload)
        
        assert response.status_code == 502
        assert "Failed to generate responses" in response.get_json()['error']

def test_get_tournament_new_user(client):
    """Test getting tournament for new user"""
    with patch('app.routes.tournaments.TournamentService.get_tournament_with_user_state') as mock_get:
        mock_tournament = MagicMock()
        mock_tournament.id = 1
        mock_tournament.question = "Test question?"
        mock_tournament.prompts = [
            MagicMock(text="A", response="Response A", model="test-model"),
            MagicMock(text="B", response="Response B", model="test-model")
        ]
        mock_tournament.bracket_template = [
            [{"participant1": 0, "participant2": 1, "winner": None}]
        ]
        
        mock_get.return_value = (mock_tournament, None, [
            [{"participant1": 0, "participant2": 1, "winner": None}]
        ])
        
        response = client.get('/api/tournaments/1')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['id'] == 1
        assert data['user_state']['completed'] is False
        assert data['user_state']['next_match'] is None

def test_get_tournament_existing_user(client):
    """Test getting tournament for existing user"""
    with patch('app.routes.tournaments.TournamentService.get_tournament_with_user_state') as mock_get:
        mock_tournament = MagicMock()
        mock_tournament.id = 1
        mock_tournament.question = "Test question?"
        mock_tournament.prompts = [
            MagicMock(text="A", response="Response A", model="test-model"),
            MagicMock(text="B", response="Response B", model="test-model")
        ]
        mock_tournament.bracket_template = [
            [{"participant1": 0, "participant2": 1, "winner": None}]
        ]
        
        mock_user_tournament = MagicMock()
        mock_user_tournament.completed = True
        mock_user_tournament.winner_prompt_index = 1
        mock_user_tournament.get_next_votable_match.return_value = None
        mock_user_tournament.current_bracket = [
            [{"participant1": 0, "participant2": 1, "winner": 1}]
        ]
        
        mock_get.return_value = (mock_tournament, mock_user_tournament, [
            [{"participant1": 0, "participant2": 1, "winner": 1}]
        ])
        
        response = client.get('/api/tournaments/1')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['user_state']['completed'] is True
        assert data['user_state']['winner_prompt_index'] == 1
        assert data['user_bracket'][0][0]['winner'] == 1

def test_get_tournament_with_results(client):
    """Test getting tournament with results included"""
    with patch('app.routes.tournaments.TournamentService.get_tournament_with_user_state') as mock_get:
        with patch('app.routes.tournaments.TournamentService.get_prompt_rankings') as mock_rankings:
            with patch('app.routes.tournaments.TournamentService.get_participation_stats') as mock_stats:
                mock_tournament = MagicMock()
                mock_tournament.id = 1
                mock_tournament.question = "Test question?"
                mock_tournament.prompts = [MagicMock(text="A", response="Response A", model="test-model")]
                mock_tournament.bracket_template = []
                
                mock_get.return_value = (mock_tournament, None, [])
                
                mock_rankings.return_value = [
                    {
                        'prompt': 'Best option', 
                        'prompt_index': 0, 
                        'model': 'test-model',
                        'win_count': 5, 
                        'win_percentage': 50.0
                    }
                ]
                mock_stats.return_value = {
                    'total_participants': 10,
                    'completed_participants': 8,
                    'completion_rate': 80.0
                }
                
                response = client.get('/api/tournaments/1?include_results=true')
                
                assert response.status_code == 200
                data = response.get_json()
                assert 'rankings' in data
                assert 'stats' in data
                assert len(data['rankings']) == 1
                assert data['stats']['completion_rate'] == 80.0

@patch('app.routes.tournaments.get_user_id')
def test_vote_success(mock_get_user_id, client):
    """Test successful vote submission"""
    mock_get_user_id.return_value = 'test_user_123'
    
    with patch('app.routes.tournaments.TournamentService.get_tournament_with_user_state') as mock_get:
        with patch('app.routes.tournaments.TournamentService.record_vote') as mock_vote:
            mock_tournament = MagicMock()
            mock_tournament.id = 1
            mock_get.return_value = (mock_tournament, None, [])
            
            mock_vote.return_value = (
                [[{"participant1": 0, "participant2": 1, "winner": 0}]],
                False,
                None
            )
            
            with client.session_transaction() as sess:
                sess['user_id'] = 'test_user_123'
            
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
            assert 'user_id' in data

@patch('app.routes.tournaments.get_user_id')
def test_vote_tournament_completion(mock_get_user_id, client):
    """Test vote that completes tournament"""
    mock_get_user_id.return_value = 'test_user_123'
    
    with patch('app.routes.tournaments.TournamentService.get_tournament_with_user_state') as mock_get:
        with patch('app.routes.tournaments.TournamentService.record_vote') as mock_vote:
            mock_tournament = MagicMock()
            mock_tournament.id = 1 
            mock_get.return_value = (mock_tournament, None, [])
            
            mock_vote.return_value = (
                [[{"participant1": 0, "participant2": 1, "winner": 1}]],
                True,
                1
            )
            
            with client.session_transaction() as sess:
                sess['user_id'] = 'test_user_123'
            
            payload = {
                "round": 0,
                "match": 0, 
                "winner": 1
            }
            
            response = client.post('/api/tournaments/1/vote', json=payload)
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['completed'] is True
            assert data['winner_prompt_index'] == 1

def test_vote_missing_fields(client):
    """Test vote with missing required fields"""
    payload = {"round": 0}
    
    response = client.post('/api/tournaments/1/vote', json=payload)
    
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data

@patch('app.routes.tournaments.get_user_id')
def test_vote_invalid_match(mock_get_user_id, client):
    """Test vote with invalid match data"""
    mock_get_user_id.return_value = 'test_user_123'
    
    with patch('app.routes.tournaments.TournamentService.get_tournament_with_user_state') as mock_get:
        with patch('app.routes.tournaments.TournamentService.record_vote') as mock_vote:
            mock_tournament = MagicMock()
            mock_tournament.id = 1
            mock_get.return_value = (mock_tournament, None, [])
            
            mock_vote.side_effect = ValueError("Invalid match number")
            
            with client.session_transaction() as sess:
                sess['user_id'] = 'test_user_123'
            
            payload = {
                "round": 0,
                "match": 99,
                "winner": 0
            }
            
            response = client.post('/api/tournaments/1/vote', json=payload)
            
            assert response.status_code == 400
            assert "Invalid match number" in response.get_json()['error']

@patch('app.routes.tournaments.get_user_id')
def test_vote_already_voted(mock_get_user_id, client):
    """Test attempting to vote twice for same match"""
    mock_get_user_id.return_value = 'test_user_123'
    
    with patch('app.routes.tournaments.TournamentService.get_tournament_with_user_state') as mock_get:
        with patch('app.routes.tournaments.TournamentService.record_vote') as mock_vote:
            mock_tournament = MagicMock()
            mock_tournament.id = 1
            mock_get.return_value = (mock_tournament, None, [])
            
            mock_vote.side_effect = ValueError("User has already voted for this match")
            
            with client.session_transaction() as sess:
                sess['user_id'] = 'test_user_123'
            
            payload = {
                "round": 0,
                "match": 0,
                "winner": 0
            }
            
            response = client.post('/api/tournaments/1/vote', json=payload)
            
            assert response.status_code == 400
            assert "User has already voted for this match" in response.get_json()['error']

def test_get_tournaments_list(client):
    """Test getting list of all tournaments"""
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
        assert 'tournaments' in data
        tournaments = data['tournaments']
        assert len(tournaments) == 2
        assert tournaments[0]['id'] == 1
        assert tournaments[1]['completion_rate'] == 60.0
        assert tournaments[0]['num_prompts'] == 4

def test_get_models(client):
    """Test getting available models"""
    with patch('app.routes.tournaments.OpenRouterClient') as mock_client_class:
        mock_client = MagicMock()
        mock_client.get_available_models.return_value = {
            "model1": "Model 1",
            "model2": "Model 2"
        }
        mock_client_class.return_value = mock_client
        
        response = client.get('/api/tournaments/models')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'models' in data
        assert len(data['models']) == 2

def test_error_handling_in_routes(client):
    """Test generic error handling in routes"""
    with patch('app.routes.tournaments.TournamentService.get_tournament_with_user_state') as mock_get:
        mock_get.side_effect = Exception("Database connection failed")
        
        response = client.get('/api/tournaments/1')
        
        assert response.status_code == 500
        data = response.get_json()
        assert 'error' in data

def test_invalid_json_payload(client):
    """Test handling of invalid JSON payload"""
    response = client.post('/api/tournaments', 
                          data="invalid json", 
                          content_type='application/json')
    
    assert response.status_code == 400

def test_empty_payload(client):
    """Test handling of empty payload"""
    response = client.post('/api/tournaments', json={})
    
    assert response.status_code == 400
    error_data = response.get_json()
    assert 'error' in error_data
