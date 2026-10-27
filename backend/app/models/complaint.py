from datetime import datetime, timezone
from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import relationship
from app.models.base import Base

class Complaint(Base):
    __tablename__ = "complaints"

    id = Column(String(64), primary_key=True, index=True)
    institution_id = Column(String(64), ForeignKey("institutions.id", ondelete="RESTRICT"), nullable=False, index=True)
    institution_permanent_id = Column(String(64), nullable=True, index=True)
    bureau = Column(String(50), nullable=False, index=True)
    category = Column(String(255), nullable=False, index=True)
    priority = Column(String(50), nullable=False, default="Medium", index=True)
    status = Column(String(50), nullable=False, default="Pending", index=True)
    officer = Column(String(255), nullable=False)
    assigned_user_id = Column(String(64), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    date = Column(String(50), nullable=False)
    due = Column(String(50), nullable=False)
    title = Column(String(500), nullable=False, index=True)
    description = Column(Text, nullable=False)

    # Complainant metadata
    complainant_user_id = Column(String(64), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    complainant_type = Column(String(50), nullable=True, default="General Public")
    complainant_name = Column(String(255), nullable=True)
    complainant_email = Column(String(255), nullable=True, index=True)
    complainant_phone = Column(String(50), nullable=True)

    # Resolution & Workflow Tracking
    remarks = Column(Text, nullable=True)
    next_action = Column(String(255), nullable=True)
    last_action_date = Column(String(50), nullable=True)

    # AI Classification Advisory Metadata
    ai_predicted_category = Column(String(255), nullable=True)
    ai_predicted_bureau = Column(String(50), nullable=True)
    ai_predicted_priority = Column(String(50), nullable=True)
    ai_confidence = Column(Float, nullable=True)
    ai_needs_manual_review = Column(Boolean, nullable=True, default=False)
    ai_model_version = Column(String(50), nullable=True)
    ai_classification_run = Column(Boolean, nullable=True, default=False)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    institution = relationship("Institution", backref="complaints")
    assigned_user = relationship("User", foreign_keys=[assigned_user_id], backref="assigned_complaints")
    complainant_user = relationship("User", foreign_keys=[complainant_user_id], backref="filed_complaints")
    timeline_events = relationship(
        "ComplaintTimeline",
        back_populates="complaint",
        order_by="ComplaintTimeline.id.asc()",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Complaint {self.id} [{self.bureau}] {self.status} - {self.title[:30]}>"
