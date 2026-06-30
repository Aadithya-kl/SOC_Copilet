import logging
from abc import ABC, abstractmethod
from typing import Dict, Type, Optional, AsyncGenerator
from pydantic import BaseModel
from openai import AsyncOpenAI
import json

logger = logging.getLogger(__name__)

class BaseLLMProvider(ABC):
    """Abstract base class for all LLM providers."""
    
    @abstractmethod
    async def generate_structured(self, prompt: str, schema: Type[BaseModel], model: str = "default") -> BaseModel:
        """Generates a structured response validating against the provided schema."""
        pass
        
    @abstractmethod
    async def generate_stream(self, prompt: str, model: str = "default") -> AsyncGenerator[str, None]:
        """Generates a streaming text response."""
        pass


class OpenAICompatibleProvider(BaseLLMProvider):
    """Provider wrapper for OpenAI-compatible APIs (OpenRouter, OmniRoute, Groq, Ollama)."""
    def __init__(self, base_url: str, api_key: str, default_model: str):
        self.client = AsyncOpenAI(base_url=base_url, api_key=api_key)
        self.default_model = default_model

    async def generate_structured(self, prompt: str, schema: Type[BaseModel], model: str = "default") -> BaseModel:
        target_model = self.default_model if model == "default" else model
        
        # We use a standard chat completion with JSON mode or prompting for JSON
        response = await self.client.chat.completions.create(
            model=target_model,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        
        content = response.choices[0].message.content
        if not content:
            raise ValueError("Empty response from LLM")
            
        try:
            parsed = json.loads(content)
            return schema.model_validate(parsed)
        except Exception as e:
            logger.error(f"Failed to validate LLM response against schema: {e}")
            raise ValueError(f"Schema validation failed: {e}")

    async def generate_stream(self, prompt: str, model: str = "default") -> AsyncGenerator[str, None]:  # type: ignore
        target_model = self.default_model if model == "default" else model
        
        stream = await self.client.chat.completions.create(
            model=target_model,
            messages=[{"role": "user", "content": prompt}],
            stream=True
        )
        
        async for chunk in stream:
            content = chunk.choices[0].delta.content
            if content:
                yield content


class ProviderRegistry:
    """Registry to manage and dynamically resolve LLM providers."""
    def __init__(self):
        self._providers: Dict[str, BaseLLMProvider] = {}
        self._default_provider: Optional[str] = None
        
    def register(self, name: str, provider: BaseLLMProvider, is_default: bool = False):
        self._providers[name] = provider
        if is_default or self._default_provider is None:
            self._default_provider = name
            
    def get_provider(self, name: Optional[str] = None) -> BaseLLMProvider:
        target = name or self._default_provider
        if not target or target not in self._providers:
            raise ValueError(f"Provider '{target}' not registered.")
        return self._providers[target]

# Global registry instance
provider_registry = ProviderRegistry()
