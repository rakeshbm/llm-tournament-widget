import pytest
import os
from app import create_app, db

@pytest.fixture(scope='session')
def app():
    """Create application for testing"""
    if os.getenv('DATABASE_URL'):
        print("Running tests inside Docker container")
    else:
        print("Running tests locally")
    
    app = create_app()
    
    with app.app_context():
        db.create_all()
        yield app
        
        db.session.remove()
        db.drop_all()

@pytest.fixture(scope='function')
def client(app):
    """Test client"""
    return app.test_client()

@pytest.fixture(scope='function')
def db_session(app):
    """Database session for testing with transaction rollback"""
    with app.app_context():
        connection = db.engine.connect()
        transaction = connection.begin()
        
        db.session.configure(bind=connection)
        
        yield db.session
        
        transaction.rollback()
        connection.close()
        db.session.remove()

@pytest.fixture
def sample_tournament(db_session):
    """Create a sample tournament for testing"""
    from app.models import Tournament, TournamentPrompt
    
    tournament = Tournament(
        question="What's the best programming language?",
        bracket_template=[
            [
                {"participant1": 0, "participant2": 1, "winner": None},
                {"participant1": 2, "participant2": 3, "winner": None}
            ],
            [
                {"participant1": None, "participant2": None, "winner": None}
            ]
        ]
    )
    
    db_session.add(tournament)
    db_session.flush()
    
    prompts = [
        TournamentPrompt(tournament_id=tournament.id, position=0, text="Python is great", response="Python response"),
        TournamentPrompt(tournament_id=tournament.id, position=1, text="JavaScript rocks", response="JS response"),
        TournamentPrompt(tournament_id=tournament.id, position=2, text="Go is fast", response="Go response"),
        TournamentPrompt(tournament_id=tournament.id, position=3, text="Rust is safe", response="Rust response")
    ]
    db_session.add_all(prompts)
    db_session.commit()
    
    return tournament

@pytest.fixture
def sample_tournament_with_prompts(db_session):
    """Create a sample tournament with prompts for results testing"""
    from app.models import Tournament, TournamentPrompt
    
    tournament = Tournament(
        question="Best framework?",
        bracket_template=[
            [
                {"participant1": 0, "participant2": 1, "winner": None},
                {"participant1": 2, "participant2": 3, "winner": None}
            ],
            [
                {"participant1": None, "participant2": None, "winner": None}
            ]
        ]
    )
    db_session.add(tournament)
    db_session.flush()
    
    prompts = [
        TournamentPrompt(tournament_id=tournament.id, position=0, text="React is awesome", response="React response"),
        TournamentPrompt(tournament_id=tournament.id, position=1, text="Vue is simple", response="Vue response"),
        TournamentPrompt(tournament_id=tournament.id, position=2, text="Angular is powerful", response="Angular response"),
        TournamentPrompt(tournament_id=tournament.id, position=3, text="Svelte is fast", response="Svelte response")
    ]
    db_session.add_all(prompts)
    db_session.commit()
    return tournament

@pytest.fixture
def sample_user_tournament(db_session, sample_tournament):
    """Create a sample user tournament"""
    from app.models import UserTournament
    
    user_tournament = UserTournament(
        tournament_id=sample_tournament.id,
        user_id="test_user_123",
        current_round=0,
        current_match=0,
        completed=False
    )
    
    db_session.add(user_tournament)
    db_session.commit()
    
    return user_tournament

@pytest.fixture
def sample_tournament_with_prompts(db_session):
    """Create a sample tournament with prompts for results testing"""
    from app.models import Tournament, TournamentPrompt
    tournament = Tournament(
        question="Best framework?",
        bracket_template=[
            [
                {"participant1": 0, "participant2": 1, "winner": None},
                {"participant1": 2, "participant2": 3, "winner": None}
            ],
            [
                {"participant1": None, "participant2": None, "winner": None}
            ]
        ]
    )
    db_session.add(tournament)
    db_session.flush()
    
    prompts = [
        TournamentPrompt(tournament_id=tournament.id, position=0, text="React is awesome", response="React response"),
        TournamentPrompt(tournament_id=tournament.id, position=1, text="Vue is simple", response="Vue response"),
        TournamentPrompt(tournament_id=tournament.id, position=2, text="Angular is powerful", response="Angular response"),
        TournamentPrompt(tournament_id=tournament.id, position=3, text="Svelte is fast", response="Svelte response")
    ]
    db_session.add_all(prompts)
    db_session.commit()
    return tournament

@pytest.fixture
def sample_user_tournament(db_session, sample_tournament):
    """Create a sample user tournament for testing"""
    from app.models import UserTournament
    user_tournament = UserTournament(
        tournament_id=sample_tournament.id,
        user_id="test_user_123",
        current_round=0,
        current_match=0,
        completed=False
    )
    db_session.add(user_tournament)
    db_session.commit()
    return user_tournament