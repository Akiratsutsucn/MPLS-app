from pydantic import BaseModel, ConfigDict
from datetime import date, datetime


class ReminderCreate(BaseModel):
    title: str
    remind_date: date


class ReminderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    title: str
    remind_date: date
    is_dismissed: bool
    created_by: int
    created_at: datetime
