from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, func
from sqlalchemy.orm import relationship
from app.database import Base


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    system_name = Column(String(200), nullable=False)
    level = Column(Integer, nullable=False, comment="等保等级 1-5")
    phase = Column(
        String(20),
        nullable=False,
        default="preparation",
        comment="preparation/self_assessment/rectification/formal_evaluation/filing/reporting",
    )
    assignee_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    client_org = Column(String(200), default="")
    deadline = Column(DateTime, nullable=True)
    notes = Column(Text, default="")
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    assignee = relationship("User", foreign_keys=[assignee_id])
    creator = relationship("User", foreign_keys=[created_by])
    checklist_items = relationship("ChecklistItem", back_populates="project", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="project", cascade="all, delete-orphan")
    logs = relationship("ProjectLog", back_populates="project", cascade="all, delete-orphan")
    reminders = relationship("Reminder", back_populates="project", cascade="all, delete-orphan")
