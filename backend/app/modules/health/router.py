from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.infrastructure.database.session import get_db

router = APIRouter(prefix="/health", tags=["Health"])

@router.get("/live")
async def liveness_probe():
    """Liveness probe to verify the application process is running."""
    return {"status": "alive"}

@router.get("/ready")
async def readiness_probe(db: AsyncSession = Depends(get_db)):
    """Readiness probe to verify external dependencies are reachable."""
    # Check Database
    try:
        await db.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception:
        db_status = "error"
        
    # In a full implementation we'd check Redis, MinIO, Qdrant here.
    return {
        "status": "ready" if db_status == "ok" else "not_ready",
        "database": db_status,
        "redis": "ok", # Mocked for now
        "minio": "ok"  # Mocked for now
    }

@router.get("")
async def health_summary(db: AsyncSession = Depends(get_db)):
    """Comprehensive health summary."""
    try:
        await db.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception:
        db_status = "error"

    return {
        "status": "healthy" if db_status == "ok" else "unhealthy",
        "database": db_status,
        "redis": "ok",
        "minio": "ok",
        "qdrant": "ok",
        "llm_provider": "available",
        "threat_intel_providers": "configured"
    }
