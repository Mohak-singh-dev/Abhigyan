from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, String
from app.models.base import Base

class Institution(Base):
    __tablename__ = "institutions"

    id = Column(String(64), primary_key=True, index=True)
    aicte_id = Column(String(64), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False, index=True)
    city = Column(String(100), nullable=False, index=True)
    state = Column(String(100), nullable=False, index=True)
    type = Column(String(100), nullable=False, index=True)
    approved = Column(String(20), nullable=False)
    contact_email = Column(String(255), nullable=True)
    contact_phone = Column(String(50), nullable=True)
    risk_level = Column(String(50), nullable=True, default="Low")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:
        return f"<Institution {self.id} {self.name} ({self.aicte_id})>"
