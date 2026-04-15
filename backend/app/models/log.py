from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.database import Base


class ProjectLog(Base):
    __tablename__ = "project_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    content = Column(Text, nullable=False)
    log_type = Column(String(20), default="manual", comment="manual/system")
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    project = relationship("Project", back_populates="logs")
    author = relationship("User", foreign_keys=[created_by])
