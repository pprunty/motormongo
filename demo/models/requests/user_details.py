from pydantic import BaseModel
from typing import Optional
from datetime import date
from demo.models.documents.user import Gender

class UserDetailsRequest(BaseModel):
    user: str  # Assuming this is how you link UserDetails to User
    gender: Gender
    dob: date
