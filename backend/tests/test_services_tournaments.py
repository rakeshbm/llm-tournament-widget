import pytest
from unittest.mock import patch
from app.models import Tournament, TournamentPrompt, UserTournament, Vote
from app.services.tournaments import TournamentService

class TestTournamentService:
    
    @patch("app.services.tournaments.generate_llm_response")
    @patch("app.services.tournaments.create_bracket")
    def test_create_tournament_success(self, mock_create_bracket, mock_generate_llm, db_session):
        """Test successful tournament creation"""
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
        assert len(tournament.prompts) == 3
        
        saved_tournament = Tournament.query.get(tournament.id)
        assert saved_tournament is not None
        assert len(saved_tournament.bracket_template) == 2
        
        tournament_prompts = TournamentPrompt.query.filter_by(tournament_id=tournament.id).all()
        assert len(tournament_prompts) == 3
        assert tournament_prompts[0].text == "Prompt 1"
        assert tournament_prompts[0].response == "Response 1"

    @patch("app.services.tournaments.generate_llm_response")  
    def test_create_tournament_llm_failure(self, mock_generate_llm, db_session):
        """Test tournament creation with LLM failure"""
        mock_generate_llm.side_effect = ["Good response", None, "Another good response"]
        
        prompts = ["Prompt 1", "Prompt 2", "Prompt 3"]
        question = "Test question?"
        
        with pytest.raises(RuntimeError, match="Failed to generate one or more LLM responses"):
            TournamentService.create_tournament(question, prompts)

    def test_get_tournament_with_user_state_new_user(self, sample_tournament, db_session):
        """Test getting tournament state for new user"""
        tournament, user_tournament, user_bracket = TournamentService.get_tournament_with_user_state(
            sample_tournament.id, "new_user_123"
        )
        
        assert tournament.id == sample_tournament.id
        assert user_tournament is None
        assert user_bracket is not None
        assert len(user_bracket) == 2

    def test_get_tournament_with_user_state_existing_user(self, sample_tournament, sample_user_tournament, db_session):
        """Test getting tournament state for existing user with votes"""
        vote = Vote(
            user_tournament_id=sample_user_tournament.id,
            round_number=0,
            match_number=0,
            winner_index=1
        )
        db_session.add(vote)
        db_session.commit()
        
        tournament, user_tournament, user_bracket = TournamentService.get_tournament_with_user_state(
            sample_tournament.id, sample_user_tournament.user_id
        )
        
        assert tournament.id == sample_tournament.id
        assert user_tournament.id == sample_user_tournament.id
        assert user_bracket[0][0]['winner'] == 1

    def test_validate_vote_success(self, sample_tournament, db_session):
        """Test successful vote validation"""
        bracket_template = sample_tournament.bracket_template
        user_bracket = TournamentService._build_user_bracket(bracket_template, [])
        
        TournamentService.validate_vote(user_bracket, 0, 0, 1, [])

    def test_validate_vote_already_voted(self, sample_tournament, sample_user_tournament, db_session):
        """Test validation failure when user already voted"""
        vote = Vote(
            user_tournament_id=sample_user_tournament.id,
            round_number=0,
            match_number=0,
            winner_index=0
        )
        db_session.add(vote)
        db_session.commit()
        
        bracket_template = sample_tournament.bracket_template
        user_bracket = TournamentService._build_user_bracket(bracket_template, [vote])
        
        with pytest.raises(ValueError, match="User has already voted for this match"):
            TournamentService.validate_vote(user_bracket, 0, 0, 1, [vote])

    def test_validate_vote_invalid_winner(self, sample_tournament, db_session):
        """Test validation failure with invalid winner index"""
        bracket_template = sample_tournament.bracket_template
        user_bracket = TournamentService._build_user_bracket(bracket_template, [])
        
        with pytest.raises(ValueError, match="Winner index 5 must be one of the participants"):
            TournamentService.validate_vote(user_bracket, 0, 0, 5, [])

    def test_validate_vote_invalid_round(self, sample_tournament, db_session):
        """Test validation failure with invalid round number"""
        bracket_template = sample_tournament.bracket_template
        user_bracket = TournamentService._build_user_bracket(bracket_template, [])
        
        with pytest.raises(ValueError, match="Invalid round number"):
            TournamentService.validate_vote(user_bracket, 10, 0, 1, [])

    def test_validate_vote_invalid_match(self, sample_tournament, db_session):
        """Test validation failure with invalid match number"""
        bracket_template = sample_tournament.bracket_template
        user_bracket = TournamentService._build_user_bracket(bracket_template, [])
        
        with pytest.raises(ValueError, match="Invalid match number"):
            TournamentService.validate_vote(user_bracket, 0, 10, 1, [])

    def test_validate_vote_match_not_ready(self, sample_tournament, db_session):
        """Test validation failure when match is not ready for voting"""
        bracket_template = sample_tournament.bracket_template
        user_bracket = TournamentService._build_user_bracket(bracket_template, [])
        
        with pytest.raises(ValueError, match="This match is not ready for voting yet"):
            TournamentService.validate_vote(user_bracket, 1, 0, 0, [])

    def test_validate_vote_match_already_decided(self, sample_tournament, db_session):
        """Test validation failure when match already has a winner"""
        vote = Vote(
            user_tournament_id=1,
            round_number=0,
            match_number=0,
            winner_index=1
        )
        
        bracket_template = sample_tournament.bracket_template
        user_bracket = TournamentService._build_user_bracket(bracket_template, [vote])
        
        with pytest.raises(ValueError, match="User has already voted for this match"):
            TournamentService.validate_vote(user_bracket, 0, 0, 0, [vote])

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
        assert len(user_tournament.votes) == 1
        assert user_tournament.votes[0].winner_index == 1

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
        assert user_tournament.current_round >= 0
        assert user_tournament.current_match >= 0
        assert user_tournament.completed is False

    def test_record_vote_updates_current_position(self, sample_tournament, db_session):
        """Test that record_vote updates user's current position"""
        user_bracket, completed, winner = TournamentService.record_vote(
            sample_tournament, "position_user", 0, 0, 1
        )
        
        user_tournament = UserTournament.query.filter_by(
            tournament_id=sample_tournament.id,
            user_id="position_user"
        ).first()
        
        assert user_tournament.current_round >= 0
        assert user_tournament.current_match >= 0

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
            response="Response A"
        )
        prompt_b = TournamentPrompt(
            tournament_id=final_tournament.id,
            position=1,
            text="Option B",
            response="Response B"
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

    def test_get_tournament_results(self, sample_tournament_with_prompts, db_session):
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
        
        results = TournamentService.get_tournament_results(sample_tournament_with_prompts.id)
        
        assert len(results) == 4
        result_by_index = {r['prompt_index']: r for r in results}
        assert result_by_index[0]['win_count'] == 2
        assert result_by_index[1]['win_count'] == 1
        assert result_by_index[0]['win_percentage'] == 66.67

    def test_get_tournament_stats(self, sample_tournament, db_session):
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
        
        stats = TournamentService.get_tournament_stats(sample_tournament.id)
        
        assert stats['total_participants'] == 3
        assert stats['completed_participants'] == 2
        assert stats['completion_rate'] == 66.67

    def test_get_tournament_participants(self, sample_tournament, db_session):
        """Test getting tournament participants"""
        users = ["user1", "user2"]
        for user_id in users:
            user_tournament = UserTournament(
                tournament_id=sample_tournament.id,
                user_id=user_id,
                current_round=0,
                current_match=0
            )
            db_session.add(user_tournament)
        
        db_session.commit()
        
        participants = TournamentService.get_tournament_participants(sample_tournament.id)
        
        assert len(participants) == 2
        assert all('user_id' in p for p in participants)
        assert all('completed' in p for p in participants)
        assert all('started_at' in p for p in participants)

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
        
        prompt1a = TournamentPrompt(tournament_id=tournament1.id, position=0, text="A", response="RA")
        prompt1b = TournamentPrompt(tournament_id=tournament1.id, position=1, text="B", response="RB")
        prompt2a = TournamentPrompt(tournament_id=tournament2.id, position=0, text="X", response="RX")
        prompt2b = TournamentPrompt(tournament_id=tournament2.id, position=1, text="Y", response="RY")
        prompt2c = TournamentPrompt(tournament_id=tournament2.id, position=2, text="Z", response="RZ")
        
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

    def test_build_user_bracket_empty_votes(self):
        """Test bracket building with no votes"""
        bracket_template = [
            [
                {"participant1": 0, "participant2": 1, "winner": None},
                {"participant1": 2, "participant2": 3, "winner": None}
            ],
            [
                {"participant1": None, "participant2": None, "winner": None}
            ]
        ]
        
        user_bracket = TournamentService._build_user_bracket(bracket_template, [])
        
        assert user_bracket[0][0]['winner'] is None
        assert user_bracket[0][1]['winner'] is None
        assert user_bracket[1][0]['participant1'] is None

    def test_build_user_bracket_with_votes(self):
        """Test bracket building with votes"""
        bracket_template = [
            [
                {"participant1": 0, "participant2": 1, "winner": None},
                {"participant1": 2, "participant2": 3, "winner": None}
            ],
            [
                {"participant1": None, "participant2": None, "winner": None}
            ]
        ]
        
        vote2 = Vote(user_tournament_id=1, round_number=0, match_number=1, winner_index=3)
        vote1 = Vote(user_tournament_id=1, round_number=0, match_number=0, winner_index=1)
        votes = [vote2, vote1]
        
        user_bracket = TournamentService._build_user_bracket(bracket_template, votes)
        
        assert user_bracket[0][0]['winner'] == 1
        assert user_bracket[0][1]['winner'] == 3
        assert user_bracket[1][0]['participant1'] == 1
        assert user_bracket[1][0]['participant2'] == 3

    def test_build_user_bracket_skip_existing_winners(self):
        """Test that bracket building doesn't overwrite existing winners"""
        bracket_template = [
            [
                {"participant1": 0, "participant2": 1, "winner": 0},
                {"participant1": 2, "participant2": 3, "winner": None}
            ],
            [
                {"participant1": None, "participant2": None, "winner": None}
            ]
        ]
        
        vote = Vote(user_tournament_id=1, round_number=0, match_number=0, winner_index=1)
        votes = [vote]
        
        user_bracket = TournamentService._build_user_bracket(bracket_template, votes)
        
        assert user_bracket[0][0]['winner'] == 0

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
        
        TournamentService._advance_winner_in_bracket(bracket, 0, 0, 1)
        assert bracket[0][0]['winner'] is None

    def test_find_next_votable_match_normal_case(self):
        """Test finding next votable match"""
        bracket = [
            [
                {"participant1": 0, "participant2": 1, "winner": 1},
                {"participant1": 2, "participant2": 3, "winner": None}
            ],
            [
                {"participant1": None, "participant2": None, "winner": None}
            ]
        ]
        
        next_round, next_match = TournamentService._find_next_votable_match_after_vote(bracket)
        
        assert next_round == 0
        assert next_match == 1

    def test_find_next_votable_match_none_available(self):
        """Test finding next votable match when none available"""
        bracket = [
            [
                {"participant1": 0, "participant2": 1, "winner": 1}
            ]
        ]
        
        next_round, next_match = TournamentService._find_next_votable_match_after_vote(bracket)
        
        assert next_round is None
        assert next_match is None

    def test_find_next_votable_match_with_byes(self):
        """Test finding next votable match when participants have byes"""
        bracket = [
            [
                {"participant1": 0, "participant2": -1, "winner": 0},
                {"participant1": 2, "participant2": 3, "winner": None}
            ],
            [
                {"participant1": None, "participant2": None, "winner": None}
            ]
        ]
        
        next_round, next_match = TournamentService._find_next_votable_match_after_vote(bracket)
        
        assert next_round == 0
        assert next_match == 1

    def test_get_or_create_user_tournament_existing(self, sample_tournament, sample_user_tournament, db_session):
        """Test getting existing user tournament"""
        result = TournamentService.get_or_create_user_tournament(
            sample_tournament.id, 
            sample_user_tournament.user_id
        )
        
        assert result.id == sample_user_tournament.id

    def test_get_or_create_user_tournament_new(self, sample_tournament, db_session):
        """Test creating new user tournament"""
        result = TournamentService.get_or_create_user_tournament(
            sample_tournament.id, 
            "completely_new_user"
        )
        
        assert result is not None
        assert result.user_id == "completely_new_user"
        assert result.tournament_id == sample_tournament.id
        assert result.completed is False