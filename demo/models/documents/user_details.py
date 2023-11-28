import re

from demo.models.documents.user import User
from motormongo.abstracts.document import Document
from motormongo.fields.boolean_field import BooleanField
from motormongo.fields.reference_field import ReferenceField
from motormongo.fields.string_field import StringField


class UserDetails(Document):
    user = ReferenceField(User, help_text="Reference back to the User document")
    active = BooleanField()
