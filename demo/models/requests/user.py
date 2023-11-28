from pydantic import BaseModel, Field


class UserModelRequest(BaseModel):
    username: str
    email: str
    password: str
