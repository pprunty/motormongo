import re
from enum import Enum

import bcrypt

from motormongo import (
    BinaryField,
    BooleanField,
    DateTimeField,
    Document,
    EmbeddedDocument,
    EmbeddedDocumentField,
    EnumField,
    FloatField,
    GeoJSONField,
    IntegerField,
    ListField,
    ReferenceField,
    StringField,
)


def hash_password(password: str) -> bytes:
    if isinstance(password, bytes):
        password = password.decode("utf-8")  # Convert bytes to string if necessary
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())


class Status(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class Gender(Enum):
    MALE = "male"
    FEMALE = "female"


class Profile(EmbeddedDocument):
    bio = StringField()
    website = StringField(default="somesite.com")


class User(Document):
    username = StringField(min_length=3, max_length=50)
    email = StringField(
        regex=re.compile(r"^\S+@\S+\.\S+$"), min_length=0, max_length=50
    )
    password = BinaryField(hash_function=hash_password)
    location = GeoJSONField(return_as_list=True)
    last_login = DateTimeField(auto_now=True)
    age = IntegerField(min_value=5, max_value=100)
    alive = BooleanField(default=True)
    status = EnumField(enum=Status)
    favorite_colors = ListField(field=StringField())
    net_worth = FloatField(min_value=5.0, max_value=10)
    profile = EmbeddedDocumentField(document_type=Profile)

    def verify_password(self, password: str) -> bool:
        return bcrypt.checkpw(password.encode("utf-8"), self.password)

    class Meta:
        collection = "users"
        indexes = [
            {"fields": [("created_at", -1)]},  # Ascending index on username
        ]
        created_at_timestamp = True
        updated_at_timestamp = True


class Metadata(EmbeddedDocument):
    hair_color = StringField()
    ethnicity = StringField()


class UserDetails(Document):
    gender = EnumField(enum=Gender)
    user = ReferenceField(User)
    dob = DateTimeField()
    metadata = EmbeddedDocumentField(Metadata)

    class Meta:
        collection = "user_details"
        created_at_timestamp = True  # < Provide a DateTimeField for document creation
        updated_at_timestamp = True  # < Provide a DateTimeField for document creation
