from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from dotenv import load_dotenv

db = SQLAlchemy()

def create_app():
    load_dotenv()
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object("config.Config")
    
    CORS(app)
    db.init_app(app)

    from app.routes.tournaments import bp as tournaments_bp
    app.register_blueprint(tournaments_bp, url_prefix="/api/tournaments")

    with app.app_context():
        db.create_all()

    return app
