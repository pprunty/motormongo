import re
import bcrypt

from motormongo.fields.datetime_field import DateTimeField
from motormongo.fields.reference_field import ReferenceField
from motormongo.fields.float_field import FloatField
from motormongo.fields.list_field import ListField
from motormongo.fields.geopoint_field import GeoPointField
from motormongo.fields.boolean_field import BooleanField
from motormongo.abstracts.document import Document
from motormongo.fields.binary_field import BinaryField
from motormongo.fields.string_field import StringField
from motormongo.fields.integer_field import IntegerField
from motormongo.fields.enum_field import EnumField
from enum import Enum

def hash_password(password) -> bytes:
    # Example hashing function
    return bcrypt.hashpw(password.encode('utf-8'), salt=bcrypt.gensalt())

class Status(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"

class Gender(Enum):
    MALE = "male"
    FEMALE = "female"


class User(Document):
    username = StringField(help_text="The username for the user", min_length=3, max_length=50)
    email = StringField(help_text="The email for the user", regex=re.compile(r'^\S+@\S+\.\S+$'))  # Simple email regex
    password = BinaryField(help_text="The hashed password for the user", hash_function=hash_password)
    location = GeoPointField(help_text="The user's location", return_as_json=False)
    age = IntegerField(help_text="The age of the user")
    alive = BooleanField(help_text="Whether the user is dead or alive.")
    status = EnumField(enum=Status, help_text="Indicator for whether the user is active or not.")
    favorite_colors = ListField(field=StringField(), help_text="List of user's favorite colors")
    net_worth = FloatField(min_value=0.0, help_text="The user's net worth")

    # todo: add list, reference and datetime field for testing

    class Meta:
        collection = "users"  # < If not provided, will default to class name (ex. User->user, UserDetails->user_details)
        indexes = [
            {
                'fields': ['location'],
                'type': '2dsphere'
            },
            # Other index definitions...
        ]
        created_at_timestamp = True  # < Provide a DateTimeField for document creation
        updated_at_timestamp = True  # < Provide a DateTimeField for document updates

class UserDetails(Document):
    user = ReferenceField(User,
                          help_text="A reference back to the User document",
                          editable=False,
                          updated=False)
    gender = EnumField(enum=Gender, help_text="The gender of the user")
    dob = DateTimeField(help_text="The user's date of birth.")
