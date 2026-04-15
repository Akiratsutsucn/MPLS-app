from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional


class ChecklistItemCreate(BaseModel):
    content: str
    phase: str


class ChecklistItemUpdate(BaseModel):
    content: Optional[str] = None
    is_completed: Optional[bool] = None


class ChecklistItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    phase: str
    content: str
    is_completed: bool
    sort_order: int
    is_custom: bool
    completed_at: Optional[datetime] = None
    completed_by: Optional[int] = None
