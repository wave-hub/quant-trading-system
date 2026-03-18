"""Strategy model."""

from sqlalchemy import Column, String, Text, Integer, Boolean, JSON
from sqlalchemy.dialects.postgresql import UUID

from backend.config.database import Base
from backend.models.base import BaseModel


class Strategy(BaseModel, Base):
    """Strategy model."""

    __tablename__ = "strategies"

    name = Column(String(100), nullable=False, index=True)
    description = Column(Text)
    code = Column(Text, nullable=False)
    parameters = Column(JSON, default=dict)
    status = Column(String(20), default="draft", index=True)
    category = Column(String(50))
    is_visual = Column(Boolean, default=False)
    canvas_data = Column(JSON)
    generated_code = Column(Text)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    version = Column(Integer, default=1)

    def __repr__(self):
        return f"<Strategy(id={self.id}, name={self.name})>"
