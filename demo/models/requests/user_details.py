from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime
from demo.models.documents.user import Gender

class Metadata(BaseModel):
    hair_color: str
    ethnicity: str

class UserDetailsRequest(BaseModel):
    user: str  # Assuming this is how you link UserDetails to User
    gender: Gender
    dob: datetime
    metadata: Metadata

class UpdateUserDetailsRequest(BaseModel):
    gender: str
    dob: datetime
    metadata: Metadata