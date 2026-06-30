import uuid
from typing import List, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.normalized_event import NormalizedEvent
from app.models.ioc import IOC
from app.models.evidence import Evidence
from app.models.correlation import CorrelationGroup, CorrelationEvidence
from app.models.graph import GraphNode
from app.modules.graph.repository import PostgresGraphAdapter

class RelationshipBuilder:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = PostgresGraphAdapter(session)
        
    async def _get_or_create_nodes(self, investigation_id: uuid.UUID, nodes_data: List[Tuple[str, str]]) -> Dict[Tuple[str, str], uuid.UUID]:
        """
        Takes a list of (node_type, node_value) and returns a dict mapping them to GraphNode IDs.
        Since we want to bulk insert/select efficiently.
        """
        if not nodes_data:
            return {}
            
        unique_nodes = list(set(nodes_data))
        
        # Prepare to insert
        nodes_to_insert = []
        for n_type, n_val in unique_nodes:
            nodes_to_insert.append({
                "id": uuid.uuid4(),
                "investigation_id": investigation_id,
                "node_type": n_type,
                "node_value": n_val,
                "properties": {}
            })
            
        await self.repo.add_nodes(nodes_to_insert)
        
        # Now read them back to get IDs
        # To avoid massive IN clauses, we just fetch all nodes for this investigation and type matching.
        types = list(set(n[0] for n in unique_nodes))
        stmt = select(GraphNode).where(
            GraphNode.investigation_id == investigation_id,
            GraphNode.node_type.in_(types)
        )
        res = await self.session.execute(stmt)
        
        node_map = {}
        for n in res.scalars().all():
            node_map[(n.node_type, n.node_value)] = n.id
            
        return node_map

    async def build_projection(self, investigation_id: uuid.UUID):
        """
        Projects normalized events, IOCs, and evidence into the graph.
        """
        # Fetch events
        events_stmt = select(NormalizedEvent).where(NormalizedEvent.investigation_id == investigation_id)
        events = (await self.session.execute(events_stmt)).scalars().all()
        
        # Fetch IOCs
        iocs_stmt = select(IOC).where(IOC.investigation_id == investigation_id)
        iocs = (await self.session.execute(iocs_stmt)).scalars().all()
        
        nodes_needed = []
        
        # Build node requirements
        for ev in events:
            nodes_needed.append(("Event", str(ev.id)))
            if ev.source_ip:
                nodes_needed.append(("IP Address", ev.source_ip))
            if ev.destination_ip:
                nodes_needed.append(("IP Address", ev.destination_ip))
            if ev.user_name:
                nodes_needed.append(("User", ev.user_name))
            if ev.host_name:
                nodes_needed.append(("Host", ev.host_name))
                
        for ioc in iocs:
            ioc_type_map = {
                "ipv4": "IP Address",
                "domain": "Domain",
                "url": "URL",
                "md5": "File",
                "sha256": "File"
            }
            n_type = ioc_type_map.get(ioc.ioc_type, "IOC")
            nodes_needed.append((n_type, ioc.value))
            
        # Also Evidence (Techniques)
        evidence_stmt = select(Evidence).where(Evidence.investigation_id == investigation_id)
        evidences = (await self.session.execute(evidence_stmt)).scalars().all()
        for e in evidences:
            if e.mitre_technique_id:
                nodes_needed.append(("MITRE Technique", e.mitre_technique_id))
                
        node_map = await self._get_or_create_nodes(investigation_id, nodes_needed)
        
        # Build Edges
        edges = []
        for ev in events:
            ev_node = node_map.get(("Event", str(ev.id)))
            if not ev_node: continue
            
            if ev.source_ip and ("IP Address", ev.source_ip) in node_map:
                edges.append({
                    "id": uuid.uuid4(),
                    "investigation_id": investigation_id,
                    "source_node_id": node_map[("IP Address", ev.source_ip)],
                    "target_node_id": ev_node,
                    "relationship_type": "GENERATED",
                    "confidence": 1.0,
                    "properties": {}
                })
            
            if ev.destination_ip and ("IP Address", ev.destination_ip) in node_map:
                edges.append({
                    "id": uuid.uuid4(),
                    "investigation_id": investigation_id,
                    "source_node_id": ev_node,
                    "target_node_id": node_map[("IP Address", ev.destination_ip)],
                    "relationship_type": "CONNECTED_TO",
                    "confidence": 1.0,
                    "properties": {}
                })
                
            if ev.user_name and ("User", ev.user_name) in node_map:
                edges.append({
                    "id": uuid.uuid4(),
                    "investigation_id": investigation_id,
                    "source_node_id": node_map[("User", ev.user_name)],
                    "target_node_id": ev_node,
                    "relationship_type": "AUTHENTICATED" if ev.event_action and "login" in ev.event_action else "GENERATED",
                    "confidence": 1.0,
                    "properties": {}
                })
                
        for e in evidences:
            if e.mitre_technique_id and ("MITRE Technique", e.mitre_technique_id) in node_map and e.source_event_id:
                ev_node = node_map.get(("Event", str(e.source_event_id)))
                if ev_node:
                    edges.append({
                        "id": uuid.uuid4(),
                        "investigation_id": investigation_id,
                        "source_node_id": ev_node,
                        "target_node_id": node_map[("MITRE Technique", e.mitre_technique_id)],
                        "relationship_type": "USES_TECHNIQUE",
                        "confidence": 1.0 if e.confidence == "high" else 0.5,
                        "properties": {}
                    })
                    
        await self.repo.add_edges(edges)
        await self.session.commit()
