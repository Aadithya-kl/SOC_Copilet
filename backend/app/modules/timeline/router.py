import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.modules.timeline.engine import TimelineEngine

router = APIRouter(prefix="/timeline", tags=["Timeline"])

@router.get("/")
async def get_timeline(
    investigation_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    engine = TimelineEngine(db)
    return await engine.build_timeline(investigation_id)
