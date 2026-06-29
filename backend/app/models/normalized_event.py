import uuid
from datetime import datetime
from sqlalchemy import String, ForeignKey, Text, Index
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import DateTime
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import Base

class NormalizedEvent(Base):
    __tablename__ = "normalized_events"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    incident_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("incidents.id"), nullable=False)
    investigation_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("investigations.id"), nullable=False)
    
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    
    # ECS-inspired fields
    event_provider: Mapped[str | None] = mapped_column(String(255), nullable=True)
    event_action: Mapped[str | None] = mapped_column(String(255), nullable=True)
    
    source_ip: Mapped[str | None] = mapped_column(String(50), nullable=True)
    destination_ip: Mapped[str | None] = mapped_column(String(50), nullable=True)
    
    user_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    host_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    
    raw_message: Mapped[str] = mapped_column(Text, nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        Index('ix_normalized_events_org_inc_inv', 'organization_id', 'incident_id', 'investigation_id'),
        Index('ix_normalized_events_timestamp', 'timestamp'),
    )
