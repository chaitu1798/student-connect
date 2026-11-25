from pydantic import BaseModel, EmailStr
from datetime import datetime

class LoginRequest(BaseModel):
    username: str
    password: str
    mfa_code: str | None = None

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: dict

class RefreshRequest(BaseModel):
    refresh_token: str

class PasswordChangeRequest(BaseModel):
    old_password: str
    new_password: str

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: str
    role: str = "CLIENT"  # SUPER_ADMIN, ADMIN, REVIEWER, CLIENT

class UserOut(BaseModel):
    id: str
    username: str
    email: str
    full_name: str
    role: str
    is_active: bool
    must_change_password: bool
    mfa_enabled: bool
    created_at: datetime
