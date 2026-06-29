import uuid
from fastapi import APIRouter, Depends, Request, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.schemas import APIResponse
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.modules.uploads.schemas import FileRecordResponse
from app.modules.uploads.service import UploadsService


router = APIRouter(prefix="/uploads", tags=["Uploads"])

@router.post("", response_model=APIResponse[FileRecordResponse])
async def upload_file(
    request: Request,
    incident_id: uuid.UUID = Form(...),
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    
    # Ensure incident exists and belongs to the org
    from sqlalchemy import select
    from app.models.incident import Incident
    from app.core.exceptions import NotFoundError
    
    result = await session.execute(
        select(Incident).where(
            Incident.id == incident_id,
            Incident.organization_id == current_user.organization_id
        )
    )
    if not result.scalar_one_or_none():
        raise NotFoundError("Incident not found")
    
    content = await file.read()
    
    uploads_service = UploadsService(session)
    file_record = await uploads_service.upload_file(
        file_content=content,
        filename=file.filename,
        content_type=file.content_type,
        organization_id=current_user.organization_id,
        incident_id=incident_id,
        user_id=current_user.id,
        ip_address=ip_address,
        user_agent=user_agent
    )
    
    return APIResponse(
        success=True,
        message="File uploaded successfully",
        data=FileRecordResponse.model_validate(file_record, from_attributes=True)
    )
