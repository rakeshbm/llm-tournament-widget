import pytest
import json
from unittest.mock import patch, MagicMock
from app.models import Tournament, UserTournament, Vote
from app.services.tournaments import TournamentService

@pytest.fixture
def mock_db_session(monkeypatch):
    mock_session = MagicMock()
    monkeypatch.setattr("app.db.session", mock_session)
    
    mock_db = MagicMock()
    mock_db.session = mock_session
    monkeypatch.setattr("app.services.tournaments.db", mock_db)
    
    return mock_session

@pytest.fixture
def sample_tournament():
    return Tournament(
        id=1,
        question="What's the best programming language?",
        prompts=json.dumps(["Python is great", "JavaScript rocks", "Go is fast", "Rust is safe"]),
        responses=json.dumps(["Python response", "JS response", "Go response", "Rust response"]),
        bracket_template=json.dumps([
            [
                {"participant1": 0, "participant2": 1, "winner": None},
                {"participant1": 2, "participant2": 3, "winner": None}
            ],
            [
                {"participant1": None, "participant2": None, "winner": None}
            ]
        ])
    )

@patch("app.services.tournaments.generate_llm_response")
@patch("app.services.tournaments.create_bracket")
def test_create_tournament_success(mock_create_bracket, mock_generate_llm, mock_db_session):
    mock_generate_llm.side_effect = ["Response 1", "Response 2", "Response 3"]
    mock_create_bracket.return_value = [
        [
            {"participant1": 0, "participant2": 1, "winner": None},
            {"participant1": 2, "participant2": -1, "winner": 2}
        ],
        [{"participant1": None, "participant2": None, "winner": None}]
    ]
    
    prompts = ["Prompt 1", "Prompt 2", "Prompt 3"]
    question = "Test question?"
    
    tournament = TournamentService.create_tournament(question, prompts)
    
    assert tournament.question == question
    assert json.loads(tournament.prompts) == prompts
    assert json.loads(tournament.responses) == ["Response 1", "Response 2", "Response 3"]
    
    # Check that bracket was created properly
    bracket = json.loads(tournament.bracket_template)
    assert len(bracket) == 2

@patch("app.services.tournaments.generate_llm_response")  
def test_create_tournament_llm_failure(mock_generate_llm, mock_db_session):
    mock_generate_llm.side_effect = ["Good response", None, "Another good response"]
    
    prompts = ["Prompt 1", "Prompt 2", "Prompt 3"]
    question = "Test question?"
    
    with pytest.raises(RuntimeError, match="Failed to generate one or more LLM responses"):
        TournamentService.create_tournament(question, prompts)

def test_get_tournament_with_user_state_new_user(sample_tournament, mock_db_session):
    with patch('app.services.tournaments.Tournament') as mock_tournament_model:
        with patch('app.services.tournaments.UserTournament') as mock_user_tournament_model:
            # Mock Tournament.query.get_or_404
            mock_tournament_model.query.get_or_404.return_value = sample_tournament
            
            # Mock UserTournament.query.filter_by().first() returning None (new user)
            mock_user_tournament_model.query.filter_by.return_value.first.return_value = None
            
            tournament, user_tournament, user_bracket = TournamentService.get_tournament_with_user_state(1, "user123")
            
            assert tournament == sample_tournament
            assert user_tournament is None
            assert user_bracket is not None
            # New user should have empty bracket matching template
            assert len(user_bracket) == 2

def test_get_tournament_with_user_state_existing_user(sample_tournament, mock_db_session):
    existing_user_tournament = UserTournament(
        tournament_id=1,
        user_id="user123", 
        current_round=0,
        current_match=0,
        completed=False
    )
    
    existing_vote = Vote(
        tournament_id=1,
        user_id="user123",
        round_number=0,
        match_number=0,
        winner_index=0
    )
    
    with patch('app.services.tournaments.Tournament') as mock_tournament_model:
        with patch('app.services.tournaments.UserTournament') as mock_user_tournament_model:
            with patch('app.services.tournaments.Vote') as mock_vote_model:
                mock_tournament_model.query.get_or_404.return_value = sample_tournament
                mock_user_tournament_model.query.filter_by.return_value.first.return_value = existing_user_tournament
                mock_vote_model.query.filter_by.return_value.all.return_value = [existing_vote]
                
                tournament, user_tournament, user_bracket = TournamentService.get_tournament_with_user_state(1, "user123")
                
                assert tournament == sample_tournament
                assert user_tournament == existing_user_tournament
                # Bracket should reflect the user's vote
                assert user_bracket[0][0]['winner'] == 0

def test_validate_vote_success(sample_tournament, mock_db_session):
    with patch('app.services.tournaments.Vote') as mock_vote_model:
        mock_vote_model.query.filter_by.return_value.first.return_value = None  # No existing vote
        mock_vote_model.query.filter_by.return_value.all.return_value = []  # No previous votes
        
        user_bracket = TournamentService.validate_vote(sample_tournament, "user123", 0, 0, 1)
        
        assert user_bracket is not None
        assert len(user_bracket) == 2

def test_validate_vote_already_voted(sample_tournament, mock_db_session):
    existing_vote = Vote(tournament_id=1, user_id="user123", round_number=0, match_number=0, winner_index=0)
    
    with patch('app.services.tournaments.Vote') as mock_vote_model:
        mock_vote_model.query.filter_by.return_value.first.return_value = existing_vote
        
        with pytest.raises(ValueError, match="User has already voted for this match"):
            TournamentService.validate_vote(sample_tournament, "user123", 0, 0, 1)

def test_validate_vote_invalid_winner(sample_tournament, mock_db_session):
    with patch('app.services.tournaments.Vote') as mock_vote_model:
        mock_vote_model.query.filter_by.return_value.first.return_value = None
        mock_vote_model.query.filter_by.return_value.all.return_value = []
        
        with pytest.raises(ValueError, match="Winner index 5 must be one of the participants"):
            TournamentService.validate_vote(sample_tournament, "user123", 0, 0, 5)

def test_record_vote_normal_match(sample_tournament, mock_db_session):
    with patch.object(TournamentService, 'validate_vote') as mock_validate:
        with patch.object(TournamentService, 'get_or_create_user_tournament') as mock_get_user:
            with patch('app.services.tournaments.Vote') as mock_vote_model:
                
                mock_validate.return_value = json.loads(sample_tournament.bracket_template)
                mock_user_tournament = MagicMock()
                mock_user_tournament.completed = False
                mock_user_tournament.winner_prompt_index = None
                mock_get_user.return_value = mock_user_tournament
                mock_vote_model.query.filter_by.return_value.all.return_value = []
                
                user_bracket, completed, winner = TournamentService.record_vote(
                    sample_tournament, "user123", 0, 0, 1
                )
                
                assert completed is False
                assert winner is None
                assert user_bracket is not None

def test_record_vote_final_match(mock_db_session):
    # Create tournament with only final match
    final_tournament = Tournament(
        id=1,
        question="Final question?",
        prompts=json.dumps(["Option A", "Option B"]),
        responses=json.dumps(["Response A", "Response B"]),
        bracket_template=json.dumps([
            [{"participant1": 0, "participant2": 1, "winner": None}]
        ])
    )
    
    with patch.object(TournamentService, 'validate_vote') as mock_validate:
        with patch.object(TournamentService, 'get_or_create_user_tournament') as mock_get_user:
            with patch.object(TournamentService, '_update_prompt_results') as mock_update:
                with patch.object(Vote.query, 'filter_by') as mock_vote_query:
                    
                    mock_validate.return_value = json.loads(final_tournament.bracket_template)
                    mock_user_tournament = MagicMock()
                    mock_user_tournament.completed = False
                    mock_get_user.return_value = mock_user_tournament
                    mock_vote_query.return_value.all.return_value = []
                    
                    user_bracket, completed, winner = TournamentService.record_vote(
                        final_tournament, "user123", 0, 0, 1
                    )
                    
                    assert completed is True
                    assert winner == 1
                    mock_update.assert_called_once()

def test_get_or_create_user_tournament_new(mock_db_session):
    with patch('app.services.tournaments.UserTournament') as mock_user_tournament_model:
        mock_user_tournament_model.query.filter_by.return_value.first.return_value = None
        
        new_tournament = UserTournament(
            tournament_id=1,
            user_id="user123",
            current_round=0,
            current_match=0,
            completed=False
        )
        
        mock_user_tournament_model.return_value = new_tournament
        
        user_tournament = TournamentService.get_or_create_user_tournament(1, "user123")
        
        assert user_tournament.tournament_id == 1
        assert user_tournament.user_id == "user123"
        assert user_tournament.current_round == 0
        assert user_tournament.current_match == 0
        assert user_tournament.completed is False

def test_get_or_create_user_tournament_existing(mock_db_session):
    existing = UserTournament(tournament_id=1, user_id="user123", current_round=1, current_match=0)
    
    with patch('app.services.tournaments.UserTournament') as mock_user_tournament_model:
        mock_user_tournament_model.query.filter_by.return_value.first.return_value = existing
        
        user_tournament = TournamentService.get_or_create_user_tournament(1, "user123")
        
        assert user_tournament == existing

def test_get_tournament_results(sample_tournament, mock_db_session):
    mock_results = [
        MagicMock(prompt_index=1, win_count=5, total_participants=10, win_percentage=50.0),
        MagicMock(prompt_index=0, win_count=3, total_participants=10, win_percentage=30.0),
        MagicMock(prompt_index=2, win_count=2, total_participants=10, win_percentage=20.0)
    ]
    
    with patch('app.services.tournaments.Tournament') as mock_tournament_model:
        with patch('app.services.tournaments.PromptResult') as mock_prompt_result_model:
            mock_tournament_model.query.get_or_404.return_value = sample_tournament
            mock_prompt_result_model.query.filter_by.return_value.order_by.return_value.all.return_value = mock_results
            
            results = TournamentService.get_tournament_results(1)
            
            assert len(results) == 3
            assert results[0]['prompt'] == "JavaScript rocks"  # Index 1 
            assert results[0]['win_count'] == 5
            assert results[1]['prompt'] == "Python is great"   # Index 0
            assert results[1]['win_count'] == 3

def test_advance_winner_in_bracket():
    bracket = [
        [
            {"participant1": 0, "participant2": 1, "winner": None},
            {"participant1": 2, "participant2": 3, "winner": None}
        ],
        [
            {"participant1": None, "participant2": None, "winner": None}
        ]
    ]
    
    TournamentService._advance_winner_in_bracket(bracket, 0, 0, 1)
    
    assert bracket[1][0]['participant1'] == 1
    
    TournamentService._advance_winner_in_bracket(bracket, 0, 1, 3)
    
    assert bracket[1][0]['participant2'] == 3

def test_find_next_votable_match():
    bracket = [
        [
            {"participant1": 0, "participant2": 1, "winner": None},
            {"participant1": 2, "participant2": 3, "winner": None}
        ],
        [
            {"participant1": None, "participant2": None, "winner": None}
        ]
    ]
    
    next_round, next_match = TournamentService._find_next_votable_match_after_vote(bracket, 0, 0, 1)
    
    # Should find the second match in first round
    assert next_round == 0
    assert next_match == 1