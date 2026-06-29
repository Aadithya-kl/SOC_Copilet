from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.schemas import APIResponse
from app.core.database import get_db
from app.modules.auth.schemas import LoginRequest, TokenResponse, RefreshRequest, UserProfile
from app.modules.auth.service import AuthService
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login", response_model=APIResponse[TokenResponse])
async def login(
    request: Request,
    payload: LoginRequest,
    session: AsyncSession = Depends(get_db)
):
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    
    auth_service = AuthService(session)
    token_response = await auth_service.authenticate_user(
        email=payload.email,
        password=payload.password,
        ip_address=ip_address,
        user_agent=user_agent
    )
    
    return APIResponse(success=True, message="Login successful", data=token_response)

@router.post("/refresh", response_model=APIResponse[TokenResponse])
async def refresh(
    request: Request,
    payload: RefreshRequest,
    session: AsyncSession = Depends(get_db)
):
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    
    auth_service = AuthService(session)
    token_response = await auth_service.refresh_token(
        refresh_token=payload.refresh_token,
        ip_address=ip_address,
        user_agent=user_agent
    )
    
    return APIResponse(success=True, message="Token refreshed", data=token_response)

@router.post("/logout", response_model=APIResponse[None])
async def logout(
    request: Request,
    payload: RefreshRequest,
    session: AsyncSession = Depends(get_db)
):
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    
    auth_service = AuthService(session)
    await auth_service.logout(
        refresh_token=payload.refresh_token,
        ip_address=ip_address,
        user_agent=user_agent
    )
    
    return APIResponse(success=True, message="Logged out successfully", data=None)

@router.get("/me", response_model=APIResponse[UserProfile])
async def get_me(current_user: User = Depends(get_current_user)):
    user_profile = UserProfile(
        id=current_user.id,
        organization_id=current_user.organization_id,
        email=current_user.email,
        username=current_user.username,
        role=current_user.role,
        display_name=current_user.display_name
    )
    return APIResponse(success=True, data=user_profile)
