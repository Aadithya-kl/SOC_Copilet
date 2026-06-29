import time
import httpx
from typing import Any
from app.llm.providers.base import LLMProvider
from app.llm.schemas import LLMRequest, LLMResponse, ProviderHealth
from app.core.exceptions import LLMUnavailableError

class OmniRouteProvider(LLMProvider):
    def __init__(self, base_url: str = "http://localhost:8000/v1", api_key: str = "dummy"):
        self.base_url = base_url
        self.api_key = api_key
        self._client = httpx.AsyncClient(base_url=self.base_url, headers={"Authorization": f"Bearer {self.api_key}"})

    @property
    def name(self) -> str:
        return "omniroute"

    async def complete(self, request: LLMRequest) -> LLMResponse:
        start_time = time.time()
        
        # Format messages for OmniRoute (assuming OpenAI compat format)
        payload = {
            "model": request.model or "default-model",
            "messages": [{"role": m.role.value, "content": m.content} for m in request.messages],
            "max_tokens": request.max_tokens,
            "temperature": request.temperature,
        }
        
        try:
            resp = await self._client.post("/chat/completions", json=payload, timeout=request.timeout_seconds)
            resp.raise_for_status()
            data = resp.json()
            
            content = data["choices"][0]["message"]["content"]
            usage = data.get("usage", {})
            
            latency_ms = int((time.time() - start_time) * 1000)
            
            return LLMResponse(
                content=content,
                model_used=data.get("model", request.model),
                provider_used=self.name,
                input_tokens=usage.get("prompt_tokens", 0),
                output_tokens=usage.get("completion_tokens", 0),
                latency_ms=latency_ms
            )
        except httpx.HTTPError as e:
            raise LLMUnavailableError(f"OmniRoute request failed: {str(e)}")

    async def health_check(self) -> ProviderHealth:
        start_time = time.time()
        try:
            # Assuming OmniRoute has a /models endpoint for health check
            resp = await self._client.get("/models", timeout=5.0)
            resp.raise_for_status()
            latency_ms = int((time.time() - start_time) * 1000)
            return ProviderHealth(status="ok", latency_ms=latency_ms)
        except Exception as e:
            return ProviderHealth(status="error", error=str(e))
