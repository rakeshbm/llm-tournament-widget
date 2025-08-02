from flask import Flask
from flask_cors import CORS
from app.config import Config
from app.core import db

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)

    CORS(app)
    db.init_app(app)

    from app.routes.tournaments import bp as tournaments_bp
    app.register_blueprint(tournaments_bp, url_prefix="/api/tournaments")

    with app.app_context():
        db.create_all()

    return app