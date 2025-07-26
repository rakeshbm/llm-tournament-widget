from app import db

class Tournament(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    input_question = db.Column(db.String(256), nullable=False)
    prompts = db.relationship("Prompt", backref="tournament", lazy=True)

class Prompt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(512), nullable=False)
    result = db.Column(db.Text)
    tournament_id = db.Column(db.Integer, db.ForeignKey("tournament.id"), nullable=False)
    votes = db.relationship("Vote", backref="prompt", lazy=True)

class Vote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    prompt_id = db.Column(db.Integer, db.ForeignKey("prompt.id"), nullable=False)
