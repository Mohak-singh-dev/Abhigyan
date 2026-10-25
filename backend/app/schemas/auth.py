from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from app.schemas.user import UserProfileRead

class LoginRequest(BaseModel):
    email: str = Field(..., description="Registered user email address")
    password: str = Field(..., description="User password")

    model_config = ConfigDict(populate_by_name=True)

class DemoLoginRequest(BaseModel):
    userId: Optional[str] = Field(None, alias="userId", description="Target user ID (e.g. u1, u2, u1b)")
    email: Optional[str] = Field(None, description="Target user email")
    role: Optional[str] = Field(None, description="Target user role (Complainant, BureauAdmin, Officer, Admin)")

    model_config = ConfigDict(populate_by_name=True)

class TokenResponse(BaseModel):
    accessToken: str = Field(..., alias="accessToken", description="Signed JWT Bearer token")
    tokenType: str = Field(default="bearer", alias="tokenType", description="Token type")
    expiresIn: int = Field(..., alias="expiresIn", description="Token validity window in seconds")
    user: UserProfileRead = Field(..., description="Authenticated user profile")

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)
