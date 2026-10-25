from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from app.models.base import Base

class ComplaintTimeline(Base):
    __tablename__ = "complaint_timelines"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    complaint_id = Column(String(64), ForeignKey("complaints.id", ondelete="CASCADE"), nullable=False, index=True)
    label = Column(String(500), nullable=False)
    date = Column(String(50), nullable=False)
    by = Column(String(255), nullable=True)
    role = Column(String(50), nullable=True)
    note = Column(Text, nullable=True)
    user_id = Column(String(64), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    complaint = relationship("Complaint", back_populates="timeline_events")
    user = relationship("User", backref="timeline_actions")

    def __repr__(self) -> str:
        return f"<ComplaintTimeline #{self.id} for {self.complaint_id}: {self.label[:30]}>"
