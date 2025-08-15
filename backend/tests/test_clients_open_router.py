import pytest
import asyncio
import aiohttp
from unittest.mock import patch, MagicMock, AsyncMock
from app.clients.open_router import OpenRouterClient
from app.schemas import PromptData

class TestOpenRouterClient:
    
    def test_init_success(self):
        """Test successful client initialization"""
        with patch('app.clients.open_router.Config.OPENROUTER_API_KEY', 'test-api-key'):
            client = OpenRouterClient()
            assert client.api_key == 'test-api-key'
            assert client.timeout == 60

    def test_init_no_api_key(self):
        """Test client initialization without API key"""
        with patch('app.clients.open_router.Config.OPENROUTER_API_KEY', None):
            with pytest.raises(ValueError, match="OpenRouter API key is required"):
                OpenRouterClient()

    def test_get_headers(self):
        """Test header generation"""
        with patch('app.clients.open_router.Config.OPENROUTER_API_KEY', 'test-key'):
            client = OpenRouterClient()
            headers = client.get_headers()
            
            assert headers['Authorization'] == 'Bearer test-key'
            assert headers['Content-Type'] == 'application/json'
            assert headers['X-Title'] == 'LLM Prompt Arena'

    def test_get_available_models(self):
        """Test getting available models"""
        with patch('app.clients.open_router.Config.OPENROUTER_API_KEY', 'test-key'):
            client = OpenRouterClient()
            models = client.get_available_models()
            
            assert isinstance(models, dict)
            assert len(models) > 0
            assert "meta-llama/llama-3.1-8b-instruct:free" in models

    def test_validate_prompts_data_success(self):
        """Test successful prompt validation"""
        with patch('app.clients.open_router.Config.OPENROUTER_API_KEY', 'test-key'):
            client = OpenRouterClient()
            
            prompts_data = [
                {"text": "Test prompt 1", "model": "meta-llama/llama-3.1-8b-instruct:free"},
                {"text": "Test prompt 2", "model": "mistralai/mistral-7b-instruct:free"}
            ]
            
            validated = client.validate_prompts_data(prompts_data)
            
            assert len(validated) == 2
            assert all(isinstance(p, PromptData) for p in validated)
            assert validated[0].text == "Test prompt 1"

    def test_validate_prompts_data_invalid_model(self):
        """Test prompt validation with invalid model"""
        with patch('app.clients.open_router.Config.OPENROUTER_API_KEY', 'test-key'):
            client = OpenRouterClient()
            
            prompts_data = [
                {"text": "Test prompt", "model": "invalid-model"}
            ]
            
            with pytest.raises(ValueError, match="Model 'invalid-model' not in available models"):
                client.validate_prompts_data(prompts_data)

    def test_validate_prompts_data_missing_fields(self):
        """Test prompt validation with missing fields"""
        with patch('app.clients.open_router.Config.OPENROUTER_API_KEY', 'test-key'):
            client = OpenRouterClient()
            
            prompts_data = [
                {"text": "Test prompt"}  # Missing model
            ]
            
            with pytest.raises(ValueError, match="Invalid prompt data for prompt 1"):
                client.validate_prompts_data(prompts_data)

    def test_create_openrouter_request_success(self):
        """Test successful request creation"""
        with patch('app.clients.open_router.Config.OPENROUTER_API_KEY', 'test-key'):
            client = OpenRouterClient()
            
            request = client.create_openrouter_request(
                "test-model",
                "You are a helpful assistant",
                "What is AI?"
            )
            
            assert request.model == "test-model"
            assert len(request.messages) == 2
            assert request.messages[0].role == "system"
            assert request.messages[1].role == "user"
            assert request.temperature == 0.7

    @pytest.mark.asyncio
    async def test_generate_completion_success(self):
        """Test successful completion generation"""
        with patch('app.clients.open_router.Config.OPENROUTER_API_KEY', 'test-key'):
            client = OpenRouterClient()
            
            mock_response = MagicMock()
            mock_response.json = AsyncMock(return_value={
                "choices": [
                    {
                        "message": {
                            "content": "This is a test response"
                        }
                    }
                ]
            })
            mock_response.raise_for_status = MagicMock()
            
            mock_post_context = AsyncMock()
            mock_post_context.__aenter__ = AsyncMock(return_value=mock_response)
            mock_post_context.__aexit__ = AsyncMock(return_value=None)
            
            mock_session = MagicMock()
            mock_session.post = MagicMock(return_value=mock_post_context)
            
            semaphore = asyncio.Semaphore(1)
            
            result = await client.generate_completion(
                mock_session,
                "test-model",
                "System prompt",
                "User prompt",
                semaphore
            )
            
            assert result == "This is a test response"

    @pytest.mark.asyncio
    async def test_generate_completion_http_error(self):
        """Test completion generation with HTTP error"""
        with patch('app.clients.open_router.Config.OPENROUTER_API_KEY', 'test-key'):
            client = OpenRouterClient()
            
            # Mock HTTP error
            mock_response = MagicMock()
            mock_response.raise_for_status.side_effect = aiohttp.ClientError("HTTP 500")
            
            mock_post_context = AsyncMock()
            mock_post_context.__aenter__ = AsyncMock(return_value=mock_response)
            mock_post_context.__aexit__ = AsyncMock(return_value=None)
            
            mock_session = MagicMock()
            mock_session.post = MagicMock(return_value=mock_post_context)
            
            semaphore = asyncio.Semaphore(1)
            
            result = await client.generate_completion(
                mock_session,
                "test-model",
                "System prompt",
                "User prompt",
                semaphore
            )
            
            assert result.startswith("[Error: test-model HTTP error")

    @pytest.mark.asyncio
    async def test_generate_completion_timeout(self):
        """Test completion generation with timeout"""
        with patch('app.clients.open_router.Config.OPENROUTER_API_KEY', 'test-key'):
            client = OpenRouterClient()
            
            mock_session = MagicMock()
            mock_session.post.side_effect = asyncio.TimeoutError()
            
            semaphore = asyncio.Semaphore(1)
            
            result = await client.generate_completion(
                mock_session,
                "test-model",
                "System prompt",
                "User prompt",
                semaphore
            )
            
            assert result == "[Error: test-model timed out]"

    @pytest.mark.asyncio
    async def test_generate_completion_empty_response(self):
        """Test completion generation with empty response"""
        with patch('app.clients.open_router.Config.OPENROUTER_API_KEY', 'test-key'):
            client = OpenRouterClient()
            
            mock_response = MagicMock()
            mock_response.json = AsyncMock(return_value={
                "choices": [
                    {
                        "message": {
                            "content": ""
                        }
                    }
                ]
            })
            mock_response.raise_for_status = MagicMock()
            
            mock_post_context = AsyncMock()
            mock_post_context.__aenter__ = AsyncMock(return_value=mock_response)
            mock_post_context.__aexit__ = AsyncMock(return_value=None)
            
            mock_session = MagicMock()
            mock_session.post = MagicMock(return_value=mock_post_context)
            
            semaphore = asyncio.Semaphore(1)
            
            result = await client.generate_completion(
                mock_session,
                "test-model",
                "System prompt",
                "User prompt",
                semaphore
            )
            
            assert result.startswith("[Error: test-model failed")

    def test_generate_completions_success(self):
        """Test successful multiple completions generation"""
        with patch('app.clients.open_router.Config.OPENROUTER_API_KEY', 'test-key'):
            client = OpenRouterClient()
            
            prompts_data = [
                {"text": "Prompt 1", "model": "meta-llama/llama-3.1-8b-instruct:free"},
                {"text": "Prompt 2", "model": "mistralai/mistral-7b-instruct:free"}
            ]
            
            with patch.object(client, '_generate_completions_async') as mock_async:
                mock_async.return_value = ["Response 1", "Response 2"]
                
                results = client.generate_completions(prompts_data, "Test question?")
                
                assert len(results) == 2
                assert results[0] == "Response 1"
                assert results[1] == "Response 2"

    def test_generate_completions_invalid_prompts(self):
        """Test completions generation with invalid prompts"""
        with patch('app.clients.open_router.Config.OPENROUTER_API_KEY', 'test-key'):
            client = OpenRouterClient()
            
            prompts_data = [
                {"text": "Prompt", "model": "invalid-model"}
            ]
            
            with pytest.raises(ValueError, match="Model 'invalid-model' not in available models"):
                client.generate_completions(prompts_data, "Test question?")

    def test_generate_completions_empty_question(self):
        """Test completions generation with empty question"""
        with patch('app.clients.open_router.Config.OPENROUTER_API_KEY', 'test-key'):
            client = OpenRouterClient()
            
            prompts_data = [
                {"text": "Prompt", "model": "meta-llama/llama-3.1-8b-instruct:free"}
            ]
            
            with pytest.raises(ValueError, match="Question cannot be empty"):
                client.generate_completions(prompts_data, "")

    def test_client_timeout_parameter(self):
        """Test client with custom timeout"""
        with patch('app.clients.open_router.Config.OPENROUTER_API_KEY', 'test-key'):
            client = OpenRouterClient(timeout=120)
            assert client.timeout == 120

    def test_models_list_not_empty(self):
        """Test that the models list contains expected models"""
        with patch('app.clients.open_router.Config.OPENROUTER_API_KEY', 'test-key'):
            client = OpenRouterClient()
            models = client.get_available_models()
            
            # Check for some expected models
            expected_models = [
                "meta-llama/llama-3.1-8b-instruct:free",
                "mistralai/mistral-7b-instruct:free",
                "google/gemma-2-9b-it:free"
            ]
            
            for model in expected_models:
                assert model in models
                assert isinstance(models[model], str)
                assert len(models[model]) > 0