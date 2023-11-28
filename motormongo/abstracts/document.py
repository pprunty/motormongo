import json
import os
import re
from datetime import datetime
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ReturnDocument
from motormongo.fields.datetime_field import DateTimeField
from motormongo.fields.field import Field
from typing import Any, Dict, List, Tuple, Union, Awaitable

DATABASE = "test"


def add_timestamps_if_required(cls, **kwargs):
    current_time = datetime.utcnow()
    if hasattr(cls, 'Meta'):
        if getattr(cls.Meta, 'created_at_timestamp', False) and 'created_at' not in kwargs:
            kwargs['created_at'] = current_time
        if getattr(cls.Meta, 'updated_at_timestamp', False) and 'updated_at' not in kwargs:
            kwargs['updated_at'] = current_time
    return kwargs


def camel_to_snake(name):
    """Convert CamelCase to snake_case."""
    name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()


class Document:
    """

    @classmethods:

    insert_one(document: dict | **kwargs) -> Object | error
    find_one(filter: dict | **kwargs) -> Object | None
    update_one(query: dict, update_fields: dict) -> Object | error
    delete_one(query: dict | **kwargs) -> boolean | error

    insert_many(List[document | **kwargs]) -> List[Object] | error
    find_many(filter) -> List[Object] | Object | None
    update_many(query, update_fields) -> List[Object] | Object | error
    delete_many(query) -> boolean | error

    find_one_or_create
    find_one_and_replace
    find_one_and_delete
    find_one_and_update_empty_fields(query, **kwargs) -> (Object, boolean)

    # TODO: Deal with inserting reference documents (look into how Metro handles this)

    object instance methods:

    save() -> void | error
    delete() -> void | error

    """

    db = AsyncIOMotorClient(os.getenv("MONGODB_URL"))[os.getenv("MONGODB_COLLECTION")]

    def __init__(self, **kwargs):
        self._id = None
        self.Meta = None
        self.__collection = self.get_collection_name()
        print(f"Creating class for collection {self.__collection}")

        if getattr(self.Meta, 'created_at_timestamp', False):
            self.created_at = DateTimeField(default=datetime.utcnow)
        if getattr(self.Meta, 'updated_at_timestamp', False):
            self.updated_at = DateTimeField(default=datetime.utcnow)

        # # Handling _id separately
        if '_id' in kwargs:
            print(f"Setting _id: {kwargs['_id']}")
            setattr(self, '_id', ObjectId(kwargs['_id']))

        # Setting other attributes
        for name, field in self.__class__.__dict__.items():
            print(f"field = {field} and name = {name}")
            if isinstance(field, Field):
                print(f"{name} -> {kwargs.get(name, field.options.get('default'))}")
                setattr(self, name, kwargs.get(name, field.options.get('default')))

        if 'created_at' not in kwargs:
            self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    @classmethod
    def get_collection_name(cls):
        if hasattr(cls, 'Meta') and hasattr(cls.Meta, 'collection'):
            return cls.Meta.collection
        return camel_to_snake(cls.__name__)

    @classmethod
    def convert_id(cls, query):
        if '_id' in query and not isinstance(query['_id'], ObjectId):
            try:
                query['_id'] = ObjectId(query['_id'])
            except Exception as e:
                raise ValueError(f"Invalid _id format: {e}")
        return query

    @classmethod
    async def insert_one(cls, document: dict = None, **kwargs):
        # Consolidate document creation
        document = {**(document or {}), **kwargs}
        document = add_timestamps_if_required(cls, **document)
        filtered_document = {k: v for k, v in document.items() if isinstance(getattr(cls, k, None), Field)}

        # Assuming db is a pre-existing database connection
        try:
            collection_name = cls.get_collection_name()
            result = await cls.db[collection_name].insert_one(filtered_document)
            inserted_document = await cls.db[collection_name].find_one({'_id': result.inserted_id})
            print(f"inserted document = {inserted_document}")
            return cls(**inserted_document)
        except Exception as e:
            raise ValueError(f"Error inserting document: {e}")

    @classmethod
    async def insert_many(cls, documents: List[Dict[str, Any]]) -> tuple[list['Document'], Any]:
        # First, process each document to ensure it adheres to the class's structure and add timestamps if necessary
        processed_documents = []
        for doc in documents:
            if isinstance(doc, dict):
                # Add timestamps and filter the fields based on the class structure
                doc_with_timestamps = add_timestamps_if_required(cls, **doc)
                filtered_document = {k: v for k, v in doc_with_timestamps.items() if
                                     isinstance(getattr(cls, k, None), Field)}
                processed_documents.append(filtered_document)
            else:
                raise ValueError("All items in the documents list must be dictionaries.")

        # Connect to the database and insert the documents
        try:
            collection_name = cls.get_collection_name()
            result = await cls.db[collection_name].insert_many(processed_documents)
            return [cls(**doc) for doc in processed_documents], result.inserted_ids
        except Exception as e:
            raise ValueError(f"Error inserting multiple documents: {e}")

    @classmethod
    async def find_one(cls, query) -> 'Document':
        query = cls.convert_id(query)
        try:
            document = await cls.db[cls.get_collection_name()].find_one(query)
            return cls(**document) if document else None
        except Exception as e:
            raise ValueError(f"Error finding document: {e}")

    @classmethod
    async def find_many(cls, filter: dict = None, limit: int = None) -> List['Document']:
        filter = filter or {}
        try:
            cursor = cls.db[cls.get_collection_name()].find(filter)
            if limit is not None:
                cursor = cursor.limit(limit)
            documents = await cursor.to_list(length=limit)
            return [cls(**doc) for doc in documents]
        except Exception as e:
            raise ValueError(f"Error finding documents: {e}")

    @classmethod
    async def update_one(cls, query: dict, update_fields: dict) -> 'Document':
        update_fields = add_timestamps_if_required(cls, **update_fields)
        query = cls.convert_id(query)
        update_fields.pop("_id", None)
        try:
            update_result = await cls.db[cls.get_collection_name()].find_one_and_update(
                query,
                {"$set": update_fields},
                return_document=ReturnDocument.AFTER
            )
            if update_result is not None:
                return cls(**update_result)
        except Exception as e:
            raise ValueError(f"Error updating document: {e}")

    @classmethod
    async def update_many(cls, query: dict, update_fields: dict) -> Tuple[List['Document'], Any] | Tuple[
        List[Any], int]:
        # First, add timestamps to the update fields if required
        update_fields = add_timestamps_if_required(cls, **update_fields)

        # The update fields should be structured as a MongoDB update operation
        update_operation = {"$set": update_fields}

        # Connect to the database and perform the update
        try:
            collection_name = cls.get_collection_name()
            result = await cls.db[collection_name].update_many(query, update_operation)

            # If you need to return the updated documents, you have to find them
            # Note: this may not be efficient for a large number of documents
            if result.modified_count > 0:
                updated_documents = await cls.db[collection_name].find(query).to_list(length=None)
                return [cls(**doc) for doc in updated_documents], result.modified_count
            else:
                return [], 0
        except Exception as e:
            raise ValueError(f"Error updating multiple documents: {e}")

    @classmethod
    async def find_one_or_create(cls, query: dict, defaults: dict = None) -> 'Document':
        document = await cls.db[cls.get_collection_name()].find_one(query)
        if document:
            return cls(**document)
        else:
            defaults = defaults or {}
            document = {**query, **defaults}
            return await cls.insert_one(document)

    @classmethod
    async def find_one_and_replace(cls, query: dict, replacement: dict) -> 'Document':
        replacement = add_timestamps_if_required(cls, **replacement)
        try:
            updated_document = await cls.db[cls.get_collection_name()].find_one_and_replace(
                query, replacement, return_document=ReturnDocument.AFTER
            )
            return cls(**updated_document) if updated_document else None
        except Exception as e:
            raise ValueError(f"Error replacing document: {e}")

    @classmethod
    async def find_one_and_update_empty_fields(cls, query: dict, **kwargs) -> Tuple['Document', bool] | Tuple[
        None, bool]:
        existing_doc = await cls.db[cls.get_collection_name()].find_one(query)
        if existing_doc:
            update_fields = {k: v for k, v in kwargs.items() if k not in existing_doc or not existing_doc[k]}
            if update_fields:
                updated_document = await cls.update_one(query, update_fields)
                return updated_document, True
            return cls(**existing_doc), False
        return None, False

    @classmethod
    async def find_one_and_delete(cls, query: dict) -> 'Document':
        try:
            deleted_document = await cls.db[cls.get_collection_name()].find_one_and_delete(query)
            return cls(**deleted_document) if deleted_document else None
        except Exception as e:
            raise ValueError(f"Error deleting document: {e}")

    async def save(self) -> None:
        if getattr(self.Meta, 'updated_at_timestamp', False):
            self.updated_at = datetime.utcnow()

        document = {k: v for k, v in self.__dict__.items() if not k.startswith('_')}

        try:
            if not hasattr(self, '_id'):
                result = await self.db[self.__collection].insert_one(document)
                self._id = result.inserted_id
            else:
                await self.db[self.__collection].replace_one({'_id': self._id}, document)
        except Exception as e:
            raise ValueError(f"Error saving document: {e}")

    async def delete(self) -> None:
        try:
            await self.db[self.__collection].delete_one({'_id': self._id})
        except Exception as e:
            raise ValueError(f"Error deleting document: {e}")

    @staticmethod
    def _json_encoder(obj):
        """Custom JSON encoder for handling complex types."""
        if isinstance(obj, ObjectId):
            return str(obj)  # Convert ObjectId to string
        # Add more custom encodings if necessary
        raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")

    def to_json(self):
        return json.dumps(self.to_dict(), default=self._json_encoder)

    def to_dict(self):
        """Convert document to a dictionary representation."""
        return {k: v for k, v in self.__dict__.items() if not k.startswith('__')}
