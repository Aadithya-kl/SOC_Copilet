import uuid
from datetime import datetime
from sqlalchemy import String, ForeignKey, JSON, Integer
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import DateTime
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import Base

class InvestigationState(Base):
    __tablename__ = "investigations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False, index=True)
    incident_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("incidents.id"), nullable=False, index=True)
    file_record_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("incident_files.id"), nullable=False, index=True)
    
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="queued") # queued, parsing, normalizing, extracting, completed, failed
    
    # Statistics
    events_processed: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    iocs_extracted: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    
    # Metadata
    metadata_json: Mapped[dict | None] = mapped_column(JSON, nullable=True) # E.g., parse speed, memory usage
    error_message: Mapped[str | None] = mapped_column(String, nullable=True)
    
    # Summary JSON populated after deterministic correlation phase
    investigation_summary: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
