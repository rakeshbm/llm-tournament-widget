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
    assert response is None

def test_create_bracket_basic():
    """Test bracket creation with 3 prompts (requires 1 bye)"""
    prompts = ["Prompt 1", "Prompt 2", "Prompt 3"]
    bracket = utils.create_bracket(prompts)
    
    # Should have 2 rounds: semifinals + final
    assert len(bracket) == 2
    
    first_round = bracket[0]
    assert len(first_round) == 2  # 4-person bracket has 2 first round matches
    
    # Check that all matches have proper structure
    for match in first_round:
        assert 'participant1' in match
        assert 'participant2' in match
        assert 'winner' in match
        
        # Participants should be valid prompt indices or -1 (bye)
        p1, p2 = match['participant1'], match['participant2']
        assert p1 == -1 or (0 <= p1 < len(prompts))
        assert p2 == -1 or (0 <= p2 < len(prompts))
    
    # Should have exactly one bye since we have 3 prompts in a 4-slot bracket
    all_participants = []
    for match in first_round:
        all_participants.extend([match['participant1'], match['participant2']])
    
    bye_count = all_participants.count(-1)
    assert bye_count == 1
    
    # All prompt indices should appear exactly once
    prompt_indices = [p for p in all_participants if p != -1]
    assert sorted(prompt_indices) == [0, 1, 2]

def test_create_bracket_with_power_of_two():
    """Test bracket creation with 4 prompts (perfect power of 2, no byes needed)"""
    prompts = ["Prompt 1", "Prompt 2", "Prompt 3", "Prompt 4"]
    bracket = utils.create_bracket(prompts)
    
    # Should have 2 rounds: semifinals + final
    assert len(bracket) == 2
    
    first_round = bracket[0]
    assert len(first_round) == 2  # 4-person bracket has 2 first round matches
    
    # No byes should be present
    for match in first_round:
        assert match['participant1'] != -1
        assert match['participant2'] != -1
        assert 0 <= match['participant1'] < len(prompts)
        assert 0 <= match['participant2'] < len(prompts)
    
    # All prompt indices should appear exactly once
    all_participants = []
    for match in first_round:
        all_participants.extend([match['participant1'], match['participant2']])
    
    assert sorted(all_participants) == [0, 1, 2, 3]

def test_create_bracket_two_prompts():
    """Test bracket creation with 2 prompts (perfect for single elimination)"""
    prompts = ["Prompt 1", "Prompt 2"]
    bracket = utils.create_bracket(prompts)
    
    # Should have 1 round with 1 match
    assert len(bracket) == 1
    assert len(bracket[0]) == 1
    
    match = bracket[0][0]
    participants = sorted([match['participant1'], match['participant2']])
    assert participants == [0, 1]

def test_create_bracket_large():
    """Test bracket creation with 7 prompts (requires 8-slot bracket with 1 bye)"""
    prompts = [f"Prompt {i+1}" for i in range(7)]
    bracket = utils.create_bracket(prompts)
    
    # Should have 3 rounds: quarterfinals + semifinals + final
    assert len(bracket) == 3
    
    first_round = bracket[0]
    assert len(first_round) == 4  # 8-person bracket has 4 first round matches
    
    # Count byes
    all_participants = []
    for match in first_round:
        all_participants.extend([match['participant1'], match['participant2']])
    
    bye_count = all_participants.count(-1)
    assert bye_count == 1  # Only 1 bye needed for 7 prompts in 8-slot bracket
    
    # All prompt indices should appear exactly once
    prompt_indices = [p for p in all_participants if p != -1]
    assert sorted(prompt_indices) == list(range(7))

def test_create_bracket_bye_advancement():
    """Test that byes are properly handled with winner advancement"""
    prompts = ["Prompt 1", "Prompt 2", "Prompt 3"]
    bracket = utils.create_bracket(prompts)
    
    first_round = bracket[0]
    
    # Find the match with a bye
    bye_match = None
    regular_match = None
    
    for match in first_round:
        if match['participant1'] == -1 or match['participant2'] == -1:
            bye_match = match
        else:
            regular_match = match
    
    # There should be exactly one bye match and one regular match
    assert bye_match is not None
    assert regular_match is not None
    
    # Bye match should have a winner automatically determined
    assert bye_match['winner'] is not None
    assert bye_match['winner'] != -1
    
    # Regular match should not have a predetermined winner
    assert regular_match['winner'] is None

def test_create_bracket_randomization():
    """Test that bracket creation uses randomization (run multiple times)"""
    prompts = ["Prompt 1", "Prompt 2", "Prompt 3", "Prompt 4"]
    
    # Generate multiple brackets and check if they differ
    brackets = []
    for _ in range(10):
        bracket = utils.create_bracket(prompts)
        first_round_participants = []
        for match in bracket[0]:
            first_round_participants.extend([match['participant1'], match['participant2']])
        brackets.append(tuple(first_round_participants))
    
    # With randomization, we should get at least some different arrangements
    # (This might occasionally fail due to randomness)
    unique_brackets = set(brackets)
    assert len(unique_brackets) > 1, "Brackets should be randomized"

def test_bracket_structure_consistency():
    """Test that bracket structure is consistent across different sizes"""
    for num_prompts in range(2, 9):  # Test various sizes
        prompts = [f"Prompt {i+1}" for i in range(num_prompts)]
        bracket = utils.create_bracket(prompts)
        
        # Calculate expected bracket size and rounds
        bracket_size = 2 ** ((num_prompts - 1).bit_length())
        expected_rounds = (bracket_size - 1).bit_length()
        
        assert len(bracket) == expected_rounds
        
        # Check that each round has the right number of matches
        expected_matches = bracket_size // 2
        for round_idx, round_matches in enumerate(bracket):
            assert len(round_matches) == expected_matches
            expected_matches //= 2
        
        # Verify all prompt indices appear exactly once in first round
        first_round = bracket[0]
        all_participants = []
        for match in first_round:
            all_participants.extend([match['participant1'], match['participant2']])
        
        prompt_indices = [p for p in all_participants if p != -1]
        assert sorted(prompt_indices) == list(range(num_prompts))
        
        # Verify correct number of byes
        bye_count = all_participants.count(-1)
        expected_byes = bracket_size - num_prompts
        assert bye_count == expected_byes