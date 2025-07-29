import json
from flask import Blueprint, request, jsonify
from app.models import Tournament
from app.services.tournaments import TournamentService

bp = Blueprint("tournaments", __name__)

@bp.route('', methods=['POST'])
def create_tournament():
    data = request.json
    question = data.get('question')
    prompts = data.get('prompts', [])
    
    if not question or len(prompts) < 2:
        return jsonify({'error': 'Need at least 2 prompts and a question'}), 400

    try:
        tournament = TournamentService.create_tournament(question, prompts)
    except RuntimeError as e:
        return jsonify({'error': str(e)}), 502
    except Exception as e:
        return jsonify({'error': 'Unexpected error occurred.'}), 500

    return jsonify({
        'id': tournament.id,
        'question': tournament.question,
        'prompts': json.loads(tournament.prompts),
        'responses': json.loads(tournament.responses),
        'bracket': json.loads(tournament.bracket)
    }), 201

@bp.route('/<int:tournament_id>', methods=['GET'])
def get_tournament(tournament_id):
    tournament = Tournament.query.get_or_404(tournament_id)
    return jsonify({
        'id': tournament.id,
        'question': tournament.question,
        'prompts': json.loads(tournament.prompts),
        'responses': json.loads(tournament.responses),
        'bracket': json.loads(tournament.bracket),
        'winner_prompt': tournament.winner_prompt,
        'completed': tournament.completed
    })

@bp.route('/<int:tournament_id>/vote', methods=['POST'])
def vote(tournament_id):
    tournament = Tournament.query.get_or_404(tournament_id)
    data = request.json or {}

    round_number = data.get('round')
    match_number = data.get('match')
    winner_index = data.get('winner')

    if round_number is None or match_number is None or winner_index is None:
        return jsonify({"error": "Missing round, match or winner fields"}), 400

    try:
        bracket, completed, winner_prompt = TournamentService.vote(tournament, round_number, match_number, winner_index)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    return jsonify({
        'bracket': bracket,
        'completed': completed,
        'winner_prompt': winner_prompt
    })

@bp.route('', methods=['GET'])
def get_tournaments():
    tournaments = Tournament.query.order_by(Tournament.created_at.desc()).all()
    
    result = []
    for t in tournaments:
        result.append({
            'id': t.id,
            'question': t.question[:100] + '...' if len(t.question) > 100 else t.question,
            'num_prompts': len(json.loads(t.prompts)),
            'completed': t.completed,
            'created_at': t.created_at.isoformat()
        })
    
    return jsonify(result)
