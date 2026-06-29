import uuid
from datetime import datetime
from sqlalchemy import String, Boolean, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import DateTime
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    username: Mapped[str] = mapped_column(String(100), nullable=False)
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True) # NULL for OIDC-only users
    oidc_sub: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    oidc_provider: Mapped[str | None] = mapped_column(String(100), nullable=True)
    role: Mapped[str] = mapped_column(String(50), nullable=False, default="analyst")
    display_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    failed_login_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    locked_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (
        UniqueConstraint('organization_id', 'email', name='uq_org_email'),
    )
