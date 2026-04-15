from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Optional, Literal, List


class ProjectCreate(BaseModel):
    name: str
    system_name: Optional[str] = ""
    level: Optional[int] = Field(None, ge=1, le=5)
    assignee_id: Optional[int] = None
    client_org: Optional[str] = None
    start_date: Optional[datetime] = None
    deadline: Optional[datetime] = None
    notes: Optional[str] = None


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    system_name: Optional[str] = None
    level: Optional[int] = Field(None, ge=1, le=5)
    assignee_id: Optional[int] = None
    client_org: Optional[str] = None
    start_date: Optional[datetime] = None
    deadline: Optional[datetime] = None
    notes: Optional[str] = None


class PhaseUpdate(BaseModel):
    phase: Literal["preparation", "self_assessment", "rectification", "formal_evaluation", "filing", "reporting"]


class ProjectResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    system_name: str
    level: int
    phase: str
    assignee_id: Optional[int] = None
    assignee_name: Optional[str] = None
    client_org: Optional[str] = None
    start_date: Optional[datetime] = None
    deadline: Optional[datetime] = None
    notes: Optional[str] = None
    created_by: int
    creator_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    checklist_completion: Optional[float] = None


class ProjectListResponse(BaseModel):
    items: List[ProjectResponse]
    total: int
