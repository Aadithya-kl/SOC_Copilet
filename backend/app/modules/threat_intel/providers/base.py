from abc import ABC, abstractmethod
import time
from typing import Optional, Dict, Any
from app.modules.threat_intel.schemas import TIProviderResponse
import httpx
from tenacity import AsyncRetrying, stop_after_attempt, wait_exponential

class BaseTIProvider(ABC):
    provider_name: str
    provider_version: str
    weight: float

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.configured = bool(api_key)

    def _build_error_response(self, start_time: float, error_reason: str, confidence: float = 0.0) -> TIProviderResponse:
        return TIProviderResponse(
            provider_name=self.provider_name,
            provider_version=self.provider_version,
            response_time_ms=int((time.time() - start_time) * 1000),
            confidence=confidence,
            error_reason=error_reason,
            raw_response=None,
            normalized_response=None
        )

    def _build_success_response(self, start_time: float, confidence: float, raw: Any, normalized: Any, rate_limit: Optional[int] = None) -> TIProviderResponse:
        return TIProviderResponse(
            provider_name=self.provider_name,
            provider_version=self.provider_version,
            response_time_ms=int((time.time() - start_time) * 1000),
            confidence=confidence,
            rate_limit_remaining=rate_limit,
            raw_response=raw,
            normalized_response=normalized
        )

    async def _http_get(self, url: str, headers: Dict[str, str], params: Dict[str, Any] = None) -> httpx.Response:
        async for attempt in AsyncRetrying(
            stop=stop_after_attempt(3),
            wait=wait_exponential(multiplier=1, min=2, max=10)
        ):
            with attempt:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    response = await client.get(url, headers=headers, params=params)
                    response.raise_for_status()
                    return response
        raise Exception("Max retries exceeded")

    @abstractmethod
    async def lookup_ipv4(self, ip: str) -> TIProviderResponse:
        pass

    @abstractmethod
    async def lookup_domain(self, domain: str) -> TIProviderResponse:
        pass

    @abstractmethod
    async def lookup_hash(self, file_hash: str) -> TIProviderResponse:
        pass
