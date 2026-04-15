from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.database import Base


class ChecklistItem(Base):
    __tablename__ = "checklist_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    phase = Column(String(20), nullable=False)
    content = Column(String(500), nullable=False)
    is_completed = Column(Boolean, default=False)
    sort_order = Column(Integer, default=0)
    is_custom = Column(Boolean, default=False)
    completed_at = Column(DateTime, nullable=True)
    completed_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    project = relationship("Project", back_populates="checklist_items")
