import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, ConfigDict
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.evidence import Evidence
from app.models.threat_intel import ThreatIntelligence

router = APIRouter(tags=["Evidence"])

class EvidenceResponse(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    incident_id: uuid.UUID
    investigation_id: uuid.UUID
    source_event_id: Optional[uuid.UUID]
    ioc_id: Optional[uuid.UUID]
    mitre_technique_id: Optional[str]
    confidence: str
    description: Optional[str]
    
    model_config = ConfigDict(from_attributes=True)

class ThreatIntelResponse(BaseModel):
    id: uuid.UUID
    ioc_id: uuid.UUID
    provider_name: str
    confidence_score: float
    weighted_confidence: Optional[float]
    raw_response: Optional[dict]
    normalized_response: Optional[dict]
    error_reason: Optional[str]

    model_config = ConfigDict(from_attributes=True)

@router.get("/investigations/{investigation_id}/evidence", response_model=List[EvidenceResponse])
async def get_evidence_for_investigation(
    investigation_id: uuid.UUID,
    confidence: Optional[str] = Query(None),
    mitre_technique_id: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    stmt = select(Evidence).where(
        Evidence.investigation_id == investigation_id,
        Evidence.organization_id == current_user.organization_id
    )
    
    if confidence:
        stmt = stmt.where(Evidence.confidence == confidence)
    if mitre_technique_id:
        stmt = stmt.where(Evidence.mitre_technique_id == mitre_technique_id)
        
    result = await db.execute(stmt)
    return result.scalars().all()

@router.get("/iocs/{ioc_id}/threat-intel", response_model=List[ThreatIntelResponse])
async def get_threat_intel_for_ioc(
    ioc_id: uuid.UUID,
    provider: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    stmt = select(ThreatIntelligence).where(ThreatIntelligence.ioc_id == ioc_id)
    if provider:
        stmt = stmt.where(ThreatIntelligence.provider_name == provider)
        
    result = await db.execute(stmt)
    return result.scalars().all()
