import uuid
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.schemas import APIResponse
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.modules.incidents.schemas import IncidentCreate, IncidentUpdate, IncidentResponse, IncidentListResponse
from app.modules.incidents.service import IncidentService

router = APIRouter(prefix="/incidents", tags=["Incidents"])

@router.get("", response_model=APIResponse[IncidentListResponse])
async def list_incidents(
    page: int = 1,
    page_size: int = 20,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = IncidentService(session)
    items, total = await service.list_incidents(
        organization_id=current_user.organization_id,
        page=page,
        page_size=page_size
    )
    
    return APIResponse(
        success=True,
        data=IncidentListResponse(
            items=[IncidentResponse.model_validate(item, from_attributes=True) for item in items],
            total=total,
            page=page,
            page_size=page_size,
            has_next=(page * page_size) < total
        )
    )

@router.post("", response_model=APIResponse[IncidentResponse])
async def create_incident(
    request: Request,
    payload: IncidentCreate,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    
    service = IncidentService(session)
    incident = await service.create_incident(
        incident_in=payload,
        organization_id=current_user.organization_id,
        user_id=current_user.id,
        ip_address=ip_address,
        user_agent=user_agent
    )
    
    return APIResponse(
        success=True,
        message="Incident created successfully",
        data=IncidentResponse.model_validate(incident, from_attributes=True)
    )

@router.get("/{incident_id}", response_model=APIResponse[IncidentResponse])
async def get_incident(
    incident_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = IncidentService(session)
    incident = await service.get_incident(
        incident_id=incident_id,
        organization_id=current_user.organization_id
    )
    
    return APIResponse(
        success=True,
        data=IncidentResponse.model_validate(incident, from_attributes=True)
    )

@router.patch("/{incident_id}", response_model=APIResponse[IncidentResponse])
async def update_incident(
    request: Request,
    incident_id: uuid.UUID,
    payload: IncidentUpdate,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    
    service = IncidentService(session)
    incident = await service.update_incident(
        incident_id=incident_id,
        incident_update=payload,
        organization_id=current_user.organization_id,
        user_id=current_user.id,
        ip_address=ip_address,
        user_agent=user_agent
    )
    
    return APIResponse(
        success=True,
        message="Incident updated successfully",
        data=IncidentResponse.model_validate(incident, from_attributes=True)
    )
