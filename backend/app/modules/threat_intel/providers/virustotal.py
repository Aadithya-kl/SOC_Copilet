import time
from typing import Optional, Dict, Any
import httpx
from app.modules.threat_intel.providers.base import BaseTIProvider
from app.modules.threat_intel.schemas import TIProviderResponse

class VirusTotalProvider(BaseTIProvider):
    provider_name = "VirusTotal"
    provider_version = "v3"
    weight = 1.0

    async def lookup_ipv4(self, ip: str) -> TIProviderResponse:
        start_time = time.time()
        if not self.configured:
            return self._build_error_response(start_time, "NOT_CONFIGURED")
            
        url = f"https://www.virustotal.com/api/v3/ip_addresses/{ip}"
        headers = {"x-apikey": self.api_key}
        
        try:
            resp = await self._http_get(url, headers)  # type: ignore
            data = resp.json()
            stats = data.get("data", {}).get("attributes", {}).get("last_analysis_stats", {})
            malicious = stats.get("malicious", 0)
            suspicious = stats.get("suspicious", 0)
            total = sum(stats.values()) if stats else 1
            confidence = (malicious + (suspicious * 0.5)) / total if total > 0 else 0.0
            
            return self._build_success_response(
                start_time=start_time,
                confidence=min(1.0, confidence),
                raw=data,
                normalized={"malicious": malicious, "suspicious": suspicious, "total": total}
            )
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return self._build_success_response(start_time, 0.0, None, {"status": "not_found"})
            return self._build_error_response(start_time, f"HTTP_{e.response.status_code}")
        except Exception as e:
            return self._build_error_response(start_time, str(e))

    async def lookup_domain(self, domain: str) -> TIProviderResponse:
        start_time = time.time()
        if not self.configured:
            return self._build_error_response(start_time, "NOT_CONFIGURED")
            
        url = f"https://www.virustotal.com/api/v3/domains/{domain}"
        headers = {"x-apikey": self.api_key}
        
        try:
            resp = await self._http_get(url, headers)  # type: ignore
            data = resp.json()
            stats = data.get("data", {}).get("attributes", {}).get("last_analysis_stats", {})
            malicious = stats.get("malicious", 0)
            suspicious = stats.get("suspicious", 0)
            total = sum(stats.values()) if stats else 1
            confidence = (malicious + (suspicious * 0.5)) / total if total > 0 else 0.0
            
            return self._build_success_response(
                start_time=start_time,
                confidence=min(1.0, confidence),
                raw=data,
                normalized={"malicious": malicious, "suspicious": suspicious, "total": total}
            )
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return self._build_success_response(start_time, 0.0, None, {"status": "not_found"})
            return self._build_error_response(start_time, f"HTTP_{e.response.status_code}")
        except Exception as e:
            return self._build_error_response(start_time, str(e))

    async def lookup_hash(self, file_hash: str) -> TIProviderResponse:
        start_time = time.time()
        if not self.configured:
            return self._build_error_response(start_time, "NOT_CONFIGURED")
            
        url = f"https://www.virustotal.com/api/v3/files/{file_hash}"
        headers = {"x-apikey": self.api_key}
        
        try:
            resp = await self._http_get(url, headers)  # type: ignore
            data = resp.json()
            stats = data.get("data", {}).get("attributes", {}).get("last_analysis_stats", {})
            malicious = stats.get("malicious", 0)
            suspicious = stats.get("suspicious", 0)
            total = sum(stats.values()) if stats else 1
            confidence = (malicious + (suspicious * 0.5)) / total if total > 0 else 0.0
            
            return self._build_success_response(
                start_time=start_time,
                confidence=min(1.0, confidence),
                raw=data,
                normalized={"malicious": malicious, "suspicious": suspicious, "total": total}
            )
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return self._build_success_response(start_time, 0.0, None, {"status": "not_found"})
            return self._build_error_response(start_time, f"HTTP_{e.response.status_code}")
        except Exception as e:
            return self._build_error_response(start_time, str(e))
