from unittest.mock import patch, MagicMock

def test_create_tournament_success(client, db_session):
    """Test successful tournament creation via API"""
    with patch('app.routes.tournaments.TournamentService.create_tournament') as mock_create:
        mock_tournament = MagicMock()
        mock_tournament.id = 1
        mock_tournament.question = "What's better?"
        mock_tournament.prompts = [
            MagicMock(text="Option A", response="Response A"),
            MagicMock(text="Option B", response="Response B"), 
            MagicMock(text="Option C", response="Response C")
        ]
        mock_tournament.bracket_template = [
            [{"participant1": 0, "participant2": 1, "winner": None}],
            [{"participant1": None, "participant2": None, "winner": None}]
        ]
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
        assert len(data['responses']) == 3

def test_create_tournament_missing_question(client):
    """Test tournament creation with missing question"""
    payload = {"prompts": ["Option A", "Option B"]}
    
    response = client.post('/api/tournaments', json=payload)
    
    assert response.status_code == 400
    assert "error" in response.get_json()

def test_create_tournament_not_enough_prompts(client):
    """Test tournament creation with insufficient prompts"""
    payload = {
        "question": "What's better?",
        "prompts": ["Only one option"]
    }
    
    response = client.post('/api/tournaments', json=payload)
    
    assert response.status_code == 400
    assert "Need at least 2 prompts" in response.get_json()['error']

def test_create_tournament_llm_failure(client):
    """Test tournament creation with LLM failure"""
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
    """Test getting tournament for new user"""
    with patch('app.routes.tournaments.TournamentService.get_tournament_with_user_state') as mock_get:
        mock_tournament = MagicMock()
        mock_tournament.id = 1
        mock_tournament.question = "Test question?"
        mock_tournament.prompts = [
            MagicMock(text="A", response="Response A"),
            MagicMock(text="B", response="Response B")
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
        assert data['user_state']['current_round'] == 0
        assert data['user_state']['completed'] is False

def test_get_tournament_existing_user(client):
    """Test getting tournament for existing user"""
    with patch('app.routes.tournaments.TournamentService.get_tournament_with_user_state') as mock_get:
        mock_tournament = MagicMock()
        mock_tournament.id = 1
        mock_tournament.question = "Test question?"
        mock_tournament.prompts = [
            MagicMock(text="A", response="Response A"),
            MagicMock(text="B", response="Response B")
        ]
        mock_tournament.bracket_template = [
            [{"participant1": 0, "participant2": 1, "winner": None}]
        ]
        
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
    """Test getting tournament status for new user"""
    with patch('app.routes.tournaments.TournamentService.get_tournament_with_user_state') as mock_get:
        mock_get.return_value = (MagicMock(), None, [])
        
        response = client.get('/api/tournaments/1/status')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['participated'] is False
        assert data['completed'] is False
        assert data['started_at'] is None

def test_get_tournament_status_existing_user(client):
    """Test getting tournament status for existing user"""
    with patch('app.routes.tournaments.TournamentService.get_tournament_with_user_state') as mock_get:
        mock_user_tournament = MagicMock()
        mock_user_tournament.completed = True
        mock_user_tournament.current_round = 1
        mock_user_tournament.current_match = 0
        mock_user_tournament.winner_prompt_index = 2
        mock_user_tournament.started_at.isoformat.return_value = "2024-01-01T00:00:00"
        mock_user_tournament.completed_at.isoformat.return_value = "2024-01-01T00:05:00"
        
        mock_get.return_value = (MagicMock(), mock_user_tournament, [])
        
        response = client.get('/api/tournaments/1/status')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['participated'] is True
        assert data['completed'] is True
        assert data['winner_prompt_index'] == 2

def test_vote_success(client):
    """Test successful vote submission"""
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
            assert 'user_id' in data

def test_vote_tournament_completion(client):
    """Test vote that completes tournament"""
    with patch('app.routes.tournaments.TournamentService.get_tournament_with_user_state') as mock_get:
        with patch('app.routes.tournaments.TournamentService.record_vote') as mock_vote:
            mock_tournament = MagicMock()
            mock_get.return_value = (mock_tournament, None, [])
            
            mock_vote.return_value = (
                [{"participant1": 0, "participant2": 1, "winner": 1}],
                True,
                1
            )
            
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
    assert "Missing round, match or winner fields" in response.get_json()['error']

def test_vote_invalid_match(client):
    """Test vote with invalid match data"""
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

def test_vote_already_voted(client):
    """Test attempting to vote twice for same match"""
    with patch('app.routes.tournaments.TournamentService.get_tournament_with_user_state') as mock_get:
        with patch('app.routes.tournaments.TournamentService.record_vote') as mock_vote:
            mock_tournament = MagicMock()
            mock_get.return_value = (mock_tournament, None, [])
            
            mock_vote.side_effect = ValueError("User has already voted for this match")
            
            payload = {
                "round": 0,
                "match": 0,
                "winner": 0
            }
            
            response = client.post('/api/tournaments/1/vote', json=payload)
            
            assert response.status_code == 400
            assert "User has already voted for this match" in response.get_json()['error']

def test_get_tournament_results(client):
    """Test getting tournament results"""
    with patch('app.routes.tournaments.TournamentService.get_tournament_results') as mock_results:
        with patch('app.routes.tournaments.TournamentService.get_tournament_stats') as mock_stats:
            mock_results.return_value = [
                {
                    'prompt': 'Best option',
                    'prompt_index': 0,
                    'win_count': 5,
                    'total_participants': 10,
                    'win_percentage': 50.0
                },
                {
                    'prompt': 'Second option',
                    'prompt_index': 1,
                    'win_count': 3,
                    'total_participants': 10,
                    'win_percentage': 30.0
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
            assert len(data['results']) == 2
            assert data['stats']['completion_rate'] == 80.0
            assert data['results'][0]['win_percentage'] == 50.0

def test_get_tournament_participants(client):
    """Test getting tournament participants"""
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
        assert data['participants'][0]['completed'] is True
        assert data['participants'][1]['completed'] is False

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
        assert len(data) == 2
        assert data[0]['id'] == 1
        assert data[1]['completion_rate'] == 60.0
        assert data[0]['num_prompts'] == 4

def test_session_user_id_generation(client):
    """Test that user ID is generated and persisted in session"""
    with client.session_transaction() as sess:
        assert 'user_id' not in sess
    
    with patch('app.routes.tournaments.TournamentService.get_tournament_with_user_state') as mock_get:
        mock_get.return_value = (MagicMock(), None, [])
        client.get('/api/tournaments/1/status')
    
    with client.session_transaction() as sess:
        assert 'user_id' in sess
        assert len(sess['user_id']) > 0
        
        first_user_id = sess['user_id']
    
    with patch('app.routes.tournaments.TournamentService.get_tournament_with_user_state') as mock_get:
        mock_get.return_value = (MagicMock(), None, [])
        client.get('/api/tournaments/1/status')
    
    with client.session_transaction() as sess:
        assert sess['user_id'] == first_user_id

def test_error_handling_in_routes(client):
    """Test generic error handling in routes"""
    with patch('app.routes.tournaments.TournamentService.get_tournament_with_user_state') as mock_get:
        mock_get.side_effect = Exception("Database connection failed")
        
        response = client.get('/api/tournaments/1')
        
        assert response.status_code == 500
        assert "Database connection failed" in response.get_json()['error']

def test_tournament_not_found(client):
    """Test handling of non-existent tournament"""
    from werkzeug.exceptions import NotFound
    
    with patch('app.routes.tournaments.TournamentService.get_tournament_with_user_state') as mock_get:
        mock_get.side_effect = NotFound("Tournament not found")
        
        response = client.get('/api/tournaments/999')
        
        assert response.status_code in [404, 500]

def test_invalid_json_payload(client):
    """Test handling of invalid JSON payload"""
    response = client.post('/api/tournaments', 
                          data="invalid json", 
                          content_type='application/json')
    
    assert response.status_code in [400, 500]

def test_empty_payload(client):
    """Test handling of empty payload"""
    response = client.post('/api/tournaments', json={})
    
    assert response.status_code == 400
    error_data = response.get_json()
    assert 'error' in error_data

def test_vote_with_none_values(client):
    """Test vote endpoint with None values"""
    payload = {
        "round": None,
        "match": 0,
        "winner": 1
    }
    
    response = client.post('/api/tournaments/1/vote', json=payload)
    
    assert response.status_code == 400
    assert "Missing round, match or winner fields" in response.get_json()['error']