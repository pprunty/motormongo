from bson import ObjectId
from motormongo.fields.field import Field

class ReferenceField(Field):
    def __init__(self, document_class, **kwargs):
        super().__init__(**kwargs)
        self.document_class = document_class

    def __set__(self, obj, value):
        # Check if the value is a Document instance or an ObjectId
        if isinstance(value, self.document_class):
            value = value._id  # Assume the document has an _id attribute
        elif isinstance(value, str):
            value = ObjectId(value)
        elif not isinstance(value, ObjectId):
            raise ValueError(f"Value for {self.name} must be an ObjectId, a string, or an instance of {self.document_class.__name__}")

        super().__set__(obj, value)

    async def fetch(self, obj):
        """Fetch the referenced document from the database."""
        db = await self.document_class.db()
        collection = db[self.document_class.get_collection_name()]
        document = await collection.find_one({'_id': obj.__dict__[self.name]})
        return self.document_class(**document) if document else None
