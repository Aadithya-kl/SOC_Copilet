import uuid
from datetime import datetime
from sqlalchemy import String, ForeignKey, Integer, ARRAY, Text, SmallInteger
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import DateTime
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import Base

class Incident(Base):
    __tablename__ = "incidents"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="pending_upload", index=True)
    severity: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)
    risk_score: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    assigned_to: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)
    created_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    closed_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    analyst_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    tags: Mapped[list[str]] = mapped_column(ARRAY(String(100)), nullable=False, default=list)
    external_ticket_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    source_files_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_events_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    malicious_ioc_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    mitre_technique_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    investigation_started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    investigation_completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    investigation_duration_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)
    pipeline_version: Mapped[str | None] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
