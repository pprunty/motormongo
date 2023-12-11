import json
import os
import re
from datetime import datetime
from enum import Enum

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ReturnDocument
from motormongo.fields.datetime_field import DateTimeField
from motormongo.fields.field import Field
from typing import Any, Dict, List, Tuple, Union, Awaitable
from motormongo import get_db

DATABASE = "test"


def add_timestamps_if_required(cls, operation: str = "update", **kwargs):
    current_time = datetime.utcnow()
    if hasattr(cls, 'Meta'):
        if getattr(cls.Meta, 'created_at_timestamp', False) and 'created_at' not in kwargs and operation != "update":
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
    _registered_documents = []

    def __init__(self, **kwargs):
        self.__collection = self.get_collection_name()
        print(f"Creating class for collection {self.__collection}")

        # Handling _id separately
        if '_id' in kwargs:
            print(f"Setting _id: {kwargs['_id']}")
            setattr(self, '_id', ObjectId(kwargs['_id']))

        # Setting other attributes
        for name, field in self.__class__.__dict__.items():
            print(f"field = {field} and name = {name}")
            if isinstance(field, Field):
                print(f"{name} -> {kwargs.get(name, field.options.get('default'))}")
                setattr(self, name, kwargs.get(name, field.options.get('default')))

        if 'created_at' in kwargs:
            self.created_at = kwargs.get("created_at")
        # # TODO: This should be set elsewhere?
        # self.updated_at = datetime.utcnow()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        Document._registered_documents.append(cls)

    @classmethod
    async def db(cls):
        return await get_db()

    # @property
    # def collection(self):
    #     return get_collection()

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

        # Initialize the instance
        try:
            instance = cls(**document)
        except TypeError as e:
            raise ValueError(f"Error initializing object: {e}")

        # Apply timestamps
        document_w_timestamps = add_timestamps_if_required(cls, operation="create", **instance.to_dict())

        print(f"document w timestamp = {document_w_timestamps}")

        try:
            collection_name = cls.get_collection_name()
            db = await cls.db()
            result = await db[collection_name].insert_one(document_w_timestamps)
            inserted_document = await db[collection_name].find_one({'_id': result.inserted_id})
            return cls(**inserted_document)
        except Exception as e:
            raise ValueError(f"Error inserting document: {e}")

    @classmethod
    async def insert_many(cls, documents: List[Dict[str, Any]]) -> tuple[list['Document'], Any]:
        # First, process each document to ensure it adheres to the class's structure and add timestamps if necessary
        processed_documents = []
        for doc in documents:
            if isinstance(doc, dict):
                # Initialize the instance
                try:
                    instance = cls(**doc)
                except TypeError as e:
                    raise ValueError(f"Error initializing object: {e}")
                # Apply timestamps
                document_w_timestamps = add_timestamps_if_required(cls, operation="create", **instance.to_dict())
                processed_documents.append(document_w_timestamps)
            else:
                raise ValueError("All items in the documents list must be dictionaries.")

        # Connect to the database and insert the documents
        try:
            db = await cls.db()
            collection = db[cls.get_collection_name()]
            result = await collection.insert_many(processed_documents)
            return [cls(**doc) for doc in processed_documents], result.inserted_ids
        except Exception as e:
            raise ValueError(f"Error inserting multiple documents: {e}")

    @classmethod
    async def find_one(cls, filter: dict = None, **kwargs) -> 'Document':
        filter = {**(filter or {}), **kwargs}
        filter = cls.convert_id(filter)
        try:
            db = await cls.db()
            collection = db[cls.get_collection_name()]
            document = await collection.find_one(filter)
            return cls(**document) if document else None
        except Exception as e:
            raise ValueError(f"Error finding document: {e}")

    @classmethod
    async def find_many(cls, filter: dict = None, limit: int = None, **kwargs) -> List['Document']:
        """
        Finds multiple documents matching the filter or keyword arguments.

        Args:
            filter (dict): The filter criteria for the query. Defaults to None.
            limit (int): The maximum number of documents to return. Defaults to None.
            **kwargs: Additional filter criteria as keyword arguments.

        Returns:
            List[Document]: A list of found documents, or an empty list if no matching documents are found.
        """
        filter = {**(filter or {}), **kwargs}
        try:
            db = await cls.db()
            collection = db[cls.get_collection_name()]
            cursor = collection.find(filter)
            if limit is not None:
                cursor = cursor.limit(limit)
            documents = await cursor.to_list(length=limit)
            return [cls(**doc) for doc in documents]
        except Exception as e:
            raise ValueError(f"Error finding documents: {e}")

    @classmethod
    async def update_one(cls, query: dict, update_fields: dict) -> 'Document':
        update_fields = add_timestamps_if_required(cls, **update_fields, operation="update")
        query = cls.convert_id(query)
        update_fields.pop("_id", None)
        try:
            db = await cls.db()
            collection = db[cls.get_collection_name()]
            update_result = await collection.find_one_and_update(
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
            db = await cls.db()
            collection = db[cls.get_collection_name()]
            result = await collection.update_many(query, update_operation)

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
    async def delete_one(cls, query: dict) -> bool:
        """
        Deletes a single document matching the query.

        Args:
            query (dict): The query to match the document to be deleted.

        Returns:
            bool: True if a document was deleted, False otherwise.
        """
        query = cls.convert_id(query)
        try:
            db = await cls.db()
            collection = db[cls.get_collection_name()]
            delete_result = collection.delete_one(query)
            return delete_result.deleted_count > 0
        except Exception as e:
            raise ValueError(f"Error deleting document: {e}")

    @classmethod
    async def delete_many(cls, query: dict) -> int:
        """
        Deletes multiple documents matching the query.

        Args:
            query (dict): The query to match the documents to be deleted.

        Returns:
            int: The count of documents that were deleted.
        """
        try:
            db = await cls.db()
            collection = db[cls.get_collection_name()]
            delete_result = await collection.delete_many(query)
            return delete_result.deleted_count
        except Exception as e:
            raise ValueError(f"Error deleting documents: {e}")

    @classmethod
    async def find_one_or_create(cls, query: dict, defaults: dict = None) -> 'Document':
        db = await cls.db()
        collection = db[cls.get_collection_name()]
        document = await collection.find_one(query)
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
            db = await cls.db()
            collection = db[cls.get_collection_name()]
            updated_document = await collection.find_one_and_replace(
                query, replacement, return_document=ReturnDocument.AFTER
            )
            return cls(**updated_document) if updated_document else None
        except Exception as e:
            raise ValueError(f"Error replacing document: {e}")

    @classmethod
    async def find_one_and_update_empty_fields(cls, query: dict, **kwargs) -> Tuple['Document', bool] | Tuple[
        None, bool]:
        db = await cls.db()
        collection = db[cls.get_collection_name()]
        existing_doc = await collection.find_one(query)
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
            db = await cls.db()
            collection = db[cls.get_collection_name()]
            deleted_document = await collection.find_one_and_delete(query)
            return cls(**deleted_document) if deleted_document else None
        except Exception as e:
            raise ValueError(f"Error deleting document: {e}")

    async def save(self) -> None:
        document = add_timestamps_if_required(self, operation="update", **self.to_dict())
        print(f"doc dict represenatuon = {document}")
        try:
            db = await self.db()
            collection = db[self.get_collection_name()]
            if not hasattr(self, '_id'):
                result = await collection.insert_one(document)
                self._id = result.inserted_id
            else:
                await collection.replace_one({'_id': self._id}, document)
        except Exception as e:
            raise ValueError(f"Error saving document: {e}")

    async def delete(self) -> None:
        try:
            db = await self.db()
            collection = db[self.get_collection_name()]
            await collection.delete_one({'_id': self._id})
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
        """Convert document to a dictionary representation, excluding keys
        that contain '__' anywhere in the name or are 'Meta'. Convert enums to their values."""
        return {
            k: (v.value if isinstance(v, Enum) else v) for k, v in self.__dict__.items()
            if "__" not in k and k != "Meta"
        }

