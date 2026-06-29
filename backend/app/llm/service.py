from typing import Any
import structlog
from app.llm.schemas import LLMRequest, LLMResponse
from app.llm.providers.base import LLMProvider
from app.llm.providers.omniroute import OmniRouteProvider
from app.core.exceptions import LLMUnavailableError

logger = structlog.get_logger(__name__)

class LLMService:
    def __init__(self):
        # In Phase 0, we only register OmniRoute
        self.providers: dict[str, LLMProvider] = {
            "omniroute": OmniRouteProvider()
        }

    async def complete(self, request: LLMRequest) -> LLMResponse:
        """
        Execute a completion request through the optimal or requested provider.
        """
        provider_name = "omniroute" # Default to omniroute
        provider = self.providers.get(provider_name)
        
        if not provider:
            raise LLMUnavailableError(f"Provider {provider_name} not found.")

        logger.info("llm.request_started", provider=provider.name, task_type=request.task_type.value)
        
        try:
            # For phase 0, basic retry/fallback is mocked or absent
            response = await provider.complete(request)
            logger.info("llm.request_completed", 
                        provider=provider.name, 
                        latency_ms=response.latency_ms,
                        input_tokens=response.input_tokens,
                        output_tokens=response.output_tokens)
            return response
        except LLMUnavailableError as e:
            logger.error("llm.provider_error", provider=provider.name, error=str(e))
            raise
