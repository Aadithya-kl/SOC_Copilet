import jwt
from fastapi import Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Callable

from app.core.config import settings
from app.core.exceptions import UnauthenticatedError, PermissionDeniedError
from app.core.database import get_db
from app.models.user import User

security = HTTPBearer()

async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: AsyncSession = Depends(get_db)
) -> User:
    token = credentials.credentials
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise UnauthenticatedError("Could not validate credentials")
    except jwt.ExpiredSignatureError:
        raise UnauthenticatedError("Token has expired")
    except jwt.InvalidTokenError:
        raise UnauthenticatedError("Could not validate credentials")

    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user is None:
        raise UnauthenticatedError("User not found")
    if not user.is_active:
        raise PermissionDeniedError("Inactive user")

    return user

def require_role(allowed_roles: list[str]) -> Callable:
    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role == "super_admin":
            return current_user
        if current_user.role not in allowed_roles:
            raise PermissionDeniedError("Insufficient permissions")
        return current_user
    return role_checker
