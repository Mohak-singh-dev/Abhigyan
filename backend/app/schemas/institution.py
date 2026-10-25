from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

class InstitutionBase(BaseModel):
    id: str
    aicteId: str = Field(..., alias="aicteId")
    name: str
    city: str
    state: str
    type: str
    approved: str
    contactEmail: Optional[str] = None
    contactPhone: Optional[str] = None
    riskLevel: Optional[str] = "Low"

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

class InstitutionCreate(InstitutionBase):
    pass

class InstitutionRead(InstitutionBase):
    totalComplaints: int = Field(default=0, description="Total logged complaints count")
    activeComplaints: int = Field(default=0, description="Active complaints count")

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)
