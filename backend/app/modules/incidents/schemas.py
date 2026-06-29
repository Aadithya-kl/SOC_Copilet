from pydantic import BaseModel
from typing import Optional
import uuid
from datetime import datetime

class IncidentCreate(BaseModel):
    title: str
    description: str
    severity: str = "medium"
    status: str = "new"
    assigned_to_id: Optional[uuid.UUID] = None

class IncidentUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    severity: Optional[str] = None
    status: Optional[str] = None
    assigned_to_id: Optional[uuid.UUID] = None

class IncidentResponse(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    title: str
    description: str
    severity: str
    status: str
    created_by_id: Optional[uuid.UUID] = None
    assigned_to_id: Optional[uuid.UUID] = None
    created_at: datetime
    updated_at: datetime

class IncidentListResponse(BaseModel):
    items: list[IncidentResponse]
    total: int
    page: int
    page_size: int
    has_next: bool
