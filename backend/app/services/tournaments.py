import copy
from datetime import datetime
from app.models import Tournament, TournamentPrompt, UserTournament, Vote
from app import db
from app.utils import create_bracket, generate_llm_response
from sqlalchemy import func, case
from sqlalchemy.orm import joinedload, selectinload

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
            bracket_template=bracket_template
        )
        db.session.add(tournament)
        db.session.flush()
        
        # Create prompt records
        tournament_prompts = [
            TournamentPrompt(
                tournament_id=tournament.id,
                position=i,
                text=prompt,
                response=response
            ) for i, (prompt, response) in enumerate(zip(prompts, responses))
        ]
        db.session.bulk_save_objects(tournament_prompts)
        db.session.commit()
        return tournament
    
    @staticmethod
    def get_tournament_with_user_state(tournament_id, user_id):
        """Get tournament with user state"""
        tournament = Tournament.query.options(
            selectinload(Tournament.user_tournaments.and_(
                UserTournament.user_id == user_id
            )).selectinload(UserTournament.votes),
            selectinload(Tournament.prompts)
        ).get_or_404(tournament_id)
        
        user_tournament = next(
            (ut for ut in tournament.user_tournaments if ut.user_id == user_id), 
            None
        )
        
        # Build user bracket state
        if user_tournament and user_tournament.votes:
            user_bracket = TournamentService._build_user_bracket(
                tournament.bracket_template, user_tournament.votes
            )
        else:
            user_bracket = copy.deepcopy(tournament.bracket_template)
        
        return tournament, user_tournament, user_bracket
    
    @staticmethod
    def _build_user_bracket(bracket_template, user_votes):
        """Build user-specific bracket"""
        if not user_votes:
            return copy.deepcopy(bracket_template)
        
        user_bracket = copy.deepcopy(bracket_template)
        
        sorted_votes = sorted(user_votes, key=lambda v: (v.round_number, v.match_number))
        
        # Apply votes in order
        for vote in sorted_votes:
            if (vote.round_number < len(user_bracket) and 
                vote.match_number < len(user_bracket[vote.round_number])):
                
                # Apply vote
                match = user_bracket[vote.round_number][vote.match_number]
                if match.get('winner') is None:
                    match['winner'] = vote.winner_index
                    TournamentService._advance_winner_in_bracket(
                        user_bracket, vote.round_number, vote.match_number, vote.winner_index
                    )
        
        return user_bracket

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
    def validate_vote(user_bracket, round_number, match_number, winner_index, existing_votes):
        """Vote validation logic"""
        # Check for existing vote
        existing_vote_keys = {(vote.round_number, vote.match_number) for vote in existing_votes}
        if (round_number, match_number) in existing_vote_keys:
            raise ValueError("User has already voted for this match")
        
        # Validate round and match numbers
        if round_number >= len(user_bracket):
            raise ValueError("Invalid round number")
        if match_number >= len(user_bracket[round_number]):
            raise ValueError("Invalid match number")
        
        # Validate match state and participants
        current_match = user_bracket[round_number][match_number]
        p1 = current_match.get('participant1')
        p2 = current_match.get('participant2')
        
        # Check if match is ready
        if p1 is None or p1 == -1 or p2 is None or p2 == -1:
            raise ValueError("This match is not ready for voting yet")
        
        if current_match.get('winner') is not None:
            raise ValueError("This match has already been decided")
        
        # Validate winner
        participants = [p1, p2]
        if winner_index not in participants:
            raise ValueError(f"Winner index {winner_index} must be one of the participants {participants}")

    @staticmethod
    def record_vote(tournament, user_id, round_number, match_number, winner_index):
        """Record a vote and update user tournament state"""
        user_tournament = UserTournament.query.options(
            joinedload(UserTournament.votes)
        ).filter_by(
            tournament_id=tournament.id,
            user_id=user_id
        ).first()
        
        if not user_tournament:
            user_tournament = UserTournament(
                tournament_id=tournament.id,
                user_id=user_id,
                current_round=0,
                current_match=0,
                completed=False
            )
            db.session.add(user_tournament)
            db.session.flush()
            user_tournament.votes = []
        
        # Validate vote using current bracket state
        user_bracket = TournamentService._build_user_bracket(
            tournament.bracket_template, user_tournament.votes
        )
        
        TournamentService.validate_vote(
            user_bracket, round_number, match_number, winner_index, user_tournament.votes
        )
        
        # Create vote record
        vote_record = Vote(
            user_tournament_id=user_tournament.id,
            round_number=round_number,
            match_number=match_number,
            winner_index=winner_index
        )
        db.session.add(vote_record)
        user_tournament.votes.append(vote_record)
        
        # Update bracket with new vote (incremental)
        user_bracket[round_number][match_number]['winner'] = winner_index
        TournamentService._advance_winner_in_bracket(
            user_bracket, round_number, match_number, winner_index
        )
        
        # Check if this completes the tournament
        is_final_round = round_number == len(user_bracket) - 1
        tournament_completed = False
        if is_final_round:
            user_tournament.completed = True
            user_tournament.completed_at = datetime.utcnow()
            user_tournament.winner_prompt_index = winner_index
            tournament_completed = True
        else:
            # Find next match
            next_round, next_match = TournamentService._find_next_votable_match_after_vote(user_bracket)
            user_tournament.current_round = next_round if next_round is not None else round_number
            user_tournament.current_match = next_match if next_match is not None else match_number
        
        db.session.commit()
        
        return user_bracket, user_tournament.completed, user_tournament.winner_prompt_index

    @staticmethod
    def _find_next_votable_match_after_vote(user_bracket):
        """Find next votable match"""
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
    def get_tournament_results(tournament_id):
        """Get aggregated results - race condition and N+1 safe"""
        # Single atomic query gets all data
        results = db.session.query(
            TournamentPrompt.position,
            TournamentPrompt.text,
            func.count(UserTournament.id).filter(UserTournament.completed == True).label('total_participants'),
            func.count(UserTournament.id).filter(
                UserTournament.completed == True,
                UserTournament.winner_prompt_index == TournamentPrompt.position
            ).label('win_count')
        ).outerjoin(
            UserTournament, UserTournament.tournament_id == TournamentPrompt.tournament_id
        ).filter(
            TournamentPrompt.tournament_id == tournament_id
        ).group_by(
            TournamentPrompt.position, TournamentPrompt.text
        ).order_by(TournamentPrompt.position).all()
        
        # Calculate percentages from consistent data
        formatted_results = []
        for result in results:
            win_percentage = (result.win_count / result.total_participants * 100) if result.total_participants > 0 else 0.0
            formatted_results.append({
                'prompt': result.text,
                'prompt_index': result.position,
                'win_count': result.win_count,
                'total_participants': result.total_participants,
                'win_percentage': round(win_percentage, 2)
            })
        
        # Sort by win count, then by win percentage
        return sorted(formatted_results, key=lambda x: (x['win_count'], x['win_percentage']), reverse=True)

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
            'completion_rate': round((completed / total * 100), 2) if total > 0 else 0
        }

    @staticmethod
    def get_tournament_participants(tournament_id):
        """Get list of participants and their status"""
        participants = UserTournament.query.filter_by(tournament_id=tournament_id).all()
        
        return [
            {
                'user_id': participant.user_id[:8] + '...',
                'completed': participant.completed,
                'current_round': participant.current_round,
                'current_match': participant.current_match,
                'started_at': participant.started_at.isoformat(),
                'completed_at': participant.completed_at.isoformat() if participant.completed_at else None
            } for participant in participants
        ]

    # TODO: Optimize read performance
    @staticmethod
    def get_tournaments_list():
        """Get list of all tournaments"""
        results = db.session.query(
            Tournament.id,
            Tournament.question,
            Tournament.created_at,
            func.count(func.distinct(UserTournament.id)).label('total_participants'),
            func.count(func.distinct(case((UserTournament.completed == True, UserTournament.id)))).label('completed_participants'),
            func.count(func.distinct(TournamentPrompt.id)).label('num_prompts')
        ).outerjoin(UserTournament).outerjoin(TournamentPrompt).group_by(
            Tournament.id, Tournament.question, Tournament.created_at
        ).order_by(Tournament.created_at.desc()).all()
        
        return [{
            'id': tournament.id,
            'question': tournament.question[:100] + '...' if len(tournament.question) > 100 else tournament.question,
            'num_prompts': tournament.num_prompts or 0,
            'created_at': tournament.created_at.isoformat(),
            'total_participants': tournament.total_participants or 0,
            'completed_participants': tournament.completed_participants or 0,
            'completion_rate': round((tournament.completed_participants / tournament.total_participants * 100), 2) 
                             if tournament.total_participants > 0 else 0
        } for tournament in results]