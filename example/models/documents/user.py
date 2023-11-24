import re

from motormongo.abstracts.base_document import Document
from motormongo.fields.binary_field import BinaryField
from motormongo.fields.string_field import StringField


class User(Document):
    username = StringField(help_text="The username for the user", min_length=3, max_length=50)
    email = StringField(help_text="The email for the user", regex=re.compile(r'^\S+@\S+\.\S+$'))  # Simple email regex
    password = BinaryField(help_text="The hashed password for the user")

