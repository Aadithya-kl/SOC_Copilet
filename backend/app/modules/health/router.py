from fastapi import APIRouter
from app.shared.schemas import APIResponse

router = APIRouter(prefix="/health", tags=["System"])

@router.get("", response_model=APIResponse[dict])
async def health_check():
    return APIResponse(success=True, data={"status": "ok"})
