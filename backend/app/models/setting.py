from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Boolean
from sqlalchemy.orm import relationship
from app.models.base import Base


class SystemSetting(Base):
    __tablename__ = "system_settings"

    key = Column(String(64), primary_key=True, default="global", index=True)
    similarity_threshold = Column(Integer, nullable=False, default=75)
    sla_critical = Column(Integer, nullable=False, default=3)
    sla_high = Column(Integer, nullable=False, default=7)
    sla_medium = Column(Integer, nullable=False, default=14)
    auto_escalate = Column(Boolean, nullable=False, default=True)
    email_alerts = Column(Boolean, nullable=False, default=True)

    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_by = Column(String(255), nullable=True)
    updated_by_user_id = Column(
        String(64),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    updater = relationship("User", foreign_keys=[updated_by_user_id], backref="settings_updates")

    def __repr__(self) -> str:
        return (
            f"<SystemSetting key={self.key} threshold={self.similarity_threshold}% "
            f"SLA=({self.sla_critical},{self.sla_high},{self.sla_medium})>"
        )
