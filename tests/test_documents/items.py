from motormongo import Document, StringField, FloatField

class Item(Document):
    name = StringField()
    cost = FloatField()

class Book(Item):
    title = StringField()
    author = StringField()
    isbn = StringField()

    class Meta:
        collection = "books"

class Electronics(Item):
    warranty_period = StringField()  # E.g., "2 years"
    brand = StringField()