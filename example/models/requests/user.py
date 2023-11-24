from pydantic import BaseModel, Field


class UserModelRequest(BaseModel):
    name: str
    money: int
    alive: bool = Field(default=True)
