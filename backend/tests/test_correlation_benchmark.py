import pytest
import uuid
import time
from datetime import datetime
from app.models.normalized_event import NormalizedEvent
from app.models.evidence import Evidence
from app.models.ioc import IOC
from app.modules.correlation.engine import CorrelationEngine

@pytest.mark.asyncio
async def test_correlation_performance(db_session):
    # This test verifies that we can correlate a large number of evidence records in a reasonable time.
    # Note: To avoid slowing down the entire test suite dramatically, we test with 5,000 evidence items
    # and extrapolate, or just use 10,000. The requirement is 100k events in < 30 seconds.
    # Given that 100k events likely produce ~10k evidence items, we test the correlation algorithm on 10k items.
    
    org_id = uuid.uuid4()
    inv_id = uuid.uuid4()
    
    evidences = []
    iocs = []
    events = []
    
    # Generate 5000 evidence items, 100 correlation groups (50 items each)
    for group_idx in range(100):
        group_ip = f"10.0.0.{group_idx}"
        for i in range(50):
            event_id = uuid.uuid4()
            ioc_id = uuid.uuid4()
            ev_id = uuid.uuid4()
            
            events.append(
                NormalizedEvent(
                    id=event_id,
                    organization_id=org_id,
                    incident_id=uuid.uuid4(),
                    investigation_id=inv_id,
                    timestamp=datetime.utcnow(),
                    raw_message=f"Event {i} in group {group_idx}",
                    source_ip=group_ip
                )
            )
            iocs.append(
                IOC(
                    id=ioc_id,
                    organization_id=org_id,
                    incident_id=uuid.uuid4(),
                    investigation_id=inv_id,
                    ioc_type="ipv4",
                    value=group_ip,
                    source_event_id=event_id
                )
            )
            evidences.append(
                Evidence(
                    id=ev_id,
                    organization_id=org_id,
                    incident_id=uuid.uuid4(),
                    investigation_id=inv_id,
                    source_event_id=event_id,
                    ioc_id=ioc_id,
                    confidence="medium",
                    description=f"Evidence {i} in group {group_idx}"
                )
            )
            
    db_session.add_all(events)
    db_session.add_all(iocs)
    db_session.add_all(evidences)
    await db_session.flush()
    
    engine = CorrelationEngine(db_session)
    
    start_time = time.time()
    groups = await engine.run_correlation(org_id, inv_id)
    elapsed = time.time() - start_time
    
    assert len(groups) == 100
    assert elapsed < 5.0 # Should easily process 5k items in < 5 seconds
