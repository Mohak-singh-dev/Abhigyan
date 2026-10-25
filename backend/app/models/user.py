from datetime import datetime
from sqlalchemy import Column, DateTime, String
from app.models.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(String(64), primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    role = Column(String(50), nullable=False, index=True)
    designation = Column(String(255), nullable=False)
    bureau = Column(String(50), nullable=False, default="All", index=True)
    avatar_text = Column(String(10), nullable=False, default="OF")
    phone = Column(String(50), nullable=False, default="")
    status = Column(String(50), nullable=False, default="Active", index=True)
    department = Column(String(255), nullable=True)
    password_hash = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:
        return f"<User {self.id} {self.name} ({self.role})>"
