import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, ConfigDict
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.correlation import CorrelationGroup

router = APIRouter(prefix="/correlation", tags=["Correlation"])

class CorrelationGroupResponse(BaseModel):
    id: uuid.UUID
    investigation_id: uuid.UUID
    correlation_score: float
    confidence: str
    explanation: str
    evidence_count: int
    contributing_factors: dict
    
    model_config = ConfigDict(from_attributes=True)

@router.get("/groups", response_model=List[CorrelationGroupResponse])
async def get_correlation_groups(
    investigation_id: uuid.UUID,
    confidence: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    stmt = select(CorrelationGroup).where(
        CorrelationGroup.investigation_id == investigation_id,
        CorrelationGroup.organization_id == current_user.organization_id
    )
    if confidence:
        stmt = stmt.where(CorrelationGroup.confidence == confidence)
        
    result = await db.execute(stmt)
    return result.scalars().all()
