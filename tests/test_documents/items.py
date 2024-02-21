from motormongo import Document, StringField, FloatField, BooleanField


class Item(Document):
    name = StringField()
    cost = FloatField()
    high_value = BooleanField(default=False)

class Book(Item):
    title = StringField()
    author = StringField()
    isbn = StringField()

    class Meta:
        collection = "books"

class Electronics(Item):
    warranty_period = StringField()  # E.g., "2 years"
    brand = StringField()