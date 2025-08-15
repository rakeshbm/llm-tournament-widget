import pytest
from unittest.mock import patch, MagicMock
from app.models import Tournament, TournamentPrompt, UserTournament, Vote
from app.services.tournaments import TournamentService

class TestTournamentService:
    
    @patch("app.clients.open_router.OpenRouterClient.generate_completions")
    def test_create_tournament_success(self, mock_generate_completions, db_session):
        """Test successful tournament creation"""
        mock_generate_completions.return_value = ["Response 1", "Response 2", "Response 3"]
        
        prompts_data = [
            {"text": "Prompt 1", "model": "test-model"},
            {"text": "Prompt 2", "model": "test-model"},
            {"text": "Prompt 3", "model": "test-model"}
        ]
        question = "Test question?"
        
        tournament = TournamentService.create_tournament(question, prompts_data)
        
        assert tournament.question == question
        assert len(tournament.prompts) == 3
        
        saved_tournament = Tournament.query.get(tournament.id)
        assert saved_tournament is not None
        assert len(saved_tournament.bracket_template) == 2
        
        tournament_prompts = TournamentPrompt.query.filter_by(tournament_id=tournament.id).all()
        assert len(tournament_prompts) == 3
        assert tournament_prompts[0].text == "Prompt 1"
        assert tournament_prompts[0].response == "Response 1"
        assert tournament_prompts[0].model == "test-model"

    @patch("app.clients.open_router.OpenRouterClient.generate_completions")  
    def test_create_tournament_llm_failure(self, mock_generate_completions, db_session):
        """Test tournament creation with LLM failure"""
        mock_generate_completions.return_value = ["Good response", "", "Another good response"]
        
        prompts_data = [
            {"text": "Prompt 1", "model": "test-model"},
            {"text": "Prompt 2", "model": "test-model"},
            {"text": "Prompt 3", "model": "test-model"}
        ]
        question = "Test question?"
        
        with pytest.raises(RuntimeError, match="Failed to generate one or more LLM responses"):
            TournamentService.create_tournament(question, prompts_data)

    def test_get_tournament_with_user_state_new_user(self, sample_tournament, db_session):
        """Test getting tournament state for new user"""
        tournament, user_tournament, user_bracket = TournamentService.get_tournament_with_user_state(
            sample_tournament.id, "new_user_123"
        )
        
        assert tournament.id == sample_tournament.id
        assert user_tournament is None
        assert user_bracket is not None
        assert len(user_bracket) == 2

    def test_get_tournament_with_user_state_existing_user(self, sample_tournament, db_session):
        """Test getting tournament state for existing user"""
        user_tournament = UserTournament(
            tournament_id=sample_tournament.id,
            user_id="existing_user",
            current_bracket=[
                [{"participant1": 0, "participant2": 1, "winner": 1}],
                [{"participant1": None, "participant2": None, "winner": None}]
            ],
            completed=False
        )
        db_session.add(user_tournament)
        db_session.commit()
        
        tournament, returned_user_tournament, user_bracket = TournamentService.get_tournament_with_user_state(
            sample_tournament.id, "existing_user"
        )
        
        assert tournament.id == sample_tournament.id
        assert returned_user_tournament.id == user_tournament.id
        assert user_bracket[0][0]['winner'] == 1

    def test_validate_vote_success(self, sample_tournament, db_session):
        """Test successful vote validation"""
        user_bracket = sample_tournament.bracket_template
        
        # This should not raise an exception
        TournamentService._validate_vote(user_bracket, 0, 0, 1)

    def test_validate_vote_invalid_round(self, sample_tournament, db_session):
        """Test validation failure with invalid round number"""
        user_bracket = sample_tournament.bracket_template
        
        with pytest.raises(ValueError, match="Invalid round number"):
            TournamentService._validate_vote(user_bracket, 10, 0, 1)

    def test_validate_vote_invalid_match(self, sample_tournament, db_session):
        """Test validation failure with invalid match number"""
        user_bracket = sample_tournament.bracket_template
        
        with pytest.raises(ValueError, match="Invalid match number"):
            TournamentService._validate_vote(user_bracket, 0, 10, 1)

    def test_validate_vote_invalid_winner(self, sample_tournament, db_session):
        """Test validation failure with invalid winner index"""
        user_bracket = sample_tournament.bracket_template
        
        with pytest.raises(ValueError, match="Winner index 5 must be one of the participants"):
            TournamentService._validate_vote(user_bracket, 0, 0, 5)

    def test_validate_vote_match_already_decided(self, sample_tournament, db_session):
        """Test validation failure when match already has a winner"""
        user_bracket = [
            [{"participant1": 0, "participant2": 1, "winner": 1}],
            [{"participant1": None, "participant2": None, "winner": None}]
        ]
        
        with pytest.raises(ValueError, match="This match has already been decided"):
            TournamentService._validate_vote(user_bracket, 0, 0, 0)

    def test_validate_vote_match_not_ready(self, sample_tournament, db_session):
        """Test validation failure when match is not ready for voting"""
        user_bracket = sample_tournament.bracket_template
        
        with pytest.raises(ValueError, match="This match is not ready for voting yet"):
            TournamentService._validate_vote(user_bracket, 1, 0, 0)

    def test_record_vote_normal_match(self, sample_tournament, db_session):
        """Test recording a vote for normal match"""
        user_bracket, completed, winner = TournamentService.record_vote(
            sample_tournament, "test_user_456", 0, 0, 1
        )
        
        assert completed is False
        assert winner is None
        assert user_bracket is not None
        assert user_bracket[0][0]['winner'] == 1
        
        user_tournament = UserTournament.query.filter_by(
            tournament_id=sample_tournament.id,
            user_id="test_user_456"
        ).first()
        assert user_tournament is not None
        
        vote = Vote.query.filter_by(user_tournament_id=user_tournament.id).first()
        assert vote is not None
        assert vote.winner_index == 1

    def test_record_vote_creates_new_user_tournament(self, sample_tournament, db_session):
        """Test that record_vote creates UserTournament for new users"""
        existing = UserTournament.query.filter_by(
            tournament_id=sample_tournament.id,
            user_id="brand_new_user"
        ).first()
        assert existing is None
        
        user_bracket, completed, winner = TournamentService.record_vote(
            sample_tournament, "brand_new_user", 0, 0, 1
        )
        
        user_tournament = UserTournament.query.filter_by(
            tournament_id=sample_tournament.id,
            user_id="brand_new_user"
        ).first()
        assert user_tournament is not None
        assert user_tournament.completed is False

    def test_record_vote_final_match(self, db_session):
        """Test recording vote that completes tournament"""
        final_tournament = Tournament(
            question="Final question?",
            bracket_template=[
                [{"participant1": 0, "participant2": 1, "winner": None}]
            ]
        )
        db_session.add(final_tournament)
        db_session.flush()
        
        prompt_a = TournamentPrompt(
            tournament_id=final_tournament.id,
            position=0,
            text="Option A",
            response="Response A",
            model="test-model"
        )
        prompt_b = TournamentPrompt(
            tournament_id=final_tournament.id,
            position=1,
            text="Option B",
            response="Response B",
            model="test-model"
        )
        db_session.add_all([prompt_a, prompt_b])
        db_session.commit()
        
        user_bracket, completed, winner = TournamentService.record_vote(
            final_tournament, "final_user", 0, 0, 1
        )
        
        assert completed is True
        assert winner == 1
        
        user_tournament = UserTournament.query.filter_by(
            tournament_id=final_tournament.id,
            user_id="final_user"
        ).first()
        assert user_tournament.completed is True
        assert user_tournament.winner_prompt_index == 1
        assert user_tournament.completed_at is not None

    def test_record_vote_duplicate_vote(self, sample_tournament, db_session):
        """Test that duplicate votes are prevented"""
        # First vote
        TournamentService.record_vote(sample_tournament, "duplicate_user", 0, 0, 1)
        
        # Second vote for same match should fail
        with pytest.raises(ValueError, match="This match has already been decided"):
            TournamentService.record_vote(sample_tournament, "duplicate_user", 0, 0, 0)

    def test_get_prompt_rankings(self, sample_tournament_with_prompts, db_session):
        """Test getting tournament results"""
        user_tournament1 = UserTournament(
            tournament_id=sample_tournament_with_prompts.id,
            user_id="user1",
            completed=True,
            winner_prompt_index=0
        )
        user_tournament2 = UserTournament(
            tournament_id=sample_tournament_with_prompts.id,
            user_id="user2",
            completed=True,
            winner_prompt_index=1
        )
        user_tournament3 = UserTournament(
            tournament_id=sample_tournament_with_prompts.id,
            user_id="user3",
            completed=True,
            winner_prompt_index=0
        )
        
        db_session.add_all([user_tournament1, user_tournament2, user_tournament3])
        db_session.commit()
        
        results = TournamentService.get_prompt_rankings(sample_tournament_with_prompts.id)
        
        assert len(results) == 4
        result_by_index = {r['prompt_index']: r for r in results}
        assert result_by_index[0]['win_count'] == 2
        assert result_by_index[1]['win_count'] == 1
        assert result_by_index[0]['win_percentage'] == 66.67

    def test_get_participation_stats(self, sample_tournament, db_session):
        """Test getting tournament statistics"""
        users = ["user1", "user2", "user3"]
        for i, user_id in enumerate(users):
            user_tournament = UserTournament(
                tournament_id=sample_tournament.id,
                user_id=user_id,
                completed=(i < 2)
            )
            db_session.add(user_tournament)
        
        db_session.commit()
        
        stats = TournamentService.get_participation_stats(sample_tournament.id)
        
        assert stats['total_participants'] == 3
        assert stats['completed_participants'] == 2
        assert stats['completion_rate'] == 66.67

    def test_get_tournaments_list(self, db_session):
        """Test getting tournaments list"""
        tournament1 = Tournament(
            question="Question 1?",
            bracket_template=[[{"participant1": 0, "participant2": 1, "winner": None}]]
        )
        tournament2 = Tournament(
            question="Very long question " + "x" * 100,
            bracket_template=[[{"participant1": 0, "participant2": 1, "winner": None}]]
        )
        
        db_session.add_all([tournament1, tournament2])
        db_session.flush()
        
        prompt1a = TournamentPrompt(tournament_id=tournament1.id, position=0, text="A", response="RA", model="test-model")
        prompt1b = TournamentPrompt(tournament_id=tournament1.id, position=1, text="B", response="RB", model="test-model")
        prompt2a = TournamentPrompt(tournament_id=tournament2.id, position=0, text="X", response="RX", model="test-model")
        prompt2b = TournamentPrompt(tournament_id=tournament2.id, position=1, text="Y", response="RY", model="test-model")
        prompt2c = TournamentPrompt(tournament_id=tournament2.id, position=2, text="Z", response="RZ", model="test-model")
        
        db_session.add_all([prompt1a, prompt1b, prompt2a, prompt2b, prompt2c])
        
        user_tournament = UserTournament(
            tournament_id=tournament1.id,
            user_id="user1",
            completed=True
        )
        db_session.add(user_tournament)
        db_session.commit()
        
        results = TournamentService.get_tournaments_list()
        
        assert len(results) >= 2
        t1_result = next(r for r in results if r['id'] == tournament1.id)
        t2_result = next(r for r in results if r['id'] == tournament2.id)
        
        assert t1_result['num_prompts'] == 2
        assert t1_result['completion_rate'] == 100.0
        
        assert t2_result['question'].endswith('...')
        assert t2_result['num_prompts'] == 3
        assert t2_result['completion_rate'] == 0

    def test_advance_winner_in_bracket(self):
        """Test advancing winner to next round"""
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

    def test_advance_winner_final_round(self):
        """Test advancing winner doesn't break on final round"""
        bracket = [
            [
                {"participant1": 0, "participant2": 1, "winner": None}
            ]
        ]
        
        # Should not raise exception
        TournamentService._advance_winner_in_bracket(bracket, 0, 0, 1)
