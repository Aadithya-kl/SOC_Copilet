from pydantic import BaseModel, ConfigDict
from typing import Optional, Any

class TIProviderResponse(BaseModel):
    provider_name: str
    provider_version: str
    response_time_ms: int
    confidence: float # 0.0 to 1.0
    weighted_confidence: Optional[float] = None
    rate_limit_remaining: Optional[int] = None
    cache_hit: bool = False
    error_reason: Optional[str] = None
    raw_response: Optional[Any] = None
    normalized_response: Optional[Any] = None

    model_config = ConfigDict(from_attributes=True)
