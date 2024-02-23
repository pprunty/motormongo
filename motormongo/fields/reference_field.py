from bson import ObjectId

from motormongo.fields.exceptions import ReferenceConversionError, ReferenceTypeError
from motormongo.fields.field import Field


class ReferenceField(Field):
    def __init__(self, document_class, **kwargs):
        super().__init__(type=ObjectId, **kwargs)
        self.document_class = document_class

    def __set__(self, obj, value):
        # If the value is an instance of the document_class, try to get its _id
        if isinstance(value, self.document_class):
            # If the value is an object, attempt to retrieve its ObjectId
            if hasattr(value, "_id"):
                value = ObjectId(value._id)
        # If the value is a string, attempt to convert it to ObjectId
        elif isinstance(value, str):
            try:
                value = ObjectId(value)
            except Exception:
                raise ReferenceConversionError(
                    f"String value '{value}' cannot be converted to an ObjectId."
                )
        # If the value is neither a string nor an ObjectId, nor a document instance, raise an error
        elif not isinstance(value, ObjectId):
            raise ReferenceTypeError(
                f"Value for {self.name} must be an ObjectId, a string representation of ObjectId, or an instance of {self.document_class.__name__}. Got {type(value)}."
            )

        super().__set__(obj, value)

    def __get__(self, instance, owner):
        if instance is None:
            return self  # Accessed on the class, not an instance

        # Return a coroutine that fetches the document
        # It's important to note that this coroutine must be awaited when accessed
        async def async_fetch():
            return await self.fetch(instance)

        return async_fetch()

    async def fetch(self, obj):
        """Fetch the referenced document from the database."""
        reference_value = obj.__dict__.get(self.name)
        if reference_value is None:
            return None
        if not isinstance(reference_value, ObjectId):
            raise ValueError(f"The reference '{self.name}' must be an ObjectId.")

        db = await self.document_class.db()
        collection = db[self.document_class.get_collection_name()]
        document = await collection.find_one({"_id": reference_value})
        return self.document_class(**document) if document else None
