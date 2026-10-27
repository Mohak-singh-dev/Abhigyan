from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator

VALID_USER_ROLES = {"Admin", "BureauAdmin", "Officer", "Complainant"}
VALID_USER_BUREAUS = {"All", "RB", "PGRC", "Approval", "Academic", "SB", "EO"}
VALID_USER_STATUSES = {"Active", "On Leave", "Inactive"}

class UserProfileBase(BaseModel):
    id: str
    name: str
    email: str
    role: str
    designation: str
    bureau: str = "All"
    avatarText: str = Field(default="OF", alias="avatarText")
    phone: str = ""
    status: str = "Active"
    department: Optional[str] = None

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

class UserProfileRead(UserProfileBase):
    activeCasesCount: int = Field(default=0, description="Active assigned cases count")

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

UserProfileCreate = UserProfileBase

class UserCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=255, description="Full official name")
    email: str = Field(..., min_length=5, max_length=255, description="Official email address")
    role: str = Field(..., description="System role: Admin, BureauAdmin, Officer, Complainant")
    bureau: str = Field(default="All", description="Bureau assignment")
    designation: Optional[str] = Field(None, max_length=255, description="Official title/designation")
    phone: Optional[str] = Field("", max_length=50, description="Phone contact")
    status: Optional[str] = Field("Active", description="Duty status: Active, On Leave, Inactive")
    department: Optional[str] = Field(None, max_length=255, description="Department name")
    password: str = Field(..., min_length=6, max_length=128, description="Initial account password")

    model_config = ConfigDict(populate_by_name=True)

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        clean = v.strip()
        if len(clean) < 6:
            raise ValueError("Initial password must be at least 6 characters.")
        return clean

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

    @field_validator("role")
    @classmethod
    def validate_role(cls, v: str) -> str:
        clean = v.strip()
        for r in VALID_USER_ROLES:
            if r.lower() == clean.lower():
                return r
        raise ValueError(f"Invalid role '{v}'. Permitted roles: {', '.join(sorted(VALID_USER_ROLES))}.")

    @field_validator("bureau")
    @classmethod
    def validate_bureau(cls, v: str) -> str:
        clean = v.strip()
        for b in VALID_USER_BUREAUS:
            if b.lower() == clean.lower():
                return b
        raise ValueError(f"Invalid bureau '{v}'. Permitted bureaus: {', '.join(sorted(VALID_USER_BUREAUS))}.")

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: Optional[str]) -> str:
        if not v or not v.strip():
            return "Active"
        clean = v.strip()
        for s in VALID_USER_STATUSES:
            if s.lower() == clean.lower():
                return s
        raise ValueError(f"Invalid status '{v}'. Permitted statuses: {', '.join(sorted(VALID_USER_STATUSES))}.")

class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    email: Optional[str] = Field(None, min_length=5, max_length=255)
    role: Optional[str] = Field(None)
    bureau: Optional[str] = Field(None)
    designation: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=50)
    status: Optional[str] = Field(None)
    department: Optional[str] = Field(None, max_length=255)
    password: Optional[str] = Field(None, min_length=6, max_length=128)

    model_config = ConfigDict(populate_by_name=True)

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        clean = v.strip().lower()
        if "@" not in clean or "." not in clean.split("@")[-1] or len(clean.split("@")[0]) == 0:
            raise ValueError("Invalid email format.")
        return clean

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        clean = v.strip()
        if len(clean) < 2:
            raise ValueError("Name must be at least 2 characters.")
        return clean

    @field_validator("role")
    @classmethod
    def validate_role(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        clean = v.strip()
        for r in VALID_USER_ROLES:
            if r.lower() == clean.lower():
                return r
        raise ValueError(f"Invalid role '{v}'. Permitted roles: {', '.join(sorted(VALID_USER_ROLES))}.")

    @field_validator("bureau")
    @classmethod
    def validate_bureau(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        clean = v.strip()
        for b in VALID_USER_BUREAUS:
            if b.lower() == clean.lower():
                return b
        raise ValueError(f"Invalid bureau '{v}'. Permitted bureaus: {', '.join(sorted(VALID_USER_BUREAUS))}.")

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        clean = v.strip()
        for s in VALID_USER_STATUSES:
            if s.lower() == clean.lower():
                return s
        raise ValueError(f"Invalid status '{v}'. Permitted statuses: {', '.join(sorted(VALID_USER_STATUSES))}.")

class UserStatusUpdate(BaseModel):
    status: str = Field(..., description="Duty status: Active, On Leave, Inactive")

    model_config = ConfigDict(populate_by_name=True)

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        clean = v.strip()
        for s in VALID_USER_STATUSES:
            if s.lower() == clean.lower():
                return s
        raise ValueError(f"Invalid status '{v}'. Permitted statuses: {', '.join(sorted(VALID_USER_STATUSES))}.")
