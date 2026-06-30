import time
import httpx
from app.modules.threat_intel.providers.base import BaseTIProvider
from app.modules.threat_intel.schemas import TIProviderResponse

class URLHausProvider(BaseTIProvider):
    provider_name = "URLHaus"
    provider_version = "v1"
    weight = 0.85

    async def lookup_ipv4(self, ip: str) -> TIProviderResponse:
        start_time = time.time()
        url = "https://urlhaus-api.abuse.ch/v1/host/"
        data = {"host": ip}
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(url, data=data)
                resp.raise_for_status()
                result = resp.json()
                
            if result.get("query_status") == "ok":
                urls = result.get("urls", [])
                confidence = 1.0 if len(urls) > 0 else 0.0
                return self._build_success_response(
                    start_time=start_time,
                    confidence=confidence,
                    raw=result,
                    normalized={"malicious_urls": len(urls)}
                )
            else:
                return self._build_success_response(start_time, 0.0, result, {"malicious_urls": 0})
        except Exception as e:
            return self._build_error_response(start_time, str(e))

    async def lookup_domain(self, domain: str) -> TIProviderResponse:
        start_time = time.time()
        url = "https://urlhaus-api.abuse.ch/v1/host/"
        data = {"host": domain}
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(url, data=data)
                resp.raise_for_status()
                result = resp.json()
                
            if result.get("query_status") == "ok":
                urls = result.get("urls", [])
                confidence = 1.0 if len(urls) > 0 else 0.0
                return self._build_success_response(
                    start_time=start_time,
                    confidence=confidence,
                    raw=result,
                    normalized={"malicious_urls": len(urls)}
                )
            else:
                return self._build_success_response(start_time, 0.0, result, {"malicious_urls": 0})
        except Exception as e:
            return self._build_error_response(start_time, str(e))

    async def lookup_hash(self, file_hash: str) -> TIProviderResponse:
        start_time = time.time()
        url = "https://urlhaus-api.abuse.ch/v1/payload/"
        data = {"md5_hash": file_hash} if len(file_hash) == 32 else {"sha256_hash": file_hash}
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(url, data=data)
                resp.raise_for_status()
                result = resp.json()
                
            if result.get("query_status") == "ok":
                confidence = 1.0
                return self._build_success_response(
                    start_time=start_time,
                    confidence=confidence,
                    raw=result,
                    normalized={"malicious": True}
                )
            else:
                return self._build_success_response(start_time, 0.0, result, {"malicious": False})
        except Exception as e:
            return self._build_error_response(start_time, str(e))
