import time
import httpx
from app.modules.threat_intel.providers.base import BaseTIProvider
from app.modules.threat_intel.schemas import TIProviderResponse

class AbuseIPDBProvider(BaseTIProvider):
    provider_name = "AbuseIPDB"
    provider_version = "v2"
    weight = 0.9

    async def lookup_ipv4(self, ip: str) -> TIProviderResponse:
        start_time = time.time()
        if not self.configured:
            return self._build_error_response(start_time, "NOT_CONFIGURED")
            
        url = "https://api.abuseipdb.com/api/v2/check"
        headers = {
            "Key": self.api_key,
            "Accept": "application/json"
        }
        params = {"ipAddress": ip, "maxAgeInDays": 90}
        
        try:
            resp = await self._http_get(url, headers, params)  # type: ignore
            data = resp.json().get("data", {})
            score = data.get("abuseConfidenceScore", 0)
            confidence = score / 100.0
            
            return self._build_success_response(
                start_time=start_time,
                confidence=confidence,
                raw=data,
                normalized={"abuse_confidence_score": score, "total_reports": data.get("totalReports", 0)}
            )
        except httpx.HTTPStatusError as e:
            return self._build_error_response(start_time, f"HTTP_{e.response.status_code}")
        except Exception as e:
            return self._build_error_response(start_time, str(e))

    async def lookup_domain(self, domain: str) -> TIProviderResponse:
        start_time = time.time()
        return self._build_error_response(start_time, "NOT_SUPPORTED")

    async def lookup_hash(self, file_hash: str) -> TIProviderResponse:
        start_time = time.time()
        return self._build_error_response(start_time, "NOT_SUPPORTED")
