from motor.motor_asyncio import AsyncIOMotorClient
import os
import warnings
from pymongo.errors import OperationFailure

from motormongo.abstracts.document import Document
from motormongo.abstracts.embedded_document import EmbeddedDocument
from motormongo.fields.integer_field import IntegerField
from motormongo.fields.geojson_field import GeoJSONField
from motormongo.fields.reference_field import ReferenceField
from motormongo.fields.datetime_field import DateTimeField
from motormongo.fields.enum_field import EnumField
from motormongo.fields.binary_field import BinaryField
from motormongo.fields.boolean_field import BooleanField
from motormongo.fields.embedded_document_field import EmbeddedDocumentField
from motormongo.fields.float_field import FloatField
from motormongo.fields.list_field import ListField
from motormongo.fields.string_field import StringField

class DataBase:
    client: AsyncIOMotorClient = None
    db = None

    @classmethod
    async def connect(cls, uri: str, db: str, **pooling_options):
        cls.client = AsyncIOMotorClient(uri or os.getenv("MONGODB_URL"), **pooling_options)
        cls.db = cls.client[str(db) or str(os.getenv("MONGODB_DB"))]
        await cls.initialize_indexes()

    @classmethod
    async def close(cls):
        if cls.client is not None:
            cls.client.close()
            cls.client = None
            cls.db = None


    @classmethod
    async def initialize_indexes(cls):
        for document_class in Document._registered_documents:
            await cls.create_indexes_for_document(document_class)

    @classmethod
    async def create_indexes_for_document(cls, document_class):
        if hasattr(document_class, 'Meta') and hasattr(document_class.Meta, 'indexes'):
            try:
                collection_name = document_class.get_collection_name()
                collection = cls.db[collection_name]
                for index in document_class.Meta.indexes:
                    fields = index['fields']
                    options = {k: v for k, v in index.items() if k != 'fields'}
                    await collection.create_index(fields, **options)
            except OperationFailure as e:
                if "index option" in str(e).lower() and "atlas tier" in str(e).lower():
                    # Issue a colored warning to the user
                    message = "\033[93mWarning: An index option used in a motormongo Document is either not supported" \
                              " by your MongoDB Atlas tier or does not exist. Consider upgrading MongoDB tier, or removing " \
                              "index definition on your Document class to remove this warning.\033[0m"
                    warnings.warn(message)
                else:
                    # If the error is for a different reason, you might want to re-raise the exception or handle it differently
                    raise

async def get_db():
    if DataBase.db is None:
        raise RuntimeError("Database not connected")
    return DataBase.db