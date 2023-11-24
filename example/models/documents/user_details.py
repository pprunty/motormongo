import re

from example.models.documents.user import User
from motormongo.abstracts.base_document import Document
from motormongo.fields.boolean_field import BooleanField
from motormongo.fields.reference_field import ReferenceField
from motormongo.fields.string_field import StringField


class UserDetails(Document):
    user = ReferenceField(User, help_text="Reference back to the User document")
    active = BooleanField()