import asyncio
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import timedelta
import redis.asyncio as redis
from cachetools import TTLCache

from app.core.config import settings
from app.modules.threat_intel.providers import (
    VirusTotalProvider,
    AbuseIPDBProvider,
    URLHausProvider,
    AlienVaultOTXProvider,
    PhishTankProvider
)
from app.modules.threat_intel.schemas import TIProviderResponse

logger = logging.getLogger(__name__)

class TIAggregator:
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        # Memory cache: max 1000 items, 5 minutes TTL
        self.mem_cache = TTLCache(maxsize=1000, ttl=300)
        
        self.providers = [
            VirusTotalProvider(api_key=settings.VIRUSTOTAL_API_KEY if hasattr(settings, 'VIRUSTOTAL_API_KEY') else None),
            AbuseIPDBProvider(api_key=settings.ABUSEIPDB_API_KEY if hasattr(settings, 'ABUSEIPDB_API_KEY') else None),
            AlienVaultOTXProvider(api_key=settings.OTX_API_KEY if hasattr(settings, 'OTX_API_KEY') else None),
            URLHausProvider(),
            PhishTankProvider(api_key=settings.PHISHTANK_API_KEY if hasattr(settings, 'PHISHTANK_API_KEY') else None),
        ]
        
        # Bounded concurrency
        self.semaphore = asyncio.Semaphore(10)

    async def _check_cache(self, cache_key: str) -> Optional[List[TIProviderResponse]]:
        # 1. Memory cache
        if cache_key in self.mem_cache:
            return self.mem_cache[cache_key]
            
        # 2. Redis cache
        cached = await self.redis.get(cache_key)
        if cached:
            try:
                data = json.loads(cached)
                responses = [TIProviderResponse.model_validate(item) for item in data]
                self.mem_cache[cache_key] = responses
                # Set cache_hit to True for callers
                for r in responses:
                    r.cache_hit = True
                return responses
            except Exception as e:
                logger.error(f"Failed to load TI cache from redis: {e}")
                
        return None

    async def _set_cache(self, cache_key: str, responses: List[TIProviderResponse]):
        self.mem_cache[cache_key] = responses
        data = [r.model_dump() for r in responses]
        await self.redis.setex(cache_key, timedelta(hours=24), json.dumps(data))

    async def _run_provider(self, provider, method_name: str, value: str) -> TIProviderResponse:
        async with self.semaphore:
            try:
                func = getattr(provider, method_name)
                # Ensure it executes with a timeout
                async with asyncio.timeout(15.0):
                    return await func(value)
            except asyncio.TimeoutError:
                return provider._build_error_response(time.time(), "TIMEOUT")
            except Exception as e:
                logger.error(f"Provider {provider.provider_name} failed: {e}")
                return provider._build_error_response(time.time(), str(e))

    async def enrich_ioc(self, ioc_type: str, ioc_value: str) -> List[TIProviderResponse]:
        cache_key = f"ti:{ioc_type}:{ioc_value}"
        
        cached = await self._check_cache(cache_key)
        if cached:
            return cached
            
        method_map = {
            "ipv4": "lookup_ipv4",
            "ipv6": "lookup_ipv6", # Wait, base provider doesn't have lookup_ipv6 yet, let's map to ipv4 or skip
            "domain": "lookup_domain",
            "url": "lookup_domain", # Depending on provider, url might use domain lookup
            "md5": "lookup_hash",
            "sha1": "lookup_hash",
            "sha256": "lookup_hash"
        }
        
        method_name = method_map.get(ioc_type)
        if not method_name:
            return []
            
        tasks = []
        for provider in self.providers:
            if hasattr(provider, method_name):
                tasks.append(self._run_provider(provider, method_name, ioc_value))
                
        if not tasks:
            return []
            
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        valid_results = []
        providers_with_method = [p for p in self.providers if hasattr(p, method_name)]
        for r, provider in zip(results, providers_with_method):
            if isinstance(r, TIProviderResponse):
                r.confidence = float(r.confidence)
                r.weighted_confidence = r.confidence * provider.weight
                valid_results.append(r)
                
        await self._set_cache(cache_key, valid_results)
        return valid_results
