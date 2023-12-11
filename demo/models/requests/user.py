from typing import List
from pydantic import BaseModel, Field
from demo.models.documents.user import Status


class UserModelRequest(BaseModel):
    username: str = Field(example="johndoe")
    email: str = Field(example="johndoe@coldmail.com")
    password: str = Field(example="password123")
    age: int = Field(example="42")
    alive: bool = Field(example=False, default=True)
    status: str = Field(example=Status.ACTIVE)
    location: List[float] = Field(example=[38.8977, 77.0365])
