from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime

# ===== REQUEST SCHEMAS =====

class PromptData(BaseModel):
    """Schema for individual prompt data in tournament creation"""
    text: str = Field(..., min_length=1, max_length=5000, description="The prompt text")
    model: str = Field(..., description="The model identifier to use")
    
    @field_validator('text')
    @classmethod
    def validate_text_not_empty(cls, v):
        if not v.strip():
            raise ValueError('Prompt text cannot be empty or whitespace only')
        return v.strip()

class CreateTournamentRequest(BaseModel):
    """Schema for creating a new tournament"""
    question: str = Field(..., min_length=1, max_length=1000, description="The tournament question")
    prompts: List[PromptData] = Field(..., min_length=2, max_length=16, description="List of prompts")
    
    @field_validator('question')
    @classmethod
    def validate_question_not_empty(cls, v):
        if not v.strip():
            raise ValueError('Question cannot be empty or whitespace only')
        return v.strip()
    
    @field_validator('prompts')
    @classmethod
    def validate_unique_combinations(cls, v):
        seen = set()
        for prompt in v:
            key = (prompt.text, prompt.model)
            if key in seen:
                raise ValueError('Duplicate prompt-model combinations are not allowed')
            seen.add(key)
        return v

class VoteRequest(BaseModel):
    """Schema for submitting a vote"""
    round: int = Field(..., ge=0, description="Round number (0-indexed)")
    match: int = Field(..., ge=0, description="Match number within the round (0-indexed)")
    winner: int = Field(..., ge=0, description="Index of the winning prompt")

# ===== RESPONSE SCHEMAS =====

class UserState(BaseModel):
    """User's tournament state"""
    completed: bool = Field(description="Whether user completed the tournament")
    winner_prompt_index: Optional[int] = Field(description="Winning prompt index if completed")
    next_match: Optional[tuple[int, int]] = Field(description="Next votable match (round, match)")

class TournamentBase(BaseModel):
    """Base tournament information"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    question: str
    prompts: List[str]
    responses: List[str]
    models: List[str]
    bracket_template: List[List[Dict[str, Any]]]

class TournamentResponse(TournamentBase):
    """Tournament response with user state"""
    user_bracket: Optional[List[List[Dict[str, Any]]]] = None
    user_state: UserState

class PromptRanking(BaseModel):
    """Ranking information for a prompt"""
    prompt: str
    prompt_index: int
    model: str
    win_count: int = Field(ge=0)
    win_percentage: float = Field(ge=0.0, le=100.0)

class ParticipationStats(BaseModel):
    """Tournament participation statistics"""
    total_participants: int = Field(ge=0)
    completed_participants: int = Field(ge=0)
    completion_rate: float = Field(ge=0.0, le=100.0)

class TournamentWithResultsResponse(TournamentBase):
    """Tournament response including results and stats"""
    user_bracket: Optional[List[List[Dict[str, Any]]]] = None
    user_state: UserState
    rankings: List[PromptRanking]
    stats: ParticipationStats

class TournamentListItem(BaseModel):
    """Tournament item in list view"""
    id: int
    question: str
    num_prompts: int = Field(ge=0)
    created_at: datetime
    total_participants: int = Field(ge=0)
    completed_participants: int = Field(ge=0)
    completion_rate: float = Field(ge=0.0, le=100.0)

class TournamentListResponse(BaseModel):
    """Response for tournament list endpoint"""
    tournaments: List[TournamentListItem]

class VoteResponse(BaseModel):
    """Response after submitting a vote"""
    user_bracket: List[List[Dict[str, Any]]]
    completed: bool
    winner_prompt_index: Optional[int] = None
    user_id: str

class ModelsResponse(BaseModel):
    """Response for available models"""
    models: Dict[str, str] = Field(description="Available models mapping")

class ErrorResponse(BaseModel):
    """Standard error response"""
    error: str = Field(description="Error message")

# ===== OPENROUTER SCHEMAS =====

class OpenRouterMessage(BaseModel):
    """OpenRouter API message format"""
    role: str = Field(..., pattern=r'^(system|user|assistant)$')
    content: str = Field(..., min_length=1)

class OpenRouterRequest(BaseModel):
    """OpenRouter API request format"""
    model: str
    messages: List[OpenRouterMessage]
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=1000, gt=0, le=4000)

class OpenRouterChoice(BaseModel):
    """OpenRouter API response choice"""
    message: Dict[str, str]
    finish_reason: str

class OpenRouterResponse(BaseModel):
    """OpenRouter API response format"""
    choices: List[OpenRouterChoice]
    usage: Optional[Dict[str, int]] = None

# Update forward references
TournamentWithResultsResponse.model_rebuild()