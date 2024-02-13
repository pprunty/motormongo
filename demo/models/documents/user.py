import re
import bcrypt
from enum import Enum

from motormongo.abstracts.embedded_document import EmbeddedDocument

from motormongo.fields.embedded_document_field import EmbeddedDocumentField
from motormongo.abstracts.document import Document
from motormongo.fields.datetime_field import DateTimeField
from motormongo.fields.reference_field import ReferenceField
from motormongo.fields.float_field import FloatField
from motormongo.fields.list_field import ListField
from motormongo.fields.geojson_field import GeoJSONField
from motormongo.fields.boolean_field import BooleanField
from motormongo.abstracts.document import Document
from motormongo.fields.binary_field import BinaryField
from motormongo.fields.string_field import StringField
from motormongo.fields.integer_field import IntegerField
from motormongo.fields.enum_field import EnumField

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
