import pytest
import respx
from httpx import Response
from app.modules.threat_intel.providers.virustotal import VirusTotalProvider
from app.modules.threat_intel.providers.phishtank import PhishTankProvider

@pytest.mark.asyncio
@respx.mock
async def test_virustotal_ipv4():
    provider = VirusTotalProvider(api_key="test_key")
    
    respx.get("https://www.virustotal.com/api/v3/ip_addresses/8.8.8.8").mock(return_value=Response(200, json={
        "data": {
            "attributes": {
                "last_analysis_stats": {
                    "malicious": 5,
                    "suspicious": 2,
                    "harmless": 80,
                    "undetected": 10
                }
            }
        }
    }))
    
    result = await provider.lookup_ipv4("8.8.8.8")
    assert result.confidence > 0.0
    assert result.provider_name == "VirusTotal"
    assert result.normalized_response["malicious"] == 5
    assert result.normalized_response["suspicious"] == 2

@pytest.mark.asyncio
@respx.mock
async def test_phishtank_domain():
    provider = PhishTankProvider(api_key="test_key")
    
    respx.post("https://checkurl.phishtank.com/checkurl/").mock(return_value=Response(200, json={
        "results": {
            "in_database": True,
            "valid": True
        }
    }))
    
    result = await provider.lookup_domain("http://evil.com")
    assert result.confidence == 1.0
    assert result.normalized_response["in_database"] is True
