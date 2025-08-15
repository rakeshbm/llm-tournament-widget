import asyncio
import aiohttp
from typing import List, Dict
from app.config import Config
from app.schemas import OpenRouterRequest, OpenRouterMessage, PromptData
from pydantic import ValidationError

class OpenRouterClient:
    """OpenRouter API client with models"""
    
    BASE_URL = "https://openrouter.ai/api/v1"
    
    MODELS = {
        # Meta Llama Models
        "meta-llama/llama-3.1-8b-instruct:free": "Llama 3.1 8B (Free)",
        "meta-llama/llama-3-8b-instruct:free": "Llama 3 8B (Free)",
        "meta-llama/llama-3.2-3b-instruct:free": "Llama 3.2 3B (Free)",
        "meta-llama/llama-3.2-1b-instruct:free": "Llama 3.2 1B (Free)",
        
        # Mistral Models
        "mistralai/mistral-7b-instruct:free": "Mistral 7B (Free)",
        
        # Google Models
        "google/gemma-2-9b-it:free": "Gemma 2 9B (Free)",
        "google/gemma-7b-it:free": "Gemma 7B (Free)",
        
        # Microsoft Models
        "microsoft/phi-3-mini-128k-instruct:free": "Phi-3 Mini (Free)",
        "microsoft/phi-3-medium-128k-instruct:free": "Phi-3 Medium (Free)",
        
        # Nous Research Models
        "nousresearch/nous-hermes-2-mixtral-8x7b-dpo": "Nous Hermes 2 Mixtral (Free)",
        
        # Other Models
        "openchat/openchat-7b:free": "OpenChat 7B (Free)",
    }
    
    def __init__(self, timeout: int = 60):
        self.api_key = Config.OPENROUTER_API_KEY
        self.timeout = timeout
        
        if not self.api_key:
            raise ValueError("OpenRouter API key is required")
    
    def get_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "X-Title": "LLM Prompt Arena"
        }
    
    def get_available_models(self) -> Dict[str, str]:
        """Get curated list of models"""
        return self.MODELS.copy()
    
    def validate_prompts_data(self, prompts_data: List[Dict[str, str]]) -> List[PromptData]:
        """Validate and parse prompts data"""
        validated_prompts = []
        for i, prompt_data in enumerate(prompts_data):
            try:
                validated_prompt = PromptData(**prompt_data)
                if validated_prompt.model not in self.MODELS:
                    raise ValueError(f"Model '{validated_prompt.model}' not in available models for prompt {i+1}")
                validated_prompts.append(validated_prompt)
            except ValidationError as e:
                raise ValueError(f"Invalid prompt data for prompt {i+1}: {str(e)}")
        
        return validated_prompts
    
    def create_openrouter_request(self, model: str, system_prompt: str, user_prompt: str) -> OpenRouterRequest:
        """Create validated OpenRouter request"""
        try:
            messages = [
                OpenRouterMessage(role="system", content=system_prompt),
                OpenRouterMessage(role="user", content=user_prompt)
            ]
            
            return OpenRouterRequest(
                model=model,
                messages=messages,
                temperature=0.7,
                max_tokens=1000
            )
        except ValidationError as e:
            raise ValueError(f"Invalid request data for model {model}: {str(e)}")
    
    async def generate_completion(self, session, model, system_prompt, user_prompt, semaphore):
        """Generate single completion with validation"""
        async with semaphore:
            try:
                # Validate request data
                request_data = self.create_openrouter_request(model, system_prompt, user_prompt)
                
                request_json = request_data.model_dump()
                
                async with session.post(
                    f"{self.BASE_URL}/chat/completions",
                    headers=self.get_headers(),
                    json=request_json,
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    response.raise_for_status()
                    result = await response.json()
                    
                    # Extract content with validation
                    try:
                        content = result["choices"][0]["message"]["content"].strip()
                        if not content:
                            raise ValueError("Empty response from API")
                        return content
                    except (KeyError, IndexError) as e:
                        raise ValueError(f"Invalid response format: {e}")
                        
            except ValidationError as e:
                print(f"Validation error for model {model}: {e}")
                return f"[Error: Invalid request data for {model}]"
            except aiohttp.ClientError as e:
                print(f"HTTP error for model {model}: {e}")
                return f"[Error: {model} HTTP error - {str(e)[:100]}]"
            except asyncio.TimeoutError:
                print(f"Timeout error for model {model}")
                return f"[Error: {model} timed out]"
            except Exception as e:
                print(f"Unexpected error for model {model}: {e}")
                return f"[Error: {model} failed - {str(e)[:100]}]"
    
    def generate_completions(self, prompts_data: List[Dict[str, str]], question: str) -> List[str]:
        """Generate completions for all prompts with validation"""
        # Validate all prompts first
        validated_prompts = self.validate_prompts_data(prompts_data)
        
        # Validate question
        if not question or not question.strip():
            raise ValueError("Question cannot be empty")
        
        return asyncio.run(self._generate_completions_async(validated_prompts, question.strip()))
    
    async def _generate_completions_async(self, validated_prompts: List[PromptData], question: str) -> List[str]:
        """Async completion generation with validated data"""
        semaphore = asyncio.Semaphore(10)  
        
        async with aiohttp.ClientSession() as session:
            tasks = [
                self.generate_completion(
                    session, 
                    prompt.model,
                    prompt.text,
                    question,
                    semaphore
                )
                for prompt in validated_prompts
            ]
            
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            
            final_responses = []
            for i, response in enumerate(responses):
                if isinstance(response, Exception):
                    model = validated_prompts[i].model
                    final_responses.append(f"[Error: {model} failed - {str(response)[:100]}]")
                else:
                    final_responses.append(response)
            
            return final_responses