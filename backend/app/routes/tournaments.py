from flask import Blueprint, request, jsonify, session
from app.services.tournaments import TournamentService
from app.clients.open_router import OpenRouterClient
from app.schemas import (
    CreateTournamentRequest, VoteRequest, TournamentResponse,
    TournamentWithResultsResponse, TournamentListResponse,
    VoteResponse, ModelsResponse, ErrorResponse
)
from pydantic import ValidationError
import uuid
from functools import wraps

bp = Blueprint("tournaments", __name__)

def get_user_id():
    """Get user ID from session (for now) or Auth0 later"""
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())
    return session['user_id']

def validate_json(model_class):
    """Decorator to validate JSON request data with Pydantic"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                data = request.get_json(force=True)
                validated_data = model_class(**data)
                request.validated_data = validated_data
                return f(*args, **kwargs)
            except ValidationError as e:
                error_response = ErrorResponse(error=f"Validation error: {str(e)}")
                return jsonify(error_response.dict()), 400
            except Exception as e:
                error_response = ErrorResponse(error=f"Invalid JSON: {str(e)}")
                return jsonify(error_response.dict()), 400
        return decorated_function
    return decorator

def handle_service_errors(f):
    """Decorator to handle service layer errors consistently"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ValueError as e:
            error_response = ErrorResponse(error=str(e))
            return jsonify(error_response.dict()), 400
        except RuntimeError as e:
            error_response = ErrorResponse(error=str(e))
            return jsonify(error_response.dict()), 502
        except Exception as e:
            error_response = ErrorResponse(error='Unexpected error occurred.')
            return jsonify(error_response.dict()), 500
    return decorated_function

@bp.route('/models', methods=['GET', 'POST'])
@handle_service_errors
def handle_models():
    """Get available models or refresh cache"""
    client = OpenRouterClient()
    
    if request.method == 'POST':
        models = client.refresh_models_cache()
    else:
        models = client.get_available_models()
    
    response = ModelsResponse(models=models)
    return jsonify(response.dict()), 200

@bp.route('', methods=['GET', 'POST'])
def handle_tournaments():
    """List tournaments or create new tournament"""
    if request.method == 'GET':
        return _get_tournaments_list()
    else:
        return _create_tournament()

@handle_service_errors
def _get_tournaments_list():
    """Get tournaments list"""
    tournaments_data = TournamentService.get_tournaments_list()
    response = TournamentListResponse(tournaments=tournaments_data)
    return jsonify(response.dict())

@validate_json(CreateTournamentRequest)
@handle_service_errors
def _create_tournament():
    """Create tournament"""
    validated_data = request.validated_data
    
    tournament = TournamentService.create_tournament(
        validated_data.question, 
        [prompt.dict() for prompt in validated_data.prompts]
    )
    
    response_data = TournamentResponse(
        id=tournament.id,
        question=tournament.question,
        prompts=[p.text for p in tournament.prompts],
        responses=[p.response for p in tournament.prompts],
        models=[p.model for p in tournament.prompts],
        bracket_template=tournament.bracket_template,
        user_state={
            'completed': False,
            'winner_prompt_index': None,
            'next_match': (0, 0)
        }
    )
    
    return jsonify(response_data.dict()), 201

@bp.route('/<int:tournament_id>', methods=['GET'])
@handle_service_errors
def get_tournament(tournament_id):
    """Get tournament details with optional results"""
    include_results = request.args.get('include_results', 'false').lower() == 'true'
    user_id = get_user_id()
    
    tournament, user_tournament, user_bracket = TournamentService.get_tournament_with_user_state(
        tournament_id, user_id
    )
    
    base_data = {
        'id': tournament.id,
        'question': tournament.question,
        'prompts': [p.text for p in tournament.prompts],
        'responses': [p.response for p in tournament.prompts],
        'models': [p.model for p in tournament.prompts],
        'bracket_template': tournament.bracket_template,
        'user_bracket': user_bracket,
        'user_state': {
            'completed': user_tournament.completed if user_tournament else False,
            'winner_prompt_index': user_tournament.winner_prompt_index if user_tournament else None,
            'next_match': user_tournament.get_next_votable_match() if user_tournament and user_tournament.current_bracket else None
        }
    }
    
    if include_results:
        rankings = TournamentService.get_prompt_rankings(tournament_id)
        stats = TournamentService.get_participation_stats(tournament_id)
        response = TournamentWithResultsResponse(
            **base_data,
            rankings=rankings,
            stats=stats
        )
    else:
        response = TournamentResponse(**base_data)
    
    return jsonify(response.dict())

@bp.route('/<int:tournament_id>/vote', methods=['POST'])
@validate_json(VoteRequest)
@handle_service_errors
def vote(tournament_id):
    """Submit vote"""
    user_id = get_user_id()
    validated_data = request.validated_data
    
    tournament, _, _ = TournamentService.get_tournament_with_user_state(tournament_id, user_id)
    
    user_bracket, completed, winner_prompt_index = TournamentService.record_vote(
        tournament, user_id, validated_data.round, 
        validated_data.match, validated_data.winner
    )
    
    response = VoteResponse(
        user_bracket=user_bracket,
        completed=completed,
        winner_prompt_index=winner_prompt_index,
        user_id=user_id
    )
    
    return jsonify(response.dict())
