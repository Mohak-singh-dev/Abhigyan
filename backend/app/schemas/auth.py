from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator
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

VALID_COMPLAINANT_TYPES = {"Student", "Faculty", "Parent", "Whistleblower", "General Public"}

class RegisterRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=255, description="Full name of complainant")
    email: str = Field(..., min_length=5, max_length=255, description="Valid email address")
    password: str = Field(..., min_length=6, max_length=128, description="Account password (min 6 chars)")
    phone: Optional[str] = Field("", max_length=50, description="Contact phone number")
    complainantType: Optional[str] = Field("General Public", alias="complainantType", description="Complainant type")
    role: Optional[str] = Field(None, description="Client-submitted role (ignored by server; Complainant is strictly enforced)")
    bureau: Optional[str] = Field(None, description="Client-submitted bureau (ignored by server)")

    model_config = ConfigDict(populate_by_name=True)

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        clean = v.strip().lower()
        if "@" not in clean or "." not in clean.split("@")[-1] or len(clean.split("@")[0]) == 0:
            raise ValueError("Invalid email format.")
        return clean

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        clean = v.strip()
        if len(clean) < 2:
            raise ValueError("Name must be at least 2 characters.")
        return clean

    @field_validator("complainantType")
    @classmethod
    def validate_complainant_type(cls, v: Optional[str]) -> str:
        if not v or not v.strip():
            return "General Public"
        clean = v.strip()
        for ct in VALID_COMPLAINANT_TYPES:
            if ct.lower() == clean.lower():
                return ct
        raise ValueError(
            f"Invalid complainantType '{v}'. Permitted types: {', '.join(sorted(VALID_COMPLAINANT_TYPES))}."
        )

class TokenResponse(BaseModel):
    accessToken: str = Field(..., alias="accessToken", description="Signed JWT Bearer token")
    tokenType: str = Field(default="bearer", alias="tokenType", description="Token type")
    expiresIn: int = Field(..., alias="expiresIn", description="Token validity window in seconds")
    user: UserProfileRead = Field(..., description="Authenticated user profile")

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)
