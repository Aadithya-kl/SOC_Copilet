import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional

from app.core.exceptions import NotFoundError
from app.models.incident import Incident
from app.models.audit_log import AuditLog
from app.modules.incidents.schemas import IncidentCreate, IncidentUpdate

class IncidentService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list_incidents(
        self, 
        organization_id: uuid.UUID, 
        page: int = 1, 
        page_size: int = 20
    ) -> tuple[list[Incident], int]:
        offset = (page - 1) * page_size
        
        query = select(Incident).where(Incident.organization_id == organization_id)
        
        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total = await self.session.scalar(count_query) or 0
        
        # Get items
        items_query = query.order_by(Incident.created_at.desc()).offset(offset).limit(page_size)
        result = await self.session.execute(items_query)
        items = list(result.scalars().all())
        
        return items, total

    async def create_incident(
        self, 
        incident_in: IncidentCreate, 
        organization_id: uuid.UUID, 
        user_id: uuid.UUID,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Incident:
        new_incident = Incident(
            organization_id=organization_id,
            created_by_id=user_id,
            title=incident_in.title,
            description=incident_in.description,
            severity=incident_in.severity,
            status=incident_in.status,
            assigned_to_id=incident_in.assigned_to_id
        )
        self.session.add(new_incident)
        await self.session.flush() # flush to get ID
        
        # Audit
        audit = AuditLog(
            user_id=user_id,
            organization_id=organization_id,
            action="incident.created",
            target_type="Incident",
            target_id=new_incident.id,
            ip_address=ip_address,
            user_agent=user_agent,
            details={"title": new_incident.title}
        )
        self.session.add(audit)
        
        await self.session.commit()
        await self.session.refresh(new_incident)
        
        return new_incident

    async def get_incident(self, incident_id: uuid.UUID, organization_id: uuid.UUID) -> Incident:
        result = await self.session.execute(
            select(Incident).where(
                Incident.id == incident_id, 
                Incident.organization_id == organization_id
            )
        )
        incident = result.scalar_one_or_none()
        
        if not incident:
            raise NotFoundError("Incident not found")
            
        return incident

    async def update_incident(
        self, 
        incident_id: uuid.UUID, 
        incident_update: IncidentUpdate, 
        organization_id: uuid.UUID,
        user_id: uuid.UUID,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Incident:
        incident = await self.get_incident(incident_id, organization_id)
        
        update_data = incident_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(incident, key, value)
            
        # Audit
        audit = AuditLog(
            user_id=user_id,
            organization_id=organization_id,
            action="incident.updated",
            target_type="Incident",
            target_id=incident.id,
            ip_address=ip_address,
            user_agent=user_agent,
            details={"updated_fields": list(update_data.keys())}
        )
        self.session.add(audit)
        
        await self.session.commit()
        await self.session.refresh(incident)
        
        return incident
