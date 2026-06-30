import uuid
import json
import asyncio
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.investigation import InvestigationState
from app.modules.investigation.schemas import InvestigationResponse, InvestigationCreate
import redis.asyncio as redis
from app.core.config import settings
from arq import create_pool
from arq.connections import RedisSettings

router = APIRouter(prefix="/investigations", tags=["Investigations"])

@router.post("", response_model=InvestigationResponse, status_code=201)
async def create_investigation(
    data: InvestigationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    investigation = InvestigationState(
        organization_id=current_user.organization_id,
        incident_id=data.incident_id,
        file_record_id=data.file_record_id,
        status="queued"
    )
    db.add(investigation)
    await db.commit()
    await db.refresh(investigation)
    
    # Enqueue task
    redis_settings = RedisSettings.from_dsn(settings.REDIS_URL)
    arq_pool = await create_pool(redis_settings)
    await arq_pool.enqueue_job('run_investigation', investigation.id)
    await arq_pool.close()
    
    return investigation

@router.get("/{investigation_id}", response_model=InvestigationResponse)
async def get_investigation_status(
    investigation_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(InvestigationState).where(
            InvestigationState.id == investigation_id,
            InvestigationState.organization_id == current_user.organization_id
        )
    )
    investigation = result.scalar_one_or_none()
    if not investigation:
        raise HTTPException(status_code=404, detail="Investigation not found")
        
    return investigation

@router.websocket("/{investigation_id}/ws")
async def investigation_websocket(
    websocket: WebSocket,
    investigation_id: uuid.UUID
):
    await websocket.accept()
    
    redis_client = redis.Redis.from_url(settings.REDIS_URL)
    pubsub = redis_client.pubsub()
    channel_name = f"investigation_{investigation_id}_progress"
    
    await pubsub.subscribe(channel_name)
    
    try:
        while True:
            # We also need to periodically yield control or check if client disconnected.
            # wait_message blocks, but we can use get_message in a loop with asyncio.sleep
            message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
            if message and message["type"] == "message":
                data = message["data"].decode("utf-8")
                await websocket.send_text(data)
                
                parsed = json.loads(data)
                if parsed.get("status") in ["completed", "failed"]:
                    break
            
            # Check for client disconnect by trying to receive
            # If we await websocket.receive(), it blocks. So we don't.
            # WebSocketDisconnect will be raised on send_text if client leaves.
            await asyncio.sleep(0.1)
    except WebSocketDisconnect:
        pass
    finally:
        await pubsub.unsubscribe(channel_name)
        await redis_client.close()
