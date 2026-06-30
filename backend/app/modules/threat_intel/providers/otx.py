import time
from typing import Optional
import httpx
from app.modules.threat_intel.providers.base import BaseTIProvider
from app.modules.threat_intel.schemas import TIProviderResponse

class AlienVaultOTXProvider(BaseTIProvider):
    provider_name = "AlienVaultOTX"
    provider_version = "v1"
    weight = 0.9

    async def _lookup_indicator(self, indicator_type: str, indicator: str) -> TIProviderResponse:
        start_time = time.time()
        if not self.configured:
            return self._build_error_response(start_time, "NOT_CONFIGURED")
            
        url = f"https://otx.alienvault.com/api/v1/indicators/{indicator_type}/{indicator}/general"
        headers = {"X-OTX-API-KEY": self.api_key}
        
        try:
            resp = await self._http_get(url, headers)  # type: ignore
            data = resp.json()
            pulse_info = data.get("pulse_info", {})
            pulse_count = pulse_info.get("count", 0)
            
            # Simple heuristic: if it's in 2 or more pulses, it's highly suspicious
            confidence = min(1.0, pulse_count / 3.0) if pulse_count > 0 else 0.0
            
            return self._build_success_response(
                start_time=start_time,
                confidence=confidence,
                raw=data,
                normalized={"pulse_count": pulse_count}
            )
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return self._build_success_response(start_time, 0.0, None, {"status": "not_found"})
            return self._build_error_response(start_time, f"HTTP_{e.response.status_code}")
        except Exception as e:
            return self._build_error_response(start_time, str(e))

    async def lookup_ipv4(self, ip: str) -> TIProviderResponse:
        return await self._lookup_indicator("IPv4", ip)

    async def lookup_domain(self, domain: str) -> TIProviderResponse:
        return await self._lookup_indicator("domain", domain)

    async def lookup_hash(self, file_hash: str) -> TIProviderResponse:
        indicator_type = "file"
        return await self._lookup_indicator(indicator_type, file_hash)
