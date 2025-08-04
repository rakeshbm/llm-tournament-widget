from datetime import datetime
from app import db
from sqlalchemy import UniqueConstraint, Index, text
from sqlalchemy.dialects.postgresql import JSONB, SMALLINT

class Tournament(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.Text, nullable=False)
    bracket_template = db.Column(JSONB)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user_tournaments = db.relationship('UserTournament', backref='tournament', lazy=True, cascade='all, delete-orphan')
    prompts = db.relationship('TournamentPrompt', backref='tournament', lazy=True, cascade='all, delete-orphan', order_by='TournamentPrompt.position')
    
    __table_args__ = (
        Index('ix_tournament_created_at', 'created_at'),
        Index('ix_tournament_bracket_gin', 'bracket_template', postgresql_using='gin'),
    )

class TournamentPrompt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tournament_id = db.Column(db.Integer, db.ForeignKey('tournament.id'), nullable=False)
    position = db.Column(SMALLINT, nullable=False)
    text = db.Column(db.Text, nullable=False)
    response = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        UniqueConstraint('tournament_id', 'position', name='uq_tournament_prompt_position'),
        Index('ix_tournament_prompt_position', 'tournament_id', 'position'),
    )

class UserTournament(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tournament_id = db.Column(db.Integer, db.ForeignKey('tournament.id'), nullable=False)
    user_id = db.Column(db.String(255), nullable=False)  # Session ID initially, Auth0 user ID later
    current_round = db.Column(SMALLINT, default=0)
    current_match = db.Column(SMALLINT, default=0)
    completed = db.Column(db.Boolean, default=False)
    winner_prompt_index = db.Column(SMALLINT)
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    votes = db.relationship('Vote', backref='user_tournament', lazy=True, cascade='all, delete-orphan')
    
    __table_args__ = (
        UniqueConstraint('tournament_id', 'user_id', name='uq_tournament_user'),
        Index('ix_user_tournament_incomplete', 'tournament_id', 'user_id', 
            postgresql_where=text('completed = false')),
        Index('ix_user_tournament_completed', 'tournament_id', 
            postgresql_where=text('completed = true')),
    )

class Vote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_tournament_id = db.Column(db.Integer, db.ForeignKey('user_tournament.id'), nullable=False)
    round_number = db.Column(SMALLINT, nullable=False)
    match_number = db.Column(SMALLINT, nullable=False)
    winner_index = db.Column(SMALLINT, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    @property
    def tournament_id(self):
        return self.user_tournament.tournament_id
    
    @property
    def user_id(self):
        return self.user_tournament.user_id
    
    __table_args__ = (
        UniqueConstraint('user_tournament_id', 'round_number', 'match_number', name='uq_vote_match'),
        Index('ix_vote_user_tournament_id', 'user_tournament_id'),
    )