from app.llm.providers.base import LLMProvider
from app.llm.schemas import LLMRequest, LLMResponse, ProviderHealth
import structlog
from app.core.exceptions import LLMUnavailableError

logger = structlog.get_logger(__name__)

class OllamaProvider(LLMProvider):
    @property
    def name(self) -> str:
        return "ollama"

    async def complete(self, request: LLMRequest) -> LLMResponse:
        raise NotImplementedError("OllamaProvider not yet implemented")

    async def health_check(self) -> ProviderHealth:
        raise NotImplementedError("OllamaProvider not yet implemented")

class OpenRouterProvider(LLMProvider):
    @property
    def name(self) -> str:
        return "openrouter"

    async def complete(self, request: LLMRequest) -> LLMResponse:
        raise NotImplementedError("OpenRouterProvider not yet implemented")

    async def health_check(self) -> ProviderHealth:
        raise NotImplementedError("OpenRouterProvider not yet implemented")

class GroqProvider(LLMProvider):
    @property
    def name(self) -> str:
        return "groq"

    async def complete(self, request: LLMRequest) -> LLMResponse:
        raise NotImplementedError("GroqProvider not yet implemented")

    async def health_check(self) -> ProviderHealth:
        raise NotImplementedError("GroqProvider not yet implemented")

class GeminiProvider(LLMProvider):
    @property
    def name(self) -> str:
        return "gemini"

    async def complete(self, request: LLMRequest) -> LLMResponse:
        raise NotImplementedError("GeminiProvider not yet implemented")

    async def health_check(self) -> ProviderHealth:
        raise NotImplementedError("GeminiProvider not yet implemented")
