from datetime import datetime
from app import db
from sqlalchemy import UniqueConstraint, Index

class Tournament(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.Text, nullable=False)
    prompts = db.Column(db.Text, nullable=False)  # JSON array of prompts
    responses = db.Column(db.Text)  # JSON array of LLM responses
    bracket_template = db.Column(db.Text)  # JSON bracket structure (static)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user_tournaments = db.relationship('UserTournament', backref='tournament', lazy=True, cascade='all, delete-orphan')
    votes = db.relationship('Vote', backref='tournament', lazy=True, cascade='all, delete-orphan')
    prompt_results = db.relationship('PromptResult', backref='tournament', lazy=True, cascade='all, delete-orphan')
    
    # Indices
    __table_args__ = (
        Index('ix_tournament_created_at', 'created_at'),
    )

class UserTournament(db.Model):
    """Tracks each user's participation in a tournament"""
    id = db.Column(db.Integer, primary_key=True)
    tournament_id = db.Column(db.Integer, db.ForeignKey('tournament.id'), nullable=False)
    user_id = db.Column(db.String(255), nullable=False)  # Session ID initially, Auth0 user ID later
    current_round = db.Column(db.Integer, default=0)
    current_match = db.Column(db.Integer, default=0)
    completed = db.Column(db.Boolean, default=False)
    winner_prompt_index = db.Column(db.Integer)  # Index of winning prompt for this user
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    # Ensure one record per user per tournament
    __table_args__ = (
        UniqueConstraint('tournament_id', 'user_id', name='uq_tournament_user'),
        Index('ix_user_tournament_tournament_id', 'tournament_id'),
        Index('ix_user_tournament_user_id', 'user_id'),
        Index('ix_user_tournament_completed', 'completed'),
        Index('ix_user_tournament_tournament_completed', 'tournament_id', 'completed'),
    )

class Vote(db.Model):
    """Stores individual votes made by users"""
    id = db.Column(db.Integer, primary_key=True)
    tournament_id = db.Column(db.Integer, db.ForeignKey('tournament.id'), nullable=False)
    user_id = db.Column(db.String(255), nullable=False)
    round_number = db.Column(db.Integer, nullable=False)
    match_number = db.Column(db.Integer, nullable=False)
    winner_index = db.Column(db.Integer, nullable=False)  # Index of chosen prompt
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Ensure one vote per user per match
    __table_args__ = (
        UniqueConstraint('tournament_id', 'user_id', 'round_number', 'match_number', name='uq_user_match_vote'),
        Index('ix_vote_tournament_user', 'tournament_id', 'user_id'),
        Index('ix_vote_tournament_id', 'tournament_id'),
    )

class PromptResult(db.Model):
    """Aggregated results for each prompt across all users"""
    id = db.Column(db.Integer, primary_key=True)
    tournament_id = db.Column(db.Integer, db.ForeignKey('tournament.id'), nullable=False)
    prompt_index = db.Column(db.Integer, nullable=False)
    win_count = db.Column(db.Integer, default=0)  # Number of users who voted this prompt as winner
    total_participants = db.Column(db.Integer, default=0)  # Total users who completed the tournament
    win_percentage = db.Column(db.Float, default=0.0)
    
    # Ensure one record per prompt per tournament
    __table_args__ = (
        UniqueConstraint('tournament_id', 'prompt_index', name='uq_tournament_prompt'),
        Index('ix_prompt_result_tournament_id', 'tournament_id'),
    )