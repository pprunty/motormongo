import os
import warnings
from pymongo import ASCENDING
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import OperationFailure

from motormongo.abstracts.document import Document
from motormongo.utils.logging import logger


class DataBase:
    client: AsyncIOMotorClient = None
    db = None

    @classmethod
    async def connect(cls, uri: str, db: str, **pooling_options):

        try:
            cls.client = AsyncIOMotorClient(
                uri, **pooling_options
            )
            cls.db = cls.client[str(db)]
            # await cls.initialize_indexes()
        except Exception as e:
            raise RuntimeError(
                f"Error connecting to MongoDB database: {e}.\nEnsure URI follows the format: "
                f"mongodb+srv://<username>:<password>@<cluster>.mongodb.net and specified "
                f"db exists."
            )

    @classmethod
    async def close(cls):
        if cls.client is not None:
            cls.client.close()
            cls.client = None
            cls.db = None

    # @classmethod
    # async def initialize_indexes(cls):
    #     for document_class in Document._registered_documents:
    #         await cls.create_indexes_for_document(document_class)

    @classmethod
    async def create_indexes_for_document(cls, document_class):
        global _options
        collection_name = document_class.get_collection_name()
        collection = cls.db[collection_name]
        logger.debug(f"Creating indexes for MongoDB document collection: {collection_name}.")
        # Automatically create unique indexes for fields marked as unique
        for field_name, field_instance in document_class._fields.items():
            if getattr(field_instance, 'unique', False):
                try:
                    await collection.create_index([(field_name, ASCENDING)], unique=True)
                    logger.debug(f"Unique index created for '{field_name}' in '{collection_name}'.")
                except Exception as e:
                    raise ValueError(
                        f"Error creating unique index on field: '{field_name}' in collection: '{collection_name}'.from "
                        f"There are already duplicate values for {field_name} in the collection: {e}")

        if hasattr(document_class, "Meta") and hasattr(document_class.Meta, "indexes"):
            logger.debug(f"Index list for collection '{collection_name}' = {document_class.Meta.indexes}")
            for index in document_class.Meta.indexes:
                try:
                    fields = index["fields"]
                    _options = {k: v for k, v in index.items() if k != "fields"}
                    logger.debug(f"Creating index for fields = {fields} and options = {_options}")
                    await collection.create_index(fields, **_options)
                except OperationFailure as e:
                    if "index option" in str(e).lower() and "atlas tier" in str(e).lower():
                        # Issue a colored warning to the user
                        message = (
                            f"\033[93mWarning: An index option '{_options}' used in a motormongo Document is either not supported"
                            " by your MongoDB Atlas tier, or does not exist. Consider upgrading MongoDB tier, or removing "
                            "index definition on your Document class to remove this warning.\033[0m"
                        )
                        warnings.warn(message)
                    else:
                        # Log or handle other types of OperationFailure if necessary
                        logger.error(f"Error creating index for fields = {fields} and options = {_options}: {e}")

    @classmethod
    async def _create_indexes(cls, document_instance):
        print(f"CREATE INDEXES FOR {document_instance.__name__}")
        document_class = document_instance.__class__
        if issubclass(document_instance, Document):
            if not document_instance._indexes_created:
                await cls.create_indexes_for_document(document_class=document_instance)
                document_class._indexes_created = True
                logger.debug(f"Indexes created for {document_class.__name__}")


async def get_db():
    if DataBase.db is None:
        raise RuntimeError("Database not connected")
    return DataBase.db
