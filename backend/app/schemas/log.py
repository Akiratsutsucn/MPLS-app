from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional


class LogCreate(BaseModel):
    content: str


class LogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    content: str
    log_type: str
    created_by: Optional[int] = None
    author_name: Optional[str] = None
    created_at: datetime
