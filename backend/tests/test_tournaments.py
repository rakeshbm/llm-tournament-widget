import pytest
from app import create_app, db
from app.models import Prompt

@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite://"
    with app.app_context():
        db.create_all()
    client = app.test_client()
    yield client

def test_create_tournament_valid(client):
    # arrange
    data = {
        "name": "Test Tournament",
        "input_question": "What's the capital of U.S.?",
        "prompts": ["Prompt A", "Prompt B"]
    }

    #  act
    response = client.post("/api/tournaments/", json=data)

    # assert
    assert response.status_code == 201
    assert "id" in response.get_json()

def test_create_tournament_missing_fields(client):
    # arrange
    data = {}

    # act
    response = client.post("/api/tournaments/", json=data)

    # assert
    assert response.status_code == 400
    assert "error" in response.get_json()

def test_create_tournament_invalid_prompts(client):
    # arrange
    data = {
        "name": "Sample",
        "input_question": "Q?",
        "prompts": [""]
    }

    # act
    response = client.post("/api/tournaments/", json=data)

    # asert
    assert response.status_code == 400
    assert "error" in response.get_json()

def test_create_tournament_not_enough_prompts(client):
    # arrange
    data = {
        "name": "One prompt",
        "input_question": "Q?",
        "prompts": ["Only one"]
    }

    # act
    response = client.post("/api/tournaments/", json=data)

    # assert
    assert response.status_code == 400
    assert "error" in response.get_json()

def test_vote_valid(client):
    # arrange
    res = client.post(
        "/api/tournaments/",
        json={
            "name": "Vote Tournament",
            "input_question": "Pick one",
            "prompts": ["Prompt 1", "Prompt 2"]
        }
    )
    tournament_id = res.get_json()["id"]

    from app.models import Prompt
    from app import create_app

    app = create_app()
    with app.app_context():
        prompt_id = Prompt.query.filter_by(tournament_id=tournament_id).first().id

    # act
    vote_res = client.post(
        f"/api/tournaments/{tournament_id}/vote",
        json={"prompt_id": prompt_id}
    )
    # assert
    assert vote_res.status_code == 200
    assert vote_res.get_json()["message"] == "Vote recorded."

def test_vote_invalid_prompt_id(client):
    # arrange
    res = client.post(
        "/api/tournaments/",
        json={
            "name": "Invalid Vote",
            "input_question": "Pick one",
            "prompts": ["A", "B"]
        }
    )
    tournament_id = res.get_json()["id"]

    # act
    vote_res = client.post(
        f"/api/tournaments/{tournament_id}/vote",
        json={"prompt_id": 9999}
    )

    # assert
    assert vote_res.status_code == 404
    assert "error" in vote_res.get_json()

def test_vote_non_integer_prompt_id(client):
    # arrange
    res = client.post(
        "/api/tournaments/",
        json={
            "name": "Non-int Vote",
            "input_question": "Pick one",
            "prompts": ["A", "B"]
        }
    )
    tournament_id = res.get_json()["id"]

    # act
    vote_res = client.post(
        f"/api/tournaments/{tournament_id}/vote",
        json={"prompt_id": "not-an-int"}
    )

    # assert
    assert vote_res.status_code == 400
    assert "error" in vote_res.get_json()
