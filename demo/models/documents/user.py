import re
import bcrypt
from enum import Enum

from motormongo import Document, EmbeddedDocument
from motormongo import (EmbeddedDocumentField, DateTimeField, ReferenceField, FloatField, ListField,
                               GeoJSONField, BooleanField, BinaryField, StringField, IntegerField, EnumField)


def hash_password(password) -> bytes:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())


class Status(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class Gender(Enum):
    MALE = "male"
    FEMALE = "female"


class User(Document):
    username = StringField(min_length=3, max_length=50)
    email = StringField(regex=re.compile(r'^\S+@\S+\.\S+$'))
    password = BinaryField(hash_function=hash_password)
    location = GeoJSONField(return_as_list=True)
    age = IntegerField()
    alive = BooleanField(default=True)
    status = EnumField(enum=Status)
    favorite_colors = ListField(field=StringField())
    net_worth = FloatField(min_value=0.0)

    class Meta:
        collection = "users"
        indexes = [{'fields': ['location'], 'type': '2dsphere'}]
        timestamps = True


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
