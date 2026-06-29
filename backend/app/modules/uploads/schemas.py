from pydantic import BaseModel
import uuid
from datetime import datetime

class FileRecordResponse(BaseModel):
    id: uuid.UUID
    incident_id: uuid.UUID
    filename: str
    storage_path: str
    content_type: str
    size_bytes: int
    hash_sha256: str
    created_at: datetime
