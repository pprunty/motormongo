import re

import bcrypt

from motormongo.abstracts.document import Document
from motormongo.fields.binary_field import BinaryField
from motormongo.fields.string_field import StringField


def hash_password(password):
    # Example hashing function
    return bcrypt.hashpw(password.encode('utf-8'), salt=bcrypt.gensalt())


class User(Document):
    username = StringField(help_text="The username for the user", min_length=3, max_length=50)
    email = StringField(help_text="The email for the user", regex=re.compile(r'^\S+@\S+\.\S+$'))  # Simple email regex
    password = BinaryField(help_text="The hashed password for the user", hash_function=hash_password)

    # password = BinaryField(help_text="The hashed password for the user", hash_function=hash_password)

    class Meta:
        collection = "users"
        created_at_timestamp = True
        updated_at_timestamp = True