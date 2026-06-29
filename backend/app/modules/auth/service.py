import jwt
import secrets
import hashlib
from datetime import datetime, timedelta, timezone
from passlib.hash import argon2
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional

from app.core.config import settings
from app.core.exceptions import UnauthenticatedError, PermissionDeniedError
from app.models.user import User
from app.models.refresh_token import RefreshToken
from app.models.audit_log import AuditLog
from app.modules.auth.schemas import TokenResponse

class AuthService:
    def __init__(self, session: AsyncSession):
        self.session = session

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        try:
            return argon2.verify(plain_password, hashed_password)
        except Exception:
            return False

    def create_access_token(self, user: User) -> str:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
        to_encode = {
            "sub": str(user.id),
            "org": str(user.organization_id),
            "role": user.role,
            "exp": expire
        }
        encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
        return encoded_jwt

    async def authenticate_user(self, email: str, password: str, ip_address: Optional[str] = None, user_agent: Optional[str] = None) -> TokenResponse:
        result = await self.session.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()

        if not user or not user.password_hash or not self.verify_password(password, user.password_hash):
            raise UnauthenticatedError("Incorrect email or password")
        
        if not user.is_active:
            raise PermissionDeniedError("Account is inactive")

        # Create access token
        access_token = self.create_access_token(user)
        
        # Create refresh token (stateful)
        raw_refresh_token = secrets.token_urlsafe(64)
        token_hash = hashlib.sha256(raw_refresh_token.encode()).hexdigest()
        
        expires_at = datetime.now(timezone.utc) + timedelta(days=7)
        db_refresh_token = RefreshToken(
            user_id=user.id,
            token_hash=token_hash,
            expires_at=expires_at,
            ip_address=ip_address,
            user_agent=user_agent
        )
        self.session.add(db_refresh_token)
        
        # Log audit
        audit = AuditLog(
            user_id=user.id,
            organization_id=user.organization_id,
            action="auth.login",
            ip_address=ip_address,
            user_agent=user_agent,
            details={"msg": "User logged in"}
        )
        self.session.add(audit)
        
        # Update last login
        user.last_login_at = datetime.now(timezone.utc)
        
        await self.session.commit()

        return TokenResponse(
            access_token=access_token,
            refresh_token=raw_refresh_token,
            expires_in=15 * 60
        )

    async def refresh_token(self, refresh_token: str, ip_address: Optional[str] = None, user_agent: Optional[str] = None) -> TokenResponse:
        token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
        
        result = await self.session.execute(select(RefreshToken).where(RefreshToken.token_hash == token_hash))
        db_token = result.scalar_one_or_none()
        
        if not db_token or db_token.revoked or db_token.expires_at < datetime.now(timezone.utc):
            if db_token:
                # If a revoked token is used, we might want to alert or revoke all others, for now just reject
                pass
            raise UnauthenticatedError("Invalid or expired refresh token")

        # Mark old token as revoked (rotation)
        db_token.revoked = True
        db_token.last_used_at = datetime.now(timezone.utc)
        
        # Get user
        user_result = await self.session.execute(select(User).where(User.id == db_token.user_id))
        user = user_result.scalar_one_or_none()
        
        if not user or not user.is_active:
            raise UnauthenticatedError("User not found or inactive")
            
        # Create new tokens
        access_token = self.create_access_token(user)
        new_raw_refresh = secrets.token_urlsafe(64)
        new_token_hash = hashlib.sha256(new_raw_refresh.encode()).hexdigest()
        
        expires_at = datetime.now(timezone.utc) + timedelta(days=7)
        new_db_refresh_token = RefreshToken(
            user_id=user.id,
            token_hash=new_token_hash,
            expires_at=expires_at,
            ip_address=ip_address,
            user_agent=user_agent
        )
        self.session.add(new_db_refresh_token)
        
        # Audit
        audit = AuditLog(
            user_id=user.id,
            organization_id=user.organization_id,
            action="auth.refresh",
            ip_address=ip_address,
            user_agent=user_agent,
            details={"old_token_id": str(db_token.id)}
        )
        self.session.add(audit)
        
        await self.session.commit()
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=new_raw_refresh,
            expires_in=15 * 60
        )
        
    async def logout(self, refresh_token: str, ip_address: Optional[str] = None, user_agent: Optional[str] = None) -> None:
        token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
        result = await self.session.execute(select(RefreshToken).where(RefreshToken.token_hash == token_hash))
        db_token = result.scalar_one_or_none()
        
        if db_token and not db_token.revoked:
            db_token.revoked = True
            
            # Audit
            audit = AuditLog(
                user_id=db_token.user_id,
                action="auth.logout",
                ip_address=ip_address,
                user_agent=user_agent,
                details={"token_id": str(db_token.id)}
            )
            self.session.add(audit)
            await self.session.commit()
