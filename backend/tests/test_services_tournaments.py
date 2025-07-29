import pytest
import json
from unittest.mock import patch
from app.models import Tournament
from app.services.tournaments import TournamentService

@pytest.fixture
def mock_db_session(monkeypatch):
    class DummySession:
        def add(self, obj): pass
        def commit(self): pass
    dummy_session = DummySession()
    monkeypatch.setattr("app.db.session", dummy_session)
    return dummy_session

@pytest.fixture
def sample_prompts():
    return ["prompt1", "prompt2", "prompt3", "prompt4"]

@pytest.fixture
def sample_question():
    return "Sample question?"

@pytest.fixture
def sample_bracket():
    return [
        [
            {"participant1": 0, "participant2": 1, "winner": None},
            {"participant1": 2, "participant2": 3, "winner": None},
        ],
        [
            {"participant1": None, "participant2": None, "winner": None}
        ]
    ]

@patch("app.services.tournaments.generate_llm_response")
@patch("app.services.tournaments.create_bracket")
def test_create_tournament(mock_create_bracket, mock_generate_llm_response, mock_db_session, sample_prompts, sample_question, sample_bracket):
    mock_generate_llm_response.side_effect = lambda p, q: f"response for {p}"
    mock_create_bracket.return_value = sample_bracket

    tournament = TournamentService.create_tournament(sample_question, sample_prompts)

    prompts = json.loads(tournament.prompts)
    responses = json.loads(tournament.responses)
    bracket = json.loads(tournament.bracket)

    assert prompts == sample_prompts
    assert responses == [f"response for {p}" for p in sample_prompts]
    assert bracket == sample_bracket
    assert tournament.question == sample_question
    assert tournament.completed is False
    assert tournament.winner_prompt is None

def test_vote_advances_bracket_and_records_vote(mock_db_session):
    tournament = Tournament(
        id=1,
        question="Q",
        prompts=json.dumps(["p1", "p2", "p3", "p4"]),
        responses=json.dumps(["r1", "r2", "r3", "r4"]),
        bracket=json.dumps([
            [
                {"participant1": 0, "participant2": 1, "winner": None},
                {"participant1": 2, "participant2": 3, "winner": None},
            ],
            [
                {"participant1": None, "participant2": None, "winner": None}
            ]
        ]),
        completed=False,
        winner_prompt=None,
    )

    bracket, completed, winner_prompt = TournamentService.vote(tournament, 0, 0, 0)

    assert bracket[0][0]['winner'] == 0
    assert bracket[1][0]['participant1'] == 0
    assert completed is False
    assert winner_prompt is None

def test_vote_final_round_completes_tournament(mock_db_session):
    tournament = Tournament(
        id=1,
        question="Q",
        prompts=json.dumps(["p1", "p2", "p3", "p4"]),
        responses=json.dumps(["r1", "r2", "r3", "r4"]),
        bracket=json.dumps([
            [
                {"participant1": 0, "participant2": 1, "winner": 0}
            ]
        ]),
        completed=False,
        winner_prompt=None,
    )

    bracket, completed, winner_prompt = TournamentService.vote(tournament, 0, 0, 0)

    assert bracket[0][0]['winner'] == 0
    assert completed is True
    assert winner_prompt == "p1"

def test_vote_invalid_round_raises(mock_db_session):
    tournament = Tournament(
        id=1,
        bracket=json.dumps([[]]),
        prompts=json.dumps([]),
        completed=False
    )
    with pytest.raises(ValueError, match="Invalid round number"):
        TournamentService.vote(tournament, 5, 0, 0)

def test_vote_invalid_match_raises(mock_db_session):
    tournament = Tournament(
        id=1,
        bracket=json.dumps([[{}]]),
        prompts=json.dumps([]),
        completed=False
    )
    with pytest.raises(ValueError, match="Invalid match number"):
        TournamentService.vote(tournament, 0, 5, 0)

def test_vote_invalid_winner_index_raises(mock_db_session):
    tournament = Tournament(
        id=1,
        bracket=json.dumps([
            [
                {"participant1": 0, "participant2": 1, "winner": None}
            ]
        ]),
        prompts=json.dumps(["p1", "p2"]),
        completed=False
    )
    with pytest.raises(ValueError, match="Winner index must be one of the participants"):
        TournamentService.vote(tournament, 0, 0, 2)

@patch("app.services.tournaments.generate_llm_response")
def test_create_tournament_raises_if_llm_fails(mock_generate_llm_response, mock_db_session, sample_prompts, sample_question):
    mock_generate_llm_response.return_value = None

    with pytest.raises(RuntimeError, match="Failed to generate one or more LLM responses."):
        TournamentService.create_tournament(sample_question, sample_prompts)
