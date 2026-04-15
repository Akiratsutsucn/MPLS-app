from pydantic import BaseModel, ConfigDict
from datetime import datetime


class UserCreate(BaseModel):
    username: str
    name: str
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    name: str
    created_at: datetime


class Token(BaseModel):
    access_token: str
    token_type: str
