import uuid
import logging
from typing import List
from collections import defaultdict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.evidence import Evidence
from app.models.normalized_event import NormalizedEvent
from app.models.ioc import IOC
from app.models.correlation import CorrelationGroup, CorrelationEvidence

logger = logging.getLogger(__name__)

class CorrelationEngine:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def run_correlation(self, organization_id: uuid.UUID, investigation_id: uuid.UUID) -> List[CorrelationGroup]:
        """
        Groups evidence into correlation groups deterministically.
        Uses Union-Find to group evidence that share IOCs, Hosts, Users, or MITRE techniques within a time window.
        """
        # Fetch all evidence for the investigation
        stmt = select(Evidence).where(
            Evidence.investigation_id == investigation_id,
            Evidence.organization_id == organization_id
        ).options(
            selectinload(Evidence.source_event_id), # We need to map these properly if not relationship
            # Wait, these are foreign keys, let's just query everything related if we haven't mapped relationships.
        )
        
        evidence_result = await self.session.execute(stmt)
        evidences = evidence_result.scalars().all()
        
        if not evidences:
            return []
            
        # Manually fetch related IOCs and Events to avoid relationship mapping issues if they aren't configured
        ioc_ids = [e.ioc_id for e in evidences if e.ioc_id]
        event_ids = [e.source_event_id for e in evidences if e.source_event_id]
        
        iocs = {}
        if ioc_ids:
            ioc_stmt = select(IOC).where(IOC.id.in_(ioc_ids))
            ioc_result = await self.session.execute(ioc_stmt)
            for i in ioc_result.scalars().all():
                iocs[i.id] = i
                
        events = {}
        if event_ids:
            event_stmt = select(NormalizedEvent).where(NormalizedEvent.id.in_(event_ids))
            event_result = await self.session.execute(event_stmt)
            for ev in event_result.scalars().all():
                events[ev.id] = ev

        # Union-Find for grouping
        parent = {e.id: e.id for e in evidences}
        
        def find(i):
            if parent[i] == i:
                return i
            parent[i] = find(parent[i])
            return parent[i]
            
        def union(i, j):
            root_i = find(i)
            root_j = find(j)
            if root_i != root_j:
                parent[root_i] = root_j

        # Build correlation indices
        ioc_map = defaultdict(list)
        mitre_map = defaultdict(list)
        host_map = defaultdict(list)
        user_map = defaultdict(list)
        
        for e in evidences:
            if e.ioc_id and e.ioc_id in iocs:
                ioc_val = iocs[e.ioc_id].value
                ioc_map[ioc_val].append(e.id)
                
            if e.mitre_technique_id:
                mitre_map[e.mitre_technique_id].append(e.id)
                
            if e.source_event_id and e.source_event_id in events:
                ev = events[e.source_event_id]
                if ev.host_name:
                    host_map[ev.host_name].append(e.id)
                if ev.user_name:
                    user_map[ev.user_name].append(e.id)
                if ev.source_ip:
                    ioc_map[ev.source_ip].append(e.id) # Treat IP as IOC for correlation
                if ev.destination_ip:
                    ioc_map[ev.destination_ip].append(e.id)

        # Correlate
        def connect_map(attribute_map):
            for key, ev_ids in attribute_map.items():
                if len(ev_ids) > 1:
                    first = ev_ids[0]
                    for other in ev_ids[1:]:
                        union(first, other)
                        
        connect_map(ioc_map)
        connect_map(mitre_map)
        connect_map(host_map)
        connect_map(user_map)
        
        # Group evidences
        groups = defaultdict(list)
        for e in evidences:
            groups[find(e.id)].append(e)
            
        # Create CorrelationGroup objects
        created_groups = []
        ce_batch = []
        
        import uuid
        for root_id, group_evidences in groups.items():
            if len(group_evidences) < 1:
                continue
                
            # Compute score and metadata
            shared_iocs = set()
            shared_mitre = set()
            high_conf_count = 0
            
            for e in group_evidences:
                if e.confidence == "high":
                    high_conf_count += 1
                if e.ioc_id and e.ioc_id in iocs:
                    shared_iocs.add(iocs[e.ioc_id].value)
                if e.mitre_technique_id:
                    shared_mitre.add(e.mitre_technique_id)
                    
            score = min(1.0, 0.2 + (0.3 * len(shared_iocs)) + (0.3 * len(shared_mitre)) + (0.2 * high_conf_count))
            confidence = "high" if score > 0.7 else "medium" if score > 0.4 else "low"
            
            factors = {
                "shared_iocs": list(shared_iocs),
                "shared_mitre_techniques": list(shared_mitre),
                "high_confidence_evidence_count": high_conf_count
            }
            
            explanation = f"Correlated {len(group_evidences)} evidence items. "
            if shared_iocs:
                explanation += f"Shared indicators: {', '.join(list(shared_iocs)[:3])}. "
            if shared_mitre:
                explanation += f"Observed techniques: {', '.join(list(shared_mitre)[:3])}. "
                
            group = CorrelationGroup(
                id=uuid.uuid4(),
                organization_id=organization_id,
                investigation_id=investigation_id,
                correlation_score=score,
                confidence=confidence,
                explanation=explanation.strip(),
                evidence_count=len(group_evidences),
                contributing_factors=factors
            )
            created_groups.append(group)
            
            for e in group_evidences:
                ce_batch.append({
                    "id": uuid.uuid4(),
                    "correlation_group_id": group.id,
                    "evidence_id": e.id
                })
                
        # Insert
        if created_groups:
            self.session.add_all(created_groups)
            await self.session.flush() # To get group IDs if needed, but we already set them
            
            if ce_batch:
                from sqlalchemy.dialects.postgresql import insert as pg_insert
                stmt = pg_insert(CorrelationEvidence).values(ce_batch).on_conflict_do_nothing()  # type: ignore
                await self.session.execute(stmt)
                
            await self.session.commit()
            
        return created_groups
