from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

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

class UserProfileCreate(UserProfileBase):
    pass

class UserProfileRead(UserProfileBase):
    activeCasesCount: int = Field(default=0, description="Active assigned cases count")

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)
