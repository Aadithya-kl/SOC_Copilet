import uuid
import json
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.investigation import InvestigationState
from app.modules.timeline.engine import TimelineEngine
from app.models.correlation import CorrelationGroup

class ContextBuilder:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def build_context(self, investigation_id: uuid.UUID) -> Dict[str, Any]:
        """
        Retrieves deterministic artifacts (Summary, Timeline, Correlation Groups)
        and formats them into strings for prompt injection.
        """
        # Summary
        stmt = select(InvestigationState).where(InvestigationState.id == investigation_id)
        inv = (await self.session.execute(stmt)).scalars().first()
        summary = inv.investigation_summary if inv and inv.investigation_summary else {}
        
        # Timeline
        timeline_engine = TimelineEngine(self.session)
        timeline_raw = await timeline_engine.build_timeline(investigation_id)
        
        # Correlation Groups
        corr_stmt = select(CorrelationGroup).where(CorrelationGroup.investigation_id == investigation_id)
        groups = (await self.session.execute(corr_stmt)).scalars().all()
        
        # Sanitization & Truncation (budget enforcement)
        # To strictly enforce token budget, we truncate timelines to the most recent/important 1000 items
        timeline_truncated = timeline_raw[-1000:] if len(timeline_raw) > 1000 else timeline_raw
        
        groups_raw = []
        for g in groups:
            groups_raw.append({
                "id": str(g.id),
                "score": g.correlation_score,
                "confidence": g.confidence,
                "explanation": g.explanation,
                "factors": g.contributing_factors
            })
            
        groups_truncated = groups_raw[:100] if len(groups_raw) > 100 else groups_raw
        
        return {
            "summary": json.dumps(summary, indent=2),
            "timeline": json.dumps(timeline_truncated, indent=2),
            "correlation_groups": json.dumps(groups_truncated, indent=2)
        }
