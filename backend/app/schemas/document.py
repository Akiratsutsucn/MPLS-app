from pydantic import BaseModel, ConfigDict
from datetime import datetime


class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    phase: str
    filename: str
    filesize: int
    uploaded_by: int
    uploaded_at: datetime
