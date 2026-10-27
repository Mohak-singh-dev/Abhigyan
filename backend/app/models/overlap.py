from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, JSON
from sqlalchemy.orm import relationship
from app.models.base import Base

class ComplaintOverlap(Base):
    __tablename__ = "complaint_overlaps"

    id = Column(String(64), primary_key=True, index=True)
    complaint_a_id = Column(String(64), ForeignKey("complaints.id", ondelete="CASCADE"), nullable=False, index=True)
    complaint_b_id = Column(String(64), ForeignKey("complaints.id", ondelete="CASCADE"), nullable=False, index=True)
    similarity = Column(Integer, nullable=False, default=85)
    reasons = Column(JSON, nullable=True)
    status = Column(String(50), nullable=False, default="open", index=True)  # open, linked, dismissed, deferred
    decision_state = Column(String(50), nullable=True)
    justification = Column(Text, nullable=True)
    reviewed_by = Column(String(255), nullable=True)
    reviewed_by_user_id = Column(String(64), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    reviewed_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    complaint_a = relationship("Complaint", foreign_keys=[complaint_a_id], backref="overlaps_as_a")
    complaint_b = relationship("Complaint", foreign_keys=[complaint_b_id], backref="overlaps_as_b")
    reviewer = relationship("User", foreign_keys=[reviewed_by_user_id], backref="reviewed_overlaps")
    history = relationship(
        "ComplaintOverlapHistory",
        back_populates="overlap",
        order_by="ComplaintOverlapHistory.id.asc()",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<ComplaintOverlap {self.id}: {self.complaint_a_id} <-> {self.complaint_b_id} ({self.status})>"


class ComplaintOverlapHistory(Base):
    __tablename__ = "complaint_overlap_history"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    overlap_id = Column(String(64), ForeignKey("complaint_overlaps.id", ondelete="CASCADE"), nullable=False, index=True)
    decision_state = Column(String(50), nullable=False)
    justification = Column(Text, nullable=True)
    actor_name = Column(String(255), nullable=True)
    actor_user_id = Column(String(64), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    actor_role = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    overlap = relationship("ComplaintOverlap", back_populates="history")
    actor = relationship("User", foreign_keys=[actor_user_id])

    def __repr__(self) -> str:
        return f"<ComplaintOverlapHistory #{self.id} for {self.overlap_id}: {self.decision_state}>"
