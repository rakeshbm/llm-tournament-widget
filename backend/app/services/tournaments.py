import json
from app.models import Tournament, Vote
from app import db
from app.utils import create_bracket, generate_llm_response

class TournamentService:
    @staticmethod
    def create_tournament(question, prompts):
        responses = [generate_llm_response(prompt, question) for prompt in prompts]
        bracket = create_bracket(prompts)

        tournament = Tournament(
            question=question,
            prompts=json.dumps(prompts),
            responses=json.dumps(responses),
            bracket=json.dumps(bracket),
            completed=False,
            winner_prompt=None,
        )
        db.session.add(tournament)
        db.session.commit()
        return tournament

    @staticmethod
    def vote(tournament, round_number, match_number, winner_index):
        bracket = json.loads(tournament.bracket)

        if round_number >= len(bracket):
            raise ValueError("Invalid round number")
        if match_number >= len(bracket[round_number]):
            raise ValueError("Invalid match number")
        
        # check winner_index validity in participants
        match = bracket[round_number][match_number]
        participants = []
        if 'participant1' in match:
            participants.append(match['participant1'])
        if 'participant2' in match:
            participants.append(match['participant2'])

        if winner_index not in participants:
            raise ValueError("Winner index must be one of the participants")

        # Save vote record
        vote_record = Vote(
            tournament_id=tournament.id,
            round_number=round_number,
            match_number=match_number,
            winner_index=winner_index
        )
        db.session.add(vote_record)

        # Update bracket winner for this match
        bracket[round_number][match_number]['winner'] = winner_index
        
        # Advance winner to next round if not final
        if round_number < len(bracket) - 1:
            next_round = round_number + 1
            next_match = match_number // 2
            
            if match_number % 2 == 0:
                bracket[next_round][next_match]['participant1'] = winner_index
            else:
                bracket[next_round][next_match]['participant2'] = winner_index
        else:
            # Final round: tournament completed
            prompts = json.loads(tournament.prompts)
            tournament.winner_prompt = prompts[winner_index] if winner_index < len(prompts) else None
            tournament.completed = True
        
        tournament.bracket = json.dumps(bracket)
        db.session.commit()

        return bracket, tournament.completed, tournament.winner_prompt
