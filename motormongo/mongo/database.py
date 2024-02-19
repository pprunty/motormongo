import os
import warnings

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
                uri or os.getenv("MONGODB_URL"), **pooling_options
            )
            cls.db = cls.client[str(db) or str(os.getenv("MONGODB_DB"))]
            await cls.initialize_indexes()
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

    @classmethod
    async def initialize_indexes(cls):
        for document_class in Document._registered_documents:
            await cls.create_indexes_for_document(document_class)

    @classmethod
    async def create_indexes_for_document(cls, document_class):
        global _options

        if hasattr(document_class, "Meta") and hasattr(document_class.Meta, "indexes"):
            try:
                collection_name = document_class.get_collection_name()
                collection = cls.db[collection_name]
                logger.debug(
                    f"Index list for collection '{collection_name}' = {document_class.Meta.indexes}"
                )
                for index in document_class.Meta.indexes:
                    fields = index["fields"]
                    _options = {k: v for k, v in index.items() if k != "fields"}
                    logger.debug(f"Fields = {fields} and options = {_options}")
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


async def get_db():
    if DataBase.db is None:
        raise RuntimeError("Database not connected")
    return DataBase.db
