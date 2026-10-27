from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator
from app.schemas.timeline import TimelineEventRead

VALID_BUREAUS = {"RB", "PGRC", "Approval", "Academic", "SB", "EO"}
VALID_PRIORITIES = {"Critical", "High", "Medium", "Low"}
VALID_STATUSES = {"Pending", "In Progress", "Resolved", "Escalated"}
VALID_COMPLAINANT_TYPES = {"Student", "Faculty", "Parent", "Whistleblower", "General Public"}

class ComplaintBase(BaseModel):
    title: str = Field(..., min_length=5, max_length=500, description="Subject or brief summary of the grievance")
    description: str = Field(..., min_length=10, description="Detailed narrative and facts of the complaint")
    bureau: str = Field(..., description="Handling bureau: RB, PGRC, Approval, Academic, SB, EO")
    category: str = Field(..., min_length=2, max_length=255, description="Complaint category classification")
    priority: str = Field(default="Medium", description="Severity priority: Critical, High, Medium, Low")
    institutionId: str = Field(..., alias="institutionId", description="Referenced institution internal ID (e.g. i1)")
    institutionPermanentId: Optional[str] = Field(None, alias="institutionPermanentId", description="AICTE Permanent Institute ID")
    complainantType: Optional[str] = Field(default="General Public", alias="complainantType")
    complainantName: Optional[str] = Field(None, alias="complainantName")
    complainantEmail: Optional[str] = Field(None, alias="complainantEmail")
    complainantPhone: Optional[str] = Field(None, alias="complainantPhone")
    remarks: Optional[str] = None
    nextAction: Optional[str] = Field(None, alias="nextAction")
    lastActionDate: Optional[str] = Field(None, alias="lastActionDate")

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    @field_validator("bureau")
    @classmethod
    def validate_bureau(cls, v: str) -> str:
        for b in VALID_BUREAUS:
            if b.lower() == v.strip().lower():
                return b
        raise ValueError(f"Invalid Bureau '{v}'. Permitted bureaus: {', '.join(sorted(VALID_BUREAUS))}")

    @field_validator("priority")
    @classmethod
    def validate_priority(cls, v: str) -> str:
        for p in VALID_PRIORITIES:
            if p.lower() == v.strip().lower():
                return p
        raise ValueError(f"Invalid Priority '{v}'. Permitted values: {', '.join(sorted(VALID_PRIORITIES))}")

    @field_validator("complainantType")
    @classmethod
    def validate_complainant_type(cls, v: Optional[str]) -> Optional[str]:
        if not v:
            return "General Public"
        for ct in VALID_COMPLAINANT_TYPES:
            if ct.lower() == v.strip().lower():
                return ct
        raise ValueError(f"Invalid complainantType '{v}'. Permitted types: {', '.join(sorted(VALID_COMPLAINANT_TYPES))}")

class ComplaintCreate(ComplaintBase):
    id: Optional[str] = Field(None, description="Optional custom or client Case ID; generated automatically if omitted")
    officer: Optional[str] = Field(None, description="Assigned officer name; assigned by default bureau routing if omitted")
    status: Optional[str] = Field(default="Pending", description="Initial case status (defaults to 'Pending')")
    date: Optional[str] = Field(None, description="Filing date (YYYY-MM-DD); defaults to current date if omitted")
    due: Optional[str] = Field(None, description="Statutory SLA due date (YYYY-MM-DD); calculated from priority if omitted")

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: Optional[str]) -> str:
        if not v:
            return "Pending"
        for s in VALID_STATUSES:
            if s.lower() == v.strip().lower():
                return s
        raise ValueError(f"Invalid Status '{v}'. Permitted statuses: {', '.join(sorted(VALID_STATUSES))}")

class ComplaintRead(ComplaintBase):
    id: str
    officer: str
    status: str
    date: str
    due: str
    assignedUserId: Optional[str] = Field(None, alias="assignedUserId")
    complainantUserId: Optional[str] = Field(None, alias="complainantUserId")
    institutionName: Optional[str] = Field(None, alias="institutionName")
    createdAt: Optional[datetime] = Field(None, alias="createdAt")
    updatedAt: Optional[datetime] = Field(None, alias="updatedAt")
    timeline: List[TimelineEventRead] = Field(default_factory=list, description="Chronological audit history events")

    # AI Classification Advisory Metadata
    aiPredictedCategory: Optional[str] = Field(None, alias="aiPredictedCategory")
    aiPredictedBureau: Optional[str] = Field(None, alias="aiPredictedBureau")
    aiPredictedPriority: Optional[str] = Field(None, alias="aiPredictedPriority")
    aiConfidence: Optional[float] = Field(None, alias="aiConfidence")
    aiNeedsManualReview: Optional[bool] = Field(None, alias="aiNeedsManualReview")
    aiModelVersion: Optional[str] = Field(None, alias="aiModelVersion")
    aiClassificationRun: Optional[bool] = Field(None, alias="aiClassificationRun")

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

class ComplaintClassifyRequest(BaseModel):
    title: str = Field(..., description="Subject or brief summary of the grievance")
    description: str = Field(..., description="Detailed narrative of the complaint")
    confidenceThreshold: Optional[float] = Field(None, alias="confidenceThreshold", description="Optional custom minimum confidence threshold")

    model_config = ConfigDict(populate_by_name=True)

class ComplaintClassifyResponse(BaseModel):
    category: Optional[str] = Field(None, description="Predicted complaint category")
    bureau: Optional[str] = Field(None, description="Suggested bureau/cell")
    priority: Optional[str] = Field(None, description="Suggested priority")
    confidence: Optional[float] = Field(None, description="Category model confidence score (0.0 to 1.0)")
    priorityConfidence: Optional[float] = Field(None, alias="priorityConfidence", description="Priority model confidence score")
    needsManualReview: bool = Field(..., alias="needsManualReview", description="Whether human officer review is recommended")
    modelVersion: Optional[str] = Field(None, alias="modelVersion", description="Version of the prototype model")
    advisoryNotice: str = Field(..., alias="advisoryNotice", description="Advisory AI disclaimer")
    status: str = Field(default="success", description="Status of classification: success, unavailable, invalid_input, error")
    reviewReasons: List[str] = Field(default_factory=list, alias="reviewReasons", description="Reasons for manual review recommendation")

    model_config = ConfigDict(populate_by_name=True)

class ComplaintStatusUpdate(BaseModel):
    status: str = Field(..., description="Target status: Pending, In Progress, Resolved, Escalated")
    remarks: Optional[str] = Field(None, description="Updated case remarks")
    nextAction: Optional[str] = Field(None, alias="nextAction", description="Next workflow action")
    note: Optional[str] = Field(None, description="Timeline event narrative note")
    by: Optional[str] = Field(None, description="Actor display name (informational only; actor is always derived from JWT)")
    role: Optional[str] = Field(None, description="Actor role (informational only; role is always derived from JWT)")
    userId: Optional[str] = Field(None, alias="userId", description="ID of executing user (informational only; derived from JWT)")
    overrideReason: Optional[str] = Field(
        None,
        alias="overrideReason",
        description=(
            "System Admin only: Non-empty justification required to perform a status transition that "
            "bypasses normal workflow rules (e.g. re-opening Resolved cases). Must not be blank. "
            "Recorded verbatim in the case timeline."
        ),
    )

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        for s in VALID_STATUSES:
            if s.lower() == v.strip().lower():
                return s
        raise ValueError(f"Invalid status '{v}'. Permitted statuses: {', '.join(sorted(VALID_STATUSES))}")

class ComplaintAssignmentUpdate(BaseModel):
    userId: Optional[str] = Field(None, alias="userId", description="ID of target user (e.g. u2)")
    officer: Optional[str] = Field(None, description="Name of target officer (e.g. 'Rajesh Kumar')")
    bureau: Optional[str] = Field(None, description="Target bureau (e.g. 'PGRC', 'RB', 'Approval', etc.)")
    reason: Optional[str] = Field(None, description="Administrative justification for assignment")
    by: Optional[str] = Field(None, description="Actor display name (informational only; derived from JWT)")
    byRole: Optional[str] = Field(None, alias="byRole", description="Actor role (informational only; derived from JWT)")
    preserveBureau: Optional[bool] = Field(
        None,
        alias="preserveBureau",
        description=(
            "If True, the complaint's current bureau is kept unchanged regardless of the target officer's home bureau. "
            "Ordinary officer reassignment should set this to True. Cross-bureau transfer should leave it False/None "
            "and pass an explicit bureau. Defaults to False (legacy behaviour: officer's home bureau wins)."
        ),
    )

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    @field_validator("bureau")
    @classmethod
    def validate_bureau(cls, v: Optional[str]) -> Optional[str]:
        if not v:
            return None
        for b in VALID_BUREAUS:
            if b.lower() == v.strip().lower():
                return b
        raise ValueError(f"Invalid Bureau '{v}'. Permitted bureaus: {', '.join(sorted(VALID_BUREAUS))}")

class ComplaintListResponse(BaseModel):
    items: List[ComplaintRead]
    total: int
    page: int
    pageSize: int = Field(..., alias="pageSize")
    totalPages: int = Field(..., alias="totalPages")

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

class TimelineNoteCreate(BaseModel):
    note: str = Field(..., min_length=1, max_length=2000, description="Timeline note or remark text")
    label: Optional[str] = Field(None, description="Optional custom timeline event label")

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

