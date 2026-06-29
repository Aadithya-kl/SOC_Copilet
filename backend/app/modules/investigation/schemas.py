from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional
import uuid

class NormalizedEventCreate(BaseModel):
    timestamp: datetime
    event_provider: Optional[str] = None
    event_action: Optional[str] = None
    source_ip: Optional[str] = None
    destination_ip: Optional[str] = None
    user_name: Optional[str] = None
    host_name: Optional[str] = None
    raw_message: str

    model_config = ConfigDict(from_attributes=True)

class InvestigationCreate(BaseModel):
    incident_id: uuid.UUID
    file_record_id: uuid.UUID
    
    model_config = ConfigDict(from_attributes=True)

class InvestigationResponse(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    incident_id: uuid.UUID
    file_record_id: uuid.UUID
    status: str
    events_processed: int
    iocs_extracted: int
    metadata_json: Optional[dict] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)
