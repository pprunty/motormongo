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

        try:
            cls.client = AsyncIOMotorClient(uri, **pooling_options)
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

    @classmethod
    async def remove_outdated_indexes(
            cls, document_class, defined_indexes, existing_indexes
    ):
        # Identify indexes that need to be removed
        indexes_to_remove = set(existing_indexes) - set(defined_indexes)

        collection_name = document_class.get_collection_name()
        collection = cls.db[collection_name]

        for index_name in indexes_to_remove:
            if index_name not in [
                "_id_"
            ]:  # Avoid dropping the default index on the _id field
                logger.debug(
                    f"Removing outdated index '{index_name}' from '{collection_name}'."
                )
                await collection.drop_index(index_name)

    @classmethod
    async def create_indexes_for_document(cls, document_class):  # noqa: C901
        collection_name = document_class.get_collection_name()
        collection = cls.db[collection_name]
        logger.debug(
            f"Creating indexes for MongoDB document collection: {collection_name}."
        )

        # Retrieve existing indexes
        existing_indexes = await cls.get_existing_indexes(collection)
        defined_indexes = set()

        # Automatically create unique indexes for fields marked as unique
        for field_name, field_instance in document_class._fields.items():
            if getattr(field_instance, "unique", False):
                index_name = f"{field_name}_unique"
                defined_indexes.add(index_name)  # Add to defined_indexes
                if index_name not in existing_indexes:
                    try:
                        await collection.create_index(
                            [(field_name, ASCENDING)], unique=True, name=index_name
                        )
                        logger.debug(
                            f"Unique index created for '{field_name}' in '{collection_name}'."
                        )
                    except Exception as e:
                        raise ValueError(
                            f"Error creating unique index on field: '{field_name}' in collection: '{collection_name}'. "
                            f"There are already duplicate values for {field_name} in the collection: {e}"
                        )
                else:
                    logger.debug(
                        f"Index '{index_name}' already exists for '{field_name}' in '{collection_name}'."
                    )

        # Create other specified indexes based on Meta class
        if hasattr(document_class, "Meta") and hasattr(document_class.Meta, "indexes"):
            logger.debug(
                f"Index list for collection '{collection_name}' = {document_class.Meta.indexes}"
            )
            for index in document_class.Meta.indexes:
                try:
                    fields_input = index["fields"]
                    # Normalize fields to a format suitable for create_index
                    fields = [
                        (f, ASCENDING) if isinstance(f, str) else f
                        for f in fields_input
                    ]
                    _options = {k: v for k, v in index.items() if k != "fields"}
                    index_name = _options.get(
                        "name", "_".join([str(f[0]) for f in fields])
                    )
                    defined_indexes.add(index_name)  # Add to defined_indexes
                    if index_name not in existing_indexes:
                        logger.debug(
                            f"Creating index for fields = {fields} and options = {_options}"
                        )
                        await collection.create_index(fields, **_options)
                    else:
                        logger.debug(
                            f"Index '{index_name}' already exists and won't be recreated."
                        )
                except OperationFailure as e:
                    cls.handle_operation_failure(e, _options)

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
            message = (
                f"\033[93mWarning: An index option '{_options}' used in a motormongo Document is either not supported"
                " by your MongoDB Atlas tier, or does not exist. Consider upgrading MongoDB tier, or removing "
                "index definition on your Document class to remove this warning.\033[0m"
            )
            warnings.warn(message)
        else:
            logger.error(f"Error creating index: {e}")

    @classmethod
    async def _create_indexes(cls, document_instance):
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
