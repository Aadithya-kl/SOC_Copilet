from abc import ABC, abstractmethod
from app.llm.schemas import LLMRequest, LLMResponse, ProviderHealth

class LLMProvider(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the provider (e.g., 'omniroute', 'ollama')."""
        pass

    @abstractmethod
    async def complete(self, request: LLMRequest) -> LLMResponse:
        """Execute a completion request."""
        pass

    @abstractmethod
    async def health_check(self) -> ProviderHealth:
        """Check if the provider is available."""
        pass
