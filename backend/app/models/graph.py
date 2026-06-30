import uuid
from datetime import datetime
from sqlalchemy import String, ForeignKey, JSON, Index, Float, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import DateTime
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import Base

class GraphNode(Base):
    __tablename__ = "graph_nodes"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    investigation_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("investigations.id", ondelete="CASCADE"), nullable=False, index=True)
    
    node_type: Mapped[str] = mapped_column(String(50), nullable=False) # e.g. "Incident", "Investigation", "Event", "IOC", "Host", "User", "Process", "File", "Domain", "URL", "IP Address", "MITRE Technique"
    node_value: Mapped[str] = mapped_column(String(500), nullable=False) # e.g. "192.168.1.1", "T1110"
    
    properties: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        Index('ix_graph_nodes_inv_type', 'investigation_id', 'node_type'),
        # Ensure we only have one node of a specific type/value per investigation
        UniqueConstraint('investigation_id', 'node_type', 'node_value', name='uix_graph_node_inv_type_val')
    )

class GraphEdge(Base):
    __tablename__ = "graph_edges"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    investigation_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("investigations.id", ondelete="CASCADE"), nullable=False, index=True)
    
    source_node_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("graph_nodes.id", ondelete="CASCADE"), nullable=False, index=True)
    target_node_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("graph_nodes.id", ondelete="CASCADE"), nullable=False, index=True)
    
    relationship_type: Mapped[str] = mapped_column(String(50), nullable=False) # e.g. "CONNECTED_TO", "GENERATED"
    
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    properties: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        Index('ix_graph_edges_source', 'source_node_id'),
        Index('ix_graph_edges_target', 'target_node_id'),
        UniqueConstraint('source_node_id', 'target_node_id', 'relationship_type', name='uix_graph_edge_src_tgt_type')
    )
