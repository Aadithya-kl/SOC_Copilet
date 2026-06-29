from pydantic import BaseModel, EmailStr
from typing import Optional
import uuid

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

class RefreshRequest(BaseModel):
    refresh_token: str

class UserProfile(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    email: str
    username: str
    role: str
    display_name: Optional[str] = None
