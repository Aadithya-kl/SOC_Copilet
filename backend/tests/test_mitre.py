from datetime import datetime
from app.modules.mitre.engine import MitreMappingEngine
from app.models.normalized_event import NormalizedEvent

def test_mitre_engine_bruteforce():
    engine = MitreMappingEngine() # will load from backend/rules
    event = NormalizedEvent(
        event_action="login_failed",
        event_provider="sshd",
        timestamp=datetime.utcnow(),
        raw_message="failed password for root"
    )
    
    matches = engine.evaluate_event(event)
    assert len(matches) > 0
    assert matches[0]["technique_id"] == "T1110"

def test_mitre_engine_powershell():
    engine = MitreMappingEngine()
    event = NormalizedEvent(
        timestamp=datetime.utcnow(),
        raw_message="powershell.exe -enc JABzAD0ATgBlAHcALQBPAGIAagBlAGMAdAAgAEkATwAuAE0AZQBtAG8AcgB5AFMAdAByAGUAYQBtACgAWwBDAG8AbgB2AGUAcgB0AF0AOgA6AEYAcgBvAG0AQgBhAHMAZQA2ADQAUwB0AHIAaQBuAGcAKAAiAEgA..."
    )
    
    matches = engine.evaluate_event(event)
    assert len(matches) > 0
    assert matches[0]["technique_id"] == "T1059"
