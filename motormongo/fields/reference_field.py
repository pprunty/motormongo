from motor.motor_asyncio import AsyncIOMotorClient

from motormongo.fields.field import Field

DATABASE = "test"


class ReferenceField(Field):
    def __init__(self, document_type, **kwargs):
        super().__init__(**kwargs)
        self.document_type = document_type

    async def fetch_reference(self, obj):
        db = AsyncIOMotorClient(os.getenv("MONGODB_URL"))[os.getenv("MONGODB_COLLECTION")]
        reference_id = obj.__dict__.get(self.name)
        if reference_id:
            document = await db[self.document_type.Meta.collection].find_one({'_id': reference_id})
            return self.document_type(**document) if document else None
        return None

    def __get__(self, obj, objtype=None):
        # Note: You can't directly return an awaitable here, as __get__ can't be async.
        # Instead, you might return a coroutine that can be awaited elsewhere.
        return self.fetch_reference(obj)

    def __set__(self, obj, value):
        if value is not None and not isinstance(value, ObjectId):
            if isinstance(value, self.document_type):
                value = value._id
            else:
                raise ValueError(
                    f"Value for {self.name} must be an ObjectId or an instance of {self.document_type.__name__}")
        super().__set__(obj, value)
