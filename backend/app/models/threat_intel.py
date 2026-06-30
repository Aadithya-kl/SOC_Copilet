import uuid
from datetime import datetime
from sqlalchemy import String, ForeignKey, JSON, Index, Float
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import DateTime
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import Base

class ThreatIntelligence(Base):
    __tablename__ = "threat_intelligence"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ioc_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("iocs.id"), nullable=False, index=True)
    
    provider_name: Mapped[str] = mapped_column(String(100), nullable=False)
    provider_version: Mapped[str | None] = mapped_column(String(50), nullable=True)
    
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0) # 0.0 to 1.0
    weighted_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    
    raw_response: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    normalized_response: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    
    response_time_ms: Mapped[int | None] = mapped_column(nullable=True)
    rate_limit_remaining: Mapped[int | None] = mapped_column(nullable=True)
    cache_hit: Mapped[bool] = mapped_column(default=False, nullable=False)
    error_reason: Mapped[str | None] = mapped_column(String, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        Index('ix_ti_ioc_provider', 'ioc_id', 'provider_name'),
    )
