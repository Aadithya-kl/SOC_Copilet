import uuid
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.normalized_event import NormalizedEvent
from app.models.correlation import CorrelationGroup
from app.models.investigation import InvestigationState

class TimelineEngine:
    def __init__(self, session: AsyncSession):
        self.session = session
        
    async def build_timeline(self, investigation_id: uuid.UUID) -> List[Dict[str, Any]]:
        # Fetch events ordered by timestamp
        stmt = select(NormalizedEvent).where(
            NormalizedEvent.investigation_id == investigation_id
        ).order_by(NormalizedEvent.timestamp.asc())
        
        events = (await self.session.execute(stmt)).scalars().all()
        
        timeline = []
        last_event = None
        
        for ev in events:
            # Collapse duplicates: same action, provider, user, host within 1 second
            if last_event:
                time_diff = (ev.timestamp - last_event.timestamp).total_seconds()
                if time_diff < 1.0 and \
                   ev.event_action == last_event.event_action and \
                   ev.user_name == last_event.user_name and \
                   ev.host_name == last_event.host_name:
                    
                    timeline[-1]["count"] += 1
                    timeline[-1]["end_time"] = ev.timestamp.isoformat()
                    continue
                    
            timeline_event = {
                "id": str(ev.id),
                "timestamp": ev.timestamp.isoformat(),
                "end_time": ev.timestamp.isoformat(),
                "action": ev.event_action,
                "provider": ev.event_provider,
                "user": ev.user_name,
                "host": ev.host_name,
                "message": ev.raw_message,
                "count": 1
            }
            timeline.append(timeline_event)
            last_event = ev
            
        return timeline

    async def generate_summary(self, investigation_id: uuid.UUID) -> Dict[str, Any]:
        # Simple counts for summary
        from sqlalchemy import func
        from app.models.ioc import IOC
        from app.models.evidence import Evidence
        
        # Events Count
        evt_stmt = select(func.count(NormalizedEvent.id)).where(NormalizedEvent.investigation_id == investigation_id)
        evt_count = (await self.session.execute(evt_stmt)).scalar()
        
        # IOC Count
        ioc_stmt = select(func.count(IOC.id)).where(IOC.investigation_id == investigation_id)
        ioc_count = (await self.session.execute(ioc_stmt)).scalar()
        
        # Evidence Count
        evi_stmt = select(func.count(Evidence.id)).where(Evidence.investigation_id == investigation_id)
        evi_count = (await self.session.execute(evi_stmt)).scalar()
        
        # Correlation Groups
        corr_stmt = select(func.count(CorrelationGroup.id)).where(CorrelationGroup.investigation_id == investigation_id)
        corr_count = (await self.session.execute(corr_stmt)).scalar()
        
        # Timeline
        timeline = await self.build_timeline(investigation_id)
        timeline_length = len(timeline)
        
        summary = {
            "events_parsed": evt_count,
            "normalized_events": evt_count,
            "iocs_extracted": ioc_count,
            "threat_matches": evi_count, # Approx
            "mitre_techniques": evi_count, # Approx
            "correlation_groups_count": corr_count,
            "timeline_length": timeline_length,
            "evidence_count": evi_count
        }
        
        # Update InvestigationState
        inv_stmt = select(InvestigationState).where(InvestigationState.id == investigation_id)
        inv = (await self.session.execute(inv_stmt)).scalars().first()
        if inv:
            inv.investigation_summary = summary
            await self.session.commit()
            
        return summary
