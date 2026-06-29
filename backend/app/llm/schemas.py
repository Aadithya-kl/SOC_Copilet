from enum import Enum
from pydantic import BaseModel, Field
from typing import Any

class TaskType(str, Enum):
    GENERAL = "general"
    STRUCTURED_EXTRACTION = "structured_extraction"
    REASONING = "reasoning"
    NARRATIVE = "narrative"
    EMBEDDING = "embedding"
    FAST_CLASSIFICATION = "fast_classification"

class MessageRole(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"

class Message(BaseModel):
    role: MessageRole
    content: str

class LLMRequest(BaseModel):
    messages: list[Message]
    model: str | None = None
    task_type: TaskType = TaskType.GENERAL
    max_tokens: int = 2048
    temperature: float = 0.1
    response_format: dict | None = None
    timeout_seconds: int = 120
    allow_fallback: bool = True
    metadata: dict[str, Any] = Field(default_factory=dict)

class LLMResponse(BaseModel):
    content: str | dict | list
    model_used: str
    provider_used: str
    input_tokens: int
    output_tokens: int
    latency_ms: int

class ProviderHealth(BaseModel):
    status: str
    latency_ms: int | None = None
    error: str | None = None
