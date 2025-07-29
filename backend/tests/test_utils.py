import pytest
from unittest.mock import patch, MagicMock
from app import utils, create_app

@pytest.fixture(autouse=True)
def app_context():
    app = create_app()
    app.config["OPENROUTER_API_KEY"] = "fake_api_key"
    with app.app_context():
        yield

@patch("app.utils.requests.post")
def test_generate_llm_response_success(mock_post):
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "choices": [{"message": {"content": "Test response"}}]
    }
    mock_response.raise_for_status.return_value = None
    mock_post.return_value = mock_response

    prompt = "You are an assistant."
    question = "Hello, what is 2 + 2?"
    response = utils.generate_llm_response(prompt, question)

    assert response == "Test response"
    mock_post.assert_called_once()
    assert "Authorization" in mock_post.call_args[1]['headers']
    assert "fake_api_key" in mock_post.call_args[1]['headers']['Authorization']

@patch("app.utils.requests.post")
def test_generate_llm_response_failure(mock_post):
    mock_post.side_effect = Exception("API error")

    response = utils.generate_llm_response("prompt", "question")
    assert response == None

def test_create_bracket_basic():
    prompts = ["Prompt 1", "Prompt 2", "Prompt 3"]
    bracket = utils.create_bracket(prompts)
    
    assert len(bracket) >= 1
    
    first_round = bracket[0]
    bracket_size = 2 ** ((len(prompts)-1).bit_length())
    assert len(first_round) == bracket_size // 2

    for match in first_round:
        assert 'participant1' in match
        assert 'participant2' in match
        assert 'winner' in match
        assert (match['participant1'] == -1 or (0 <= match['participant1'] < len(prompts)))
        assert (match['participant2'] == -1 or (0 <= match['participant2'] < len(prompts)) or match['participant2'] is None)

def test_create_bracket_with_power_of_two():
    prompts = ["Prompt 1", "Prompt 2", "Prompt 3", "Prompt 4"]
    bracket = utils.create_bracket(prompts)
    assert len(bracket) == 2
    first_round = bracket[0]
    for match in first_round:
        assert match['participant1'] != -1
        assert match['participant2'] != -1
