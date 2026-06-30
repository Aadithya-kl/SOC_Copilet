from abc import ABC, abstractmethod
from typing import List, Dict, Any
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.models.graph import GraphNode, GraphEdge

class GraphRepository(ABC):
    @abstractmethod
    async def add_nodes(self, nodes: List[Dict[str, Any]]):
        pass

    @abstractmethod
    async def add_edges(self, edges: List[Dict[str, Any]]):
        pass
        
    @abstractmethod
    async def get_neighbors(self, investigation_id: uuid.UUID, node_value: str, depth: int = 1) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def export_graph(self, investigation_id: uuid.UUID) -> Dict[str, Any]:
        pass


class PostgresGraphAdapter(GraphRepository):
    def __init__(self, session: AsyncSession):
        self.session = session
        
    async def add_nodes(self, nodes: List[Dict[str, Any]]):
        if not nodes:
            return
        stmt = pg_insert(GraphNode).values(nodes).on_conflict_do_nothing(
            index_elements=['investigation_id', 'node_type', 'node_value']
        )
        await self.session.execute(stmt)

    async def add_edges(self, edges: List[Dict[str, Any]]):
        if not edges:
            return
        stmt = pg_insert(GraphEdge).values(edges).on_conflict_do_nothing(
            index_elements=['source_node_id', 'target_node_id', 'relationship_type']
        )
        await self.session.execute(stmt)

    async def get_neighbors(self, investigation_id: uuid.UUID, node_value: str, depth: int = 1) -> Dict[str, Any]:
        # Simple immediate neighbors for now
        stmt = select(GraphNode).where(GraphNode.investigation_id == investigation_id, GraphNode.node_value == node_value)
        result = await self.session.execute(stmt)
        node = result.scalars().first()
        if not node:
            return {"nodes": [], "edges": []}
            
        edge_stmt = select(GraphEdge).where(
            GraphEdge.investigation_id == investigation_id,
            (GraphEdge.source_node_id == node.id) | (GraphEdge.target_node_id == node.id)
        )
        edges_res = await self.session.execute(edge_stmt)
        edges = edges_res.scalars().all()
        
        node_ids = set()
        for e in edges:
            node_ids.add(e.source_node_id)
            node_ids.add(e.target_node_id)
            
        nodes_stmt = select(GraphNode).where(GraphNode.id.in_(list(node_ids)))
        nodes_res = await self.session.execute(nodes_stmt)
        nodes = nodes_res.scalars().all()
        
        return {
            "nodes": [{"id": str(n.id), "type": n.node_type, "value": n.node_value, "properties": n.properties} for n in nodes],
            "edges": [{"source": str(e.source_node_id), "target": str(e.target_node_id), "type": e.relationship_type, "confidence": e.confidence} for e in edges]
        }
        
    async def export_graph(self, investigation_id: uuid.UUID) -> Dict[str, Any]:
        nodes_stmt = select(GraphNode).where(GraphNode.investigation_id == investigation_id)
        edges_stmt = select(GraphEdge).where(GraphEdge.investigation_id == investigation_id)
        
        n_res = await self.session.execute(nodes_stmt)
        e_res = await self.session.execute(edges_stmt)
        
        return {
            "nodes": [{"id": str(n.id), "type": n.node_type, "value": n.node_value, "properties": n.properties} for n in n_res.scalars().all()],
            "edges": [{"source": str(e.source_node_id), "target": str(e.target_node_id), "type": e.relationship_type, "confidence": e.confidence} for e in e_res.scalars().all()]
        }
