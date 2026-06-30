import time
import httpx
from app.modules.threat_intel.providers.base import BaseTIProvider
from app.modules.threat_intel.schemas import TIProviderResponse

class PhishTankProvider(BaseTIProvider):
    provider_name = "PhishTank"
    provider_version = "v1"
    weight = 0.80

    async def lookup_ipv4(self, ip: str) -> TIProviderResponse:
        start_time = time.time()
        return self._build_error_response(start_time, "NOT_SUPPORTED")

    async def lookup_domain(self, domain: str) -> TIProviderResponse:
        start_time = time.time()
        url = "https://checkurl.phishtank.com/checkurl/"
        data = {
            "url": domain, # Phishtank expects URL, but checking domain might hit
            "format": "json"
        }
        if self.configured:
            data["app_key"] = self.api_key  # type: ignore

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(url, data=data)
                resp.raise_for_status()
                result = resp.json()

            results = result.get("results", {})
            in_database = results.get("in_database", False)
            valid = results.get("valid", False)
            
            confidence = 1.0 if (in_database and valid) else 0.0
            
            return self._build_success_response(
                start_time=start_time,
                confidence=confidence,
                raw=result,
                normalized={"in_database": in_database, "valid_phish": valid}
            )
        except httpx.HTTPStatusError as e:
            return self._build_error_response(start_time, f"HTTP_{e.response.status_code}")
        except Exception as e:
            return self._build_error_response(start_time, str(e))

    async def lookup_hash(self, file_hash: str) -> TIProviderResponse:
        start_time = time.time()
        return self._build_error_response(start_time, "NOT_SUPPORTED")
