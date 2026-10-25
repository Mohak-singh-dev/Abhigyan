from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

class TimelineEventBase(BaseModel):
    label: str = Field(..., min_length=2, max_length=500, description="Event action or description")
    date: str = Field(..., description="Timestamp or date string (YYYY-MM-DD or YYYY-MM-DD HH:MM)")
    by: Optional[str] = Field(None, description="Display name of the actor or system")
    role: Optional[str] = Field(None, description="Role of the actor: Complainant, BureauAdmin, Officer, Admin")
    note: Optional[str] = Field(None, description="Detailed explanation, administrative justification, or note")

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

class TimelineEventCreate(TimelineEventBase):
    userId: Optional[str] = Field(None, alias="userId", description="Referenced user ID if initiated by an AICTE user")

class TimelineEventRead(TimelineEventBase):
    id: int
    complaintId: str = Field(..., alias="complaintId")
    userId: Optional[str] = Field(None, alias="userId")
    createdAt: Optional[datetime] = Field(None, alias="createdAt")

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)
