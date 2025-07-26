from flask import Blueprint, request, jsonify
from app.models import Tournament, Prompt, Vote
from app import db

bp = Blueprint("tournaments", __name__)

@bp.route("/", methods=["POST"])
def create_tournament():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    name = data.get("name")
    input_question = data.get("input_question")
    prompts = data.get("prompts")

    if not isinstance(name, str) or not name.strip():
        return jsonify({"error": "Name must be a non-empty string"}), 400

    if not isinstance(input_question, str) or not input_question.strip():
        return jsonify({"error": "Input question must be a non-empty string"}), 400

    if not isinstance(prompts, list) or not all(isinstance(p, str) and p.strip() for p in prompts):
        return jsonify({"error": "Prompts must be a list of non-empty strings"}), 400

    if len(prompts) < 2:
        return jsonify({"error": "At least 2 prompts are required"}), 400

    tournament = Tournament(name=name.strip(), input_question=input_question.strip())
    db.session.add(tournament)
    db.session.commit()

    for prompt_text in prompts:
        prompt = Prompt(text=prompt_text.strip(), tournament_id=tournament.id)
        db.session.add(prompt)
    db.session.commit()

    return jsonify({"id": tournament.id}), 201

@bp.route("/<int:tournament_id>/vote", methods=["POST"])
def vote(tournament_id):
    data = request.get_json()

    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    prompt_id = data.get("prompt_id")

    if not isinstance(prompt_id, int):
        return jsonify({"error": "prompt_id must be an integer"}), 400

    prompt = Prompt.query.filter_by(id=prompt_id, tournament_id=tournament_id).first()
    if not prompt:
        return jsonify({"error": "Prompt not found in this tournament"}), 404

    vote = Vote(prompt_id=prompt.id)
    db.session.add(vote)
    db.session.commit()

    return jsonify({"message": "Vote recorded."}), 200
