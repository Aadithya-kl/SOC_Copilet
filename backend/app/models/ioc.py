import uuid
from datetime import datetime
from sqlalchemy import String, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import DateTime
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import Base

class IOC(Base):
    __tablename__ = "iocs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    incident_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("incidents.id"), nullable=False)
    investigation_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("investigations.id"), nullable=False)
    
    ioc_type: Mapped[str] = mapped_column(String(50), nullable=False) # ipv4, domain, hash, etc.
    value: Mapped[str] = mapped_column(String(2048), nullable=False)
    
    # Store the context from which it was extracted (optional)
    source_event_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("normalized_events.id"), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        Index('ix_iocs_org_inc_inv', 'organization_id', 'incident_id', 'investigation_id'),
        Index('ix_iocs_type_value', 'ioc_type', 'value'),
        Index('ix_iocs_unique_value_per_inv', 'investigation_id', 'ioc_type', 'value', unique=True),
    )
