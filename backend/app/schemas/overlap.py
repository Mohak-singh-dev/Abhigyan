from datetime import datetime
from typing import List, Literal, Optional
from pydantic import BaseModel, ConfigDict, Field

class OverlapDecisionUpdate(BaseModel):
    state: Literal["linked", "dismissed", "deferred", "open", "reset"]
    justification: Optional[str] = Field(default="", max_length=2000)

class OverlapCreate(BaseModel):
    id: Optional[str] = None
    complaint_a_id: str
    complaint_b_id: str
    similarity: int = Field(default=85, ge=0, le=100)
    reasons: Optional[List[str]] = None

class OverlapHistoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    overlap_id: str
    decision_state: str
    justification: Optional[str] = None
    actor_name: Optional[str] = None
    actor_user_id: Optional[str] = None
    actor_role: Optional[str] = None
    created_at: datetime

class OverlapRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    complaint_a_id: str
    complaint_b_id: str
    a: str
    b: str
    similarity: int
    reasons: List[str] = []
    status: str
    decision_state: Optional[str] = None
    justification: Optional[str] = None
    reviewed_by: Optional[str] = None
    reviewed_by_user_id: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    history: List[OverlapHistoryRead] = []

class LinkedDocketRead(BaseModel):
    overlap_id: str
    case_id: str
    bureau: str
    title: str
    similarity: int
    justification: Optional[str] = None
    confirmed_by: Optional[str] = None
    confirmed_at: Optional[datetime] = None
