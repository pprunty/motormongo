from motormongo import Document, StringField
from motormongo.fields import ReferenceField


class User(Document):
    name = StringField()


class Post(Document):
    author = ReferenceField(document_class=User)
