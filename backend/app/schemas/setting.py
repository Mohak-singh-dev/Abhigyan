from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, model_validator


class SettingUpdate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    similarity_threshold: Optional[int] = Field(None, alias="similarityThreshold", ge=50, le=95)
    sla_critical: Optional[int] = Field(None, alias="slaCritical", ge=1, le=30)
    sla_high: Optional[int] = Field(None, alias="slaHigh", ge=1, le=60)
    sla_medium: Optional[int] = Field(None, alias="slaMedium", ge=1, le=90)
    auto_escalate: Optional[bool] = Field(None, alias="autoEscalate")
    email_alerts: Optional[bool] = Field(None, alias="emailAlerts")


class SettingRead(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    key: str = "global"
    similarity_threshold: int = 75
    sla_critical: int = 3
    sla_high: int = 7
    sla_medium: int = 14
    auto_escalate: bool = True
    email_alerts: bool = True
    updated_at: datetime
    updated_by: Optional[str] = None
    updated_by_user_id: Optional[str] = None

    # Aliases for frontend TypeScript AppSettings
    similarityThreshold: Optional[int] = None
    slaCritical: Optional[int] = None
    slaHigh: Optional[int] = None
    slaMedium: Optional[int] = None
    autoEscalate: Optional[bool] = None
    emailAlerts: Optional[bool] = None
    updatedAt: Optional[str] = None
    updatedBy: Optional[str] = None

    @model_validator(mode="after")
    def sync_aliases(self):
        if self.similarityThreshold is None:
            self.similarityThreshold = self.similarity_threshold
        if self.slaCritical is None:
            self.slaCritical = self.sla_critical
        if self.slaHigh is None:
            self.slaHigh = self.sla_high
        if self.slaMedium is None:
            self.slaMedium = self.sla_medium
        if self.autoEscalate is None:
            self.autoEscalate = self.auto_escalate
        if self.emailAlerts is None:
            self.emailAlerts = self.email_alerts
        if self.updatedAt is None and self.updated_at:
            self.updatedAt = self.updated_at.isoformat()
        if self.updatedBy is None:
            self.updatedBy = self.updated_by
        return self
