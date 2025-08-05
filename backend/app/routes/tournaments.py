from flask import Blueprint, request, jsonify, session
from app.services.tournaments import TournamentService
import uuid

bp = Blueprint("tournaments", __name__)

def get_user_id():
    """Get user ID from session (for now) or Auth0 later"""
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())  # Generate unique session-based user ID
    return session['user_id']

@bp.route('', methods=['POST'])
def create_tournament():
    """Create a new tournament"""
    data = request.json or {}
    question = data.get('question')
    prompts = data.get('prompts', [])
    
    if not question or len(prompts) < 2:
        return jsonify({'error': 'Need at least 2 prompts and a question'}), 400

    try:
        tournament = TournamentService.create_tournament(question, prompts)
        
        prompts_data = [p.text for p in tournament.prompts]
        responses_data = [p.response for p in tournament.prompts]
        
        return jsonify({
            'id': tournament.id,
            'question': tournament.question,
            'prompts': prompts_data,
            'responses': responses_data,
            'bracket_template': tournament.bracket_template
        }), 201
    except RuntimeError as e:
        return jsonify({'error': str(e)}), 502
    except Exception as e:
        return jsonify({'error': 'Unexpected error occurred.'}), 500

@bp.route('/<int:tournament_id>', methods=['GET'])
def get_tournament(tournament_id):
    """Get tournament details and user-specific state"""
    try:
        user_id = get_user_id()
        tournament, user_tournament, user_bracket = TournamentService.get_tournament_with_user_state(
            tournament_id, user_id
        )
        
        # Format user state
        if not user_tournament:
            user_state = {
                'current_round': 0,
                'current_match': 0,
                'completed': False,
                'winner_prompt_index': None
            }
        else:
            user_state = {
                'current_round': user_tournament.current_round,
                'current_match': user_tournament.current_match,
                'completed': user_tournament.completed,
                'winner_prompt_index': user_tournament.winner_prompt_index
            }
        
        # Build prompts and responses from TournamentPrompt records
        prompts_data = [p.text for p in tournament.prompts]
        responses_data = [p.response for p in tournament.prompts]
        
        return jsonify({
            'id': tournament.id,
            'question': tournament.question,
            'prompts': prompts_data,
            'responses': responses_data,
            'bracket_template': tournament.bracket_template,
            'user_bracket': user_bracket,
            'user_state': user_state
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/<int:tournament_id>/vote', methods=['POST'])
def vote(tournament_id):
    """Submit a vote for the current user"""
    try:
        user_id = get_user_id()
        data = request.json or {}

        round_number = data.get('round')
        match_number = data.get('match')
        winner_index = data.get('winner')

        if round_number is None or match_number is None or winner_index is None:
            return jsonify({"error": "Missing round, match or winner fields"}), 400

        # Get tournament first
        tournament, _, _ = TournamentService.get_tournament_with_user_state(tournament_id, user_id)
        
        user_bracket, completed, winner_prompt_index = TournamentService.record_vote(
            tournament, user_id, round_number, match_number, winner_index
        )
        
        return jsonify({
            'user_bracket': user_bracket,
            'completed': completed,
            'winner_prompt_index': winner_prompt_index,
            'user_id': user_id
        })
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Unexpected error occurred"}), 500

@bp.route('/<int:tournament_id>/results', methods=['GET'])
def get_tournament_results(tournament_id):
    """Get aggregated results for a tournament"""
    try:
        results = TournamentService.get_tournament_results(tournament_id)
        stats = TournamentService.get_tournament_stats(tournament_id)
        
        return jsonify({
            'results': results,
            'stats': stats
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('', methods=['GET'])
def get_tournaments():
    """Get list of all tournaments with summary info"""
    try:
        tournaments = TournamentService.get_tournaments_list()
        return jsonify(tournaments)
    except Exception as e:
        return jsonify({'error': str(e)}), 500