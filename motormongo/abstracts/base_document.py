import json
import re
from datetime import datetime

from bson import ObjectId
from fastapi import HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ReturnDocument

from motormongo.fields.datetime_field import DateTimeField
from motormongo.fields.field import Field

DATABASE = "test"


def camel_to_snake(name):
    """Convert CamelCase to snake_case."""
    name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()


class Document:
    def __init__(self, **kwargs):
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
    async def find_one(cls, query):
        # Convert _id to ObjectId if necessary
        if '_id' in query:
            if not isinstance(query['_id'], ObjectId):
                try:
                    query['_id'] = ObjectId(query['_id'])
                except Exception as e:
                    raise ValueError(f"Invalid _id format: {e}")
        try:
            db = AsyncIOMotorClient("mongodb+srv://pprunty:Cracker123!@cluster0.7o5omuv.mongodb.net")[DATABASE]
            document = await db[cls.get_collection_name()].find_one(query)
            return cls(**document) if document else None
        except Exception as e:
            print(f"Error finding document: {e}")
            return None

    async def save(self):
        if getattr(self.Meta, 'updated_at_timestamp', False):
            self.updated_at = datetime.datetime.utcnow()
        try:
            db = AsyncIOMotorClient("mongodb+srv://pprunty:Cracker123!@cluster0.7o5omuv.mongodb.net")[DATABASE]
            print(f"Retrieved db: {db}")
            document = {k: v for k, v in self.__dict__.items() if not k.startswith('_')}
            if not hasattr(self, '_id'):
                print(f"attempting to save document for collection: {self.__collection}")
                result = await db[self.__collection].insert_one(document)
                self._id = result.inserted_id
            else:
                await db[self.__collection].replace_one({'_id': self._id}, document)
        except Exception as e:
            print(f"Error saving document: {e}")

    @classmethod
    async def update_one(cls, query: dict, update_fields: dict):
        print(f"query = {query} and update_fields = {update_fields}")
        if '_id' in query:
            if not isinstance(query['_id'], ObjectId):
                try:
                    query['_id'] = ObjectId(query['_id'])
                except Exception as e:
                    raise ValueError(f"Invalid _id format: {e}")
        update_fields.pop("_id", None)
        try:
            db = AsyncIOMotorClient("mongodb+srv://pprunty:Cracker123!@cluster0.7o5omuv.mongodb.net")[DATABASE]
            update_result = await db[cls.get_collection_name()].find_one_and_update(
                query,
                {"$set": update_fields},
                return_document=ReturnDocument.AFTER,
            )
            if update_result is not None:
                return cls(**update_result)
            else:
                raise HTTPException(status_code=404, detail=f"Student {id} not found")
        except Exception as e:
            print(f"Error updating document: {e}")

    async def delete(self):
        try:
            db = AsyncIOMotorClient("mongodb+srv://pprunty:Cracker123!@cluster0.7o5omuv.mongodb.net")[DATABASE]
            await db[self.__collection].delete_one({'_id': self._id})
        except Exception as e:
            print(f"Error deleting document: {e}")

    def to_json(self):
        return json.dumps(self.to_dict(), default=self._json_encoder)

    def to_dict(self):
        """Convert document to a dictionary representation."""
        return {k: v for k, v in self.__dict__.items() if not k.startswith('__')}

    @staticmethod
    def _json_encoder(obj):
        """Custom JSON encoder for handling complex types."""
        if isinstance(obj, ObjectId):
            return str(obj)  # Convert ObjectId to string
        # Add more custom encodings if necessary
        raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")
