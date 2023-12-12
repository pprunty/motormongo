import re
import bcrypt

from motormongo.fields.geojson_field import GeoPointField
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


class User(Document):
    username = StringField(help_text="The username for the user", min_length=3, max_length=50)
    email = StringField(help_text="The email for the user", regex=re.compile(r'^\S+@\S+\.\S+$'))  # Simple email regex
    password = BinaryField(help_text="The hashed password for the user", hash_function=hash_password)
    location = GeoPointField(help_text="The user's location", return_as_json=False)
    age = IntegerField(help_text="The age of the user")
    alive = BooleanField(help_text="Whether the user is dead or alive.")
    status = EnumField(enum=Status, help_text="Indicator for whether the user is active or not.")
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
