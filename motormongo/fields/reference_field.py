from bson import ObjectId

from motormongo.fields.exceptions import ReferenceConversionError, ReferenceTypeError
from motormongo.fields.field import Field


class ReferenceField(Field):
    def __init__(self, document, **kwargs):
        super().__init__(type=ObjectId, **kwargs)
        self.document = document

    def validate(self, value):
        """Validate the input value against the field's constraints."""
        # If the value is an instance of the document, try to get its _id
        if isinstance(value, self.document):
            if hasattr(value, "_id"):
                return ObjectId(value._id)  # Convert to ObjectId for consistency
        # If the value is a string, attempt to convert it to ObjectId
        elif isinstance(value, str):
            try:
                return ObjectId(value)
            except Exception:
                raise ReferenceConversionError(
                    f"String value '{value}' cannot be converted to an ObjectId."
                )
        # If the value is already an ObjectId, it's valid
        elif isinstance(value, ObjectId):
            return value
        # If the value is neither a string nor an ObjectId, nor a document instance, raise an error
        else:
            raise ReferenceTypeError(
                f"Value for {self.name} must be an ObjectId, a string representation of ObjectId, or an instance of {self.document.__name__}. Got {type(value).__name__}."
            )

    def __set__(self, obj, value):
        if value is not None:
            validated_value = self.validate(
                value
            )  # Use validate method to process the value
            super().__set__(obj, validated_value)
        else:
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

        db = await self.document.db()
        collection = db[self.document.get_collection_name()]
        document = await collection.find_one({"_id": reference_value})
        return self.document(**document) if document else None
