import json
from datetime import datetime
from app.models import Tournament, UserTournament, Vote, PromptResult
from app import db
from app.utils import create_bracket, generate_llm_response
from sqlalchemy import func

class TournamentService:
    @staticmethod
    def create_tournament(question, prompts):
        """Create a new tournament with LLM responses"""
        responses = [generate_llm_response(prompt, question) for prompt in prompts]
        if any(response is None or response.strip() == "" for response in responses):
            raise RuntimeError("Failed to generate one or more LLM responses. Tournament not created.")
        
        bracket_template = create_bracket(prompts)

        tournament = Tournament(
            question=question,
            prompts=json.dumps(prompts),
            responses=json.dumps(responses),
            bracket_template=json.dumps(bracket_template)
        )
        db.session.add(tournament)
        db.session.flush()
        
        # Initialize prompt results
        prompt_results = [
            PromptResult(
                tournament_id=tournament.id,
                prompt_index=i,
                win_count=0,
                total_participants=0,
                win_percentage=0.0
            ) for i in range(len(prompts))
        ]
        db.session.add_all(prompt_results)
        db.session.commit()
        return tournament
    
    @staticmethod
    def get_tournament_with_user_state(tournament_id, user_id):
        """Get tournament with user state in a single optimized query"""
        tournament = Tournament.query.get_or_404(tournament_id)
        
        # Get user tournament and votes
        user_tournament = UserTournament.query.filter_by(
            tournament_id=tournament_id,
            user_id=user_id
        ).first()
        
        user_votes = []
        if user_tournament:
            user_votes = Vote.query.filter_by(
                tournament_id=tournament_id,
                user_id=user_id
            ).all()
        
        # Build user bracket state
        bracket_template = json.loads(tournament.bracket_template)
        user_bracket = TournamentService._build_user_bracket(bracket_template, user_votes)
        
        return tournament, user_tournament, user_bracket
    
    @staticmethod
    def _build_user_bracket(bracket_template, user_votes):
        """Build user-specific bracket by applying votes"""
        user_bracket = json.loads(json.dumps(bracket_template))
        
        # Apply user's votes to bracket and advance winners
        for vote in user_votes:
            if (vote.round_number < len(user_bracket) and 
                vote.match_number < len(user_bracket[vote.round_number])):
                user_bracket[vote.round_number][vote.match_number]['winner'] = vote.winner_index
                
                # Advance winner to next round
                TournamentService._advance_winner_in_bracket(
                    user_bracket, vote.round_number, vote.match_number, vote.winner_index
                )
        
        return user_bracket
    
    @staticmethod
    def get_or_create_user_tournament(tournament_id, user_id):
        """Get existing user tournament or create new one"""
        user_tournament = UserTournament.query.filter_by(
            tournament_id=tournament_id,
            user_id=user_id
        ).first()
        
        if not user_tournament:
            user_tournament = UserTournament(
                tournament_id=tournament_id,
                user_id=user_id,
                current_round=0,
                current_match=0,
                completed=False
            )
            db.session.add(user_tournament)
            db.session.flush()
        
        return user_tournament

    @staticmethod
    def _advance_winner_in_bracket(bracket, round_number, match_number, winner_index):
        """Advance winner to next round in bracket"""
        if round_number < len(bracket) - 1:
            next_round = round_number + 1
            next_match = match_number // 2
            
            if match_number % 2 == 0:
                bracket[next_round][next_match]['participant1'] = winner_index
            else:
                bracket[next_round][next_match]['participant2'] = winner_index

    @staticmethod
    def validate_vote(tournament, user_id, round_number, match_number, winner_index):
        """Validate vote parameters and check for existing votes"""
        # Check if user already voted for this match
        existing_vote = Vote.query.filter_by(
            tournament_id=tournament.id,
            user_id=user_id,
            round_number=round_number,
            match_number=match_number
        ).first()
        
        if existing_vote:
            raise ValueError("User has already voted for this match")
        
        # Get user's current bracket state for validation
        user_votes = Vote.query.filter_by(
            tournament_id=tournament.id,
            user_id=user_id
        ).all()
        
        bracket_template = json.loads(tournament.bracket_template)
        user_bracket = TournamentService._build_user_bracket(bracket_template, user_votes)
        
        # Validate round and match numbers
        if round_number >= len(user_bracket):
            raise ValueError("Invalid round number")
        if match_number >= len(user_bracket[round_number]):
            raise ValueError("Invalid match number")
        
        # Validate match state and participants
        current_match = user_bracket[round_number][match_number]
        participants = []
        if current_match.get('participant1') is not None and current_match.get('participant1') != -1:
            participants.append(current_match['participant1'])
        if current_match.get('participant2') is not None and current_match.get('participant2') != -1:
            participants.append(current_match['participant2'])
        
        if winner_index not in participants:
            raise ValueError(f"Winner index {winner_index} must be one of the participants {participants}")
        
        # Validate that this match is ready for voting
        if (current_match.get('participant1') is None or current_match.get('participant1') == -1 or
            current_match.get('participant2') is None or current_match.get('participant2') == -1):
            raise ValueError("This match is not ready for voting yet")
        
        if current_match.get('winner') is not None:
            raise ValueError("This match has already been decided")
        
        return user_bracket

    @staticmethod
    def record_vote(tournament, user_id, round_number, match_number, winner_index):
        """Record a vote and update user tournament state"""
        # Validate vote first
        user_bracket = TournamentService.validate_vote(
            tournament, user_id, round_number, match_number, winner_index
        )
        
        # Get or create user tournament
        user_tournament = TournamentService.get_or_create_user_tournament(tournament.id, user_id)
        
        # Create vote record
        vote_record = Vote(
            tournament_id=tournament.id,
            user_id=user_id,
            round_number=round_number,
            match_number=match_number,
            winner_index=winner_index
        )
        db.session.add(vote_record)
        
        # Check if this completes the tournament
        is_final_round = round_number == len(user_bracket) - 1
        if is_final_round:
            user_tournament.completed = True
            user_tournament.completed_at = datetime.utcnow()
            user_tournament.winner_prompt_index = winner_index
            
            # Update prompt results
            TournamentService._update_prompt_results(tournament.id, winner_index)
        else:
            # Update current position
            next_round, next_match = TournamentService._find_next_votable_match_after_vote(
                user_bracket, round_number, match_number, winner_index
            )
            user_tournament.current_round = next_round if next_round is not None else round_number
            user_tournament.current_match = next_match if next_match is not None else match_number
        
        db.session.commit()
        
        # Return updated state
        updated_user_bracket = TournamentService._build_user_bracket(
            json.loads(tournament.bracket_template), 
            Vote.query.filter_by(tournament_id=tournament.id, user_id=user_id).all()
        )
        
        return updated_user_bracket, user_tournament.completed, user_tournament.winner_prompt_index

    @staticmethod
    def _find_next_votable_match_after_vote(user_bracket, voted_round, voted_match, winner_index):
        """Find next votable match after applying a vote"""
        # Apply the new vote to the bracket
        user_bracket[voted_round][voted_match]['winner'] = winner_index
        TournamentService._advance_winner_in_bracket(
            user_bracket, voted_round, voted_match, winner_index
        )
        
        # Find next votable match
        for round_num, round_matches in enumerate(user_bracket):
            for match_num, match in enumerate(round_matches):
                p1 = match.get('participant1')
                p2 = match.get('participant2')
                
                if (p1 is not None and p1 != -1 and 
                    p2 is not None and p2 != -1 and
                    match.get('winner') is None):
                    return round_num, match_num
        
        return None, None

    @staticmethod
    def _update_prompt_results(tournament_id, winning_prompt_index):
        """Update aggregated results when a user completes a tournament"""
        # Increment win count for winning prompt
        prompt_result = PromptResult.query.filter_by(
            tournament_id=tournament_id,
            prompt_index=winning_prompt_index
        ).first()
        
        if prompt_result:
            prompt_result.win_count += 1
        
        # Update totals and percentages for all prompts
        total_completed = UserTournament.query.filter_by(
            tournament_id=tournament_id,
            completed=True
        ).count()
        
        # Bulk update all prompt results
        PromptResult.query.filter_by(tournament_id=tournament_id).update({
            'total_participants': total_completed,
            'win_percentage': func.round((PromptResult.win_count / total_completed * 100), 2) if total_completed > 0 else 0
        }, synchronize_session=False)

    @staticmethod
    def get_tournament_results(tournament_id):
        """Get aggregated results for a tournament"""
        tournament = Tournament.query.get_or_404(tournament_id)
        prompts = json.loads(tournament.prompts)
        
        results = PromptResult.query.filter_by(tournament_id=tournament_id).order_by(
            PromptResult.win_count.desc(),
            PromptResult.win_percentage.desc()
        ).all()
        
        return [
            {
                'prompt': prompts[result.prompt_index],
                'prompt_index': result.prompt_index,
                'win_count': result.win_count,
                'total_participants': result.total_participants,
                'win_percentage': result.win_percentage
            } for result in results
        ]

    @staticmethod
    def get_tournament_stats(tournament_id):
        """Get general statistics for a tournament"""
        stats = db.session.query(
            func.count(UserTournament.id).label('total_participants'),
            func.count(UserTournament.id).filter(UserTournament.completed == True).label('completed_participants')
        ).filter(UserTournament.tournament_id == tournament_id).first()
        
        total = stats.total_participants or 0
        completed = stats.completed_participants or 0
        
        return {
            'total_participants': total,
            'completed_participants': completed,
            'completion_rate': (completed / total * 100) if total > 0 else 0
        }

    @staticmethod
    def get_tournament_participants(tournament_id):
        """Get list of participants and their status"""
        participants = UserTournament.query.filter_by(tournament_id=tournament_id).all()
        
        return [
            {
                'user_id': participant.user_id[:8] + '...',  # Truncated for privacy
                'completed': participant.completed,
                'current_round': participant.current_round,
                'current_match': participant.current_match,
                'started_at': participant.started_at.isoformat(),
                'completed_at': participant.completed_at.isoformat() if participant.completed_at else None
            } for participant in participants
        ]

    @staticmethod
    def get_tournaments_list():
        """Get list of all tournaments with summary info"""
        tournaments = Tournament.query.order_by(Tournament.created_at.desc()).all()
        
        result = []
        for tournament in tournaments:
            stats = TournamentService.get_tournament_stats(tournament.id)
            prompts = json.loads(tournament.prompts)
            
            result.append({
                'id': tournament.id,
                'question': tournament.question[:100] + '...' if len(tournament.question) > 100 else tournament.question,
                'num_prompts': len(prompts),
                'created_at': tournament.created_at.isoformat(),
                'total_participants': stats['total_participants'],
                'completed_participants': stats['completed_participants'],
                'completion_rate': stats['completion_rate']
            })
        
        return result