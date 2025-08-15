import copy
from datetime import datetime
from app.models import Tournament, TournamentPrompt, UserTournament, Vote
from app import db
from app.utils import create_bracket
from sqlalchemy import func, case, and_
from sqlalchemy.orm import selectinload
from sqlalchemy.orm.attributes import flag_modified
from app.clients.open_router import OpenRouterClient

client = OpenRouterClient()

class TournamentService:
    @staticmethod
    def create_tournament(question, prompt_data_list):
        """Create a new tournament with LLM responses"""        
        # Generate responses
        responses = client.generate_completions(prompt_data_list, question)
        if any(response is None or response.strip() == "" for response in responses):
            raise RuntimeError("Failed to generate one or more LLM responses. Tournament not created.")
        
        bracket_template = create_bracket(prompt_data_list)

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
                text=prompt_data['text'],
                model=prompt_data['model'],
                response=response
            ) for i, (prompt_data, response) in enumerate(zip(prompt_data_list, responses))
        ]
        db.session.bulk_save_objects(tournament_prompts)
        db.session.commit()
        
        return Tournament.query.options(selectinload(Tournament.prompts)).get(tournament.id)
    
    @staticmethod
    def get_tournament_with_user_state(tournament_id, user_id):
        """Get tournament with user state"""
        tournament = Tournament.query.options(
            selectinload(Tournament.prompts)
        ).get_or_404(tournament_id)
        
        # Get user tournament
        user_tournament = UserTournament.query.filter(
            and_(
                UserTournament.tournament_id == tournament_id,
                UserTournament.user_id == user_id
            )
        ).first()
        
        # Get user bracket or create new one
        if user_tournament and user_tournament.current_bracket:
            user_bracket = user_tournament.current_bracket
        else:
            user_bracket = copy.deepcopy(tournament.bracket_template)
        
        return tournament, user_tournament, user_bracket

    @staticmethod
    def _validate_vote(user_bracket, round_number, match_number, winner_index):
        """Vote validation logic"""
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
        # Get user tournament
        user_tournament = UserTournament.query.filter(
            and_(
                UserTournament.tournament_id == tournament.id,
                UserTournament.user_id == user_id
            )
        ).first()
        
        if not user_tournament:
            user_tournament = UserTournament(
                tournament_id=tournament.id,
                user_id=user_id,
                current_bracket=copy.deepcopy(tournament.bracket_template),
                completed=False
            )
            db.session.add(user_tournament)
            db.session.flush()
        
        if not user_tournament.current_bracket:
            user_tournament.current_bracket = copy.deepcopy(tournament.bracket_template)
        
        user_bracket = copy.deepcopy(user_tournament.current_bracket)
        
        # Validate vote
        TournamentService._validate_vote(user_bracket, round_number, match_number, winner_index)
        
        # Check for existing vote
        existing_vote = Vote.query.filter(
            and_(
                Vote.user_tournament_id == user_tournament.id,
                Vote.round_number == round_number,
                Vote.match_number == match_number
            )
        ).first()
        
        if existing_vote:
            raise ValueError("User has already voted for this match")
        
        # Create vote record
        vote_record = Vote(
            user_tournament_id=user_tournament.id,
            round_number=round_number,
            match_number=match_number,
            winner_index=winner_index
        )
        db.session.add(vote_record)
        
        # Update bracket state
        current_match = user_bracket[round_number][match_number]
        current_match['winner'] = winner_index
        
        # Advance winner to next round
        TournamentService._advance_winner_in_bracket(
            user_bracket, round_number, match_number, winner_index
        )
        
        user_tournament.current_bracket = user_bracket
        flag_modified(user_tournament, 'current_bracket')
        
        # Check if this completes the tournament
        is_final_round = round_number == len(user_bracket) - 1
        if is_final_round:
            user_tournament.completed = True
            user_tournament.completed_at = datetime.utcnow()
            user_tournament.winner_prompt_index = winner_index
        
        db.session.commit()
        
        return user_bracket, user_tournament.completed, user_tournament.winner_prompt_index

    @staticmethod
    def _advance_winner_in_bracket(bracket, round_number, match_number, winner_index):
        """Advance winner to next round in bracket"""
        if round_number >= len(bracket) - 1:
            return
        
        next_round = round_number + 1
        next_match = match_number // 2
        
        if next_round < len(bracket) and next_match < len(bracket[next_round]):
            if match_number % 2 == 0:
                bracket[next_round][next_match]['participant1'] = winner_index
            else:
                bracket[next_round][next_match]['participant2'] = winner_index

    @staticmethod
    def get_prompt_rankings(tournament_id):
        """Get prompt performance rankings"""
        results = db.session.query(
            TournamentPrompt.position,
            TournamentPrompt.text,
            TournamentPrompt.model,
            func.count(UserTournament.id).filter(UserTournament.completed == True).label('completed_participants'),
            func.count(UserTournament.id).filter(
                and_(
                    UserTournament.completed == True,
                    UserTournament.winner_prompt_index == TournamentPrompt.position
                )
            ).label('win_count')
        ).select_from(TournamentPrompt).outerjoin(
            UserTournament, 
            UserTournament.tournament_id == TournamentPrompt.tournament_id
        ).filter(
            TournamentPrompt.tournament_id == tournament_id
        ).group_by(
            TournamentPrompt.position, TournamentPrompt.text, TournamentPrompt.model
        ).order_by(TournamentPrompt.position).all()
        
        # Calculate percentages
        formatted_results = []
        for result in results:
            win_percentage = (result.win_count / result.completed_participants * 100) if result.completed_participants > 0 else 0.0
            formatted_results.append({
                'prompt': result.text,
                'prompt_index': result.position,
                'model': result.model,
                'win_count': result.win_count,
                'win_percentage': round(win_percentage, 2)
            })
        
        # Sort by win count, then by win percentage
        return sorted(formatted_results, key=lambda x: (x['win_count'], x['win_percentage']), reverse=True)

    @staticmethod
    def get_participation_stats(tournament_id):
        """Get tournament participation statistics"""
        stats = db.session.query(
            func.count(UserTournament.id).label('total_participants'),
            func.sum(case((UserTournament.completed == True, 1), else_=0)).label('completed_participants')
        ).filter(UserTournament.tournament_id == tournament_id).first()
        
        total = stats.total_participants or 0
        completed = int(stats.completed_participants or 0)
        
        return {
            'total_participants': total,
            'completed_participants': completed,
            'completion_rate': round((completed / total * 100), 2) if total > 0 else 0
        }

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
        ).select_from(Tournament).outerjoin(
            UserTournament, UserTournament.tournament_id == Tournament.id
        ).outerjoin(
            TournamentPrompt, TournamentPrompt.tournament_id == Tournament.id
        ).group_by(
            Tournament.id, Tournament.question, Tournament.created_at
        ).order_by(Tournament.created_at.desc()).all()
        
        tournaments = []
        for tournament in results:
            total_participants = tournament.total_participants or 0
            completed_participants = int(tournament.completed_participants or 0)
            
            tournaments.append({
                'id': tournament.id,
                'question': tournament.question[:100] + '...' if len(tournament.question) > 100 else tournament.question,
                'num_prompts': tournament.num_prompts or 0,
                'created_at': tournament.created_at.isoformat(),
                'total_participants': total_participants,
                'completed_participants': completed_participants,
                'completion_rate': round((completed_participants / total_participants * 100), 2) 
                                 if total_participants > 0 else 0
            })
        
        return tournaments
