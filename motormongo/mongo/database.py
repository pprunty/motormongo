import warnings

from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ASCENDING
from pymongo.errors import OperationFailure

from motormongo.abstracts.document import Document
from motormongo.utils.logging import logger


class DataBase:
    client: AsyncIOMotorClient = None
    db = None

    @classmethod
    async def connect(cls, uri: str, db: str, **pooling_options):
        logger.info(f"Attempting to connect to MongoDB at {uri}")
        try:
            cls.client = AsyncIOMotorClient(uri, **pooling_options)
            cls.db = cls.client[str(db)]
            for document in Document.__subclasses__():
                await document.ensure_indexes()
            logger.info(f"Successfully connected to MongoDB database '{db}'.")
        except Exception as e:
            logger.error(
                f"Error connecting to MongoDB database: {e}.\nEnsure URI follows the format: "
                f"mongodb+srv://<username>:<password>@<cluster>.mongodb.net and specified "
                f"db exists."
            )
            raise RuntimeError(f"Error connecting to MongoDB: {e}")

    @classmethod
    async def close(cls):
        if cls.client is not None:
            logger.info(f"Closing connection to MongoDB database '{cls.db}'.")
            cls.client.close()
            cls.client = None
            cls.db = None

    @classmethod
    async def remove_outdated_indexes(
        cls, document_class, defined_indexes, existing_indexes
    ):
        indexes_to_remove = set(existing_indexes) - set(defined_indexes)
        collection_name = document_class.get_collection_name()

        for index_name in indexes_to_remove:
            if index_name not in [
                "_id_"
            ]:  # Avoid dropping the default index on the _id field
                logger.debug(
                    f"Removing outdated index '{index_name}' from '{collection_name}'."
                )
                await cls.db[collection_name].drop_index(index_name)

    @classmethod
    async def create_indexes_for_document(cls, document_class):
        logger.debug(f"Creating indexes for document '{document_class.__name__}'.")

        collection_name = document_class.get_collection_name()
        existing_indexes = await cls.get_existing_indexes(cls.db[collection_name])
        defined_indexes = set()

        for field_name, field_instance in document_class._fields.items():
            if getattr(field_instance, "unique", False):
                index_name = f"{field_name}_unique"
                defined_indexes.add(index_name)
                if index_name not in existing_indexes:
                    logger.debug(
                        f"Creating unique index '{index_name}' on '{field_name}' in '{collection_name}'."
                    )
                    await cls.db[collection_name].create_index(
                        [(field_name, ASCENDING)],
                        unique=True,
                        name=index_name,
                        background=True,
                    )

        if hasattr(document_class, "Meta") and hasattr(document_class.Meta, "indexes"):
            for index in document_class.Meta.indexes:
                fields = index["fields"]
                options = {k: v for k, v in index.items() if k != "fields"}
                index_name = options.pop(
                    "name",
                    "_".join([f[0] if isinstance(f, tuple) else f for f in fields]),
                )

                if index_name not in existing_indexes:
                    logger.debug(
                        f"Creating index '{index_name}' in '{collection_name}' with options: {options}"
                    )
                    try:
                        await cls.db[collection_name].create_index(
                            fields, **options, background=True
                        )
                    except OperationFailure as e:
                        logger.warning(f"Failed to create index '{index_name}': {e}")

        await cls.remove_outdated_indexes(
            document_class, defined_indexes, existing_indexes.keys()
        )

    @classmethod
    async def get_existing_indexes(cls, collection):
        existing_indexes = {}
        async for index in collection.list_indexes():
            existing_indexes[index["name"]] = index
        return existing_indexes

    @classmethod
    def handle_operation_failure(cls, e, _options):
        if "index option" in str(e).lower() and "atlas tier" in str(e).lower():
            warnings.warn(
                "An index option used is either not supported by your MongoDB Atlas tier or does not exist. "
                "Consider upgrading your MongoDB Atlas tier or removing the index definition."
            )
        else:
            logger.error(f"Operation failure during index creation: {e}")

    @classmethod
    async def _create_indexes(cls, document_class: object):
        if issubclass(document_class, Document):
            if not document_class._indexes_created:
                await cls.create_indexes_for_document(document_class=document_class)
                document_class._indexes_created = True
                logger.info(
                    f"Indexes created successfully for Document: {document_class}"
                )
            else:
                logger.info(
                    f"Indexes were already create for Document: {document_class}"
                )


async def get_db():
    if DataBase.db is None:
        raise RuntimeError("Database not connected")
    return DataBase.db
