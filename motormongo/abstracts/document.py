import json
import re
from datetime import datetime
from enum import Enum

from bson import ObjectId
from pymongo import ReturnDocument
from motormongo.fields.field import Field
from typing import Any, Dict, List, Tuple
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
        """
        Initializes a new instance of the Document class with given attributes.

        This method sets various attributes based on the provided keyword arguments.
        It handles the '_id' attribute separately and sets other attributes dynamically.

        Args:
            **kwargs: Arbitrary keyword arguments which represent the attributes of the document.

        Note:
            - The 'created_at' attribute is set if provided in the keyword arguments.
        """
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
        """
        This method is a subclass initialization hook called whenever a subclass of 'Document' is created.

        Args:
            **kwargs: Arbitrary keyword arguments.

        Note:
            - This method registers each subclass in the '_registered_documents' list for tracking purposes.
        """
        super().__init_subclass__(**kwargs)
        Document._registered_documents.append(cls)

    @classmethod
    async def db(cls):
        """
        Asynchronously retrieves the database client instance.

        Returns:
            The database client instance used by this document class.

        Note:
            - This is an asynchronous method and should be awaited.
        """
        return await get_db()

    @classmethod
    def get_collection_name(cls):
        """
        Retrieves the collection name for the document class.

        Returns:
            str: The collection name. If defined in the class's 'Meta' attribute, it uses that;
                 otherwise, converts the class name from CamelCase to snake_case.
        """
        if hasattr(cls, 'Meta') and hasattr(cls.Meta, 'collection'):
            return cls.Meta.collection
        return camel_to_snake(cls.__name__)

    @classmethod
    def convert_id(cls, query):
        """
        Converts the '_id' field in the query to an ObjectId, if necessary.

        Args:
            query (dict): The query dictionary containing possibly a string '_id' field.

        Returns:
            dict: The updated query with '_id' converted to ObjectId, if applicable.

        Raises:
            ValueError: If the '_id' format is invalid and cannot be converted to ObjectId.
        """
        if '_id' in query and not isinstance(query['_id'], ObjectId):
            try:
                query['_id'] = ObjectId(query['_id'])
            except Exception as e:
                raise ValueError(f"Invalid _id format: {e}")
        return query

    @classmethod
    async def insert_one(cls, document: dict = None, **kwargs):
        """
        Asynchronously inserts a single document into the database.

        This method consolidates the provided `document` and any additional keyword
        arguments (`kwargs`) into a single document. It initializes an instance of
        the class with this document, applies any required timestamps, and then inserts
        it into the database. If the insertion is successful, it returns an instance of
        the class representing the inserted document.

        Usage:
            user = await MyClass.insert_one(name="johndoe")

            user = await MyClass.insert_one({"name": "johndoe", "age": 45})

            doc = {"name": "johndoe", "age": 45}
            user = await MyClass.insert_one(**doc)

        Args:
            document (dict, optional): A dictionary representing the document to be inserted.
            **kwargs: Additional keyword arguments representing fields in the document.

        Returns:
            An instance of the class representing the inserted document.

        Raises:
            ValueError: If there is an error initializing the class instance or inserting the document into the database.
        """
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
    async def insert_many(cls, documents: List[Dict[str, Any]]) -> tuple[List['Document'], Any]:
        """
        Inserts multiple documents into the database collection associated with the class.

        This method first processes each document in the provided list to ensure it adheres
        to the class's structure and applies necessary timestamps. It then inserts these
        processed documents into the database collection and returns a tuple consisting of
        a list of class instances corresponding to the inserted documents and a list of
        their MongoDB-generated IDs.

        Args:
            documents (List[Dict[str, Any]]): A list of dictionaries where each dictionary
                                              represents a document to be inserted.

        Returns:
            tuple[list['Document'], Any]: A tuple containing two elements. The first element
                                          is a list of instances of the class corresponding
                                          to the inserted documents. The second element is
                                          a list of MongoDB-generated IDs for these documents.

        Raises:
            ValueError: If any of the items in the documents list is not a dictionary, or if
                        there is an error initializing an object with the given dictionary.

        Examples:
            docs_to_insert = [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]
            inserted_docs, inserted_ids = await MyClass.insert_many(docs_to_insert)
        """
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
        """
        Finds a single document in the database collection that matches the given filter.

        This method combines the provided filter dictionary and any additional keyword arguments
        to form the search criteria. It returns an instance of the class that represents the
        found document, or None if no document matches the criteria.

        Args:
            filter (dict, optional): A dictionary specifying the filter criteria for the query.
                                     Defaults to None.
            **kwargs: Additional filter criteria specified as keyword arguments.

        Returns:
            Document or None: An instance of the class representing the found document, or None
                              if no document matches the filter criteria.

        Raises:
            ValueError: If there is an error in finding the document with the given filter.

        Examples:
            user = await MyClass.find_one(name="johndoe")
            user = await MyClass.find_one({"name": "johndoe", "age": 45})
            filter_criteria = {"name": "johndoe", "age": 45}
            user = await MyClass.find_one(**filter_criteria)

        Note:
            If both filter and keyword arguments are provided, they are combined for the query.
        """
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
        Retrieves multiple documents from the database collection that match the given filter and limit.

        This method allows you to query multiple documents based on the filter criteria. It supports
        both a filter dictionary and additional keyword arguments. You can also specify a limit on
        the number of documents to retrieve.

        Args:
            filter (dict, optional): A dictionary specifying the filter criteria for the query.
                                     Defaults to None.
            limit (int, optional): The maximum number of documents to return. Defaults to None,
                                   which means no limit.
            **kwargs: Additional filter criteria specified as keyword arguments.

        Returns:
            List[Document]: A list of class instances representing the found documents. Returns an
                            empty list if no documents match the filter criteria.

        Raises:
            ValueError: If there is an error in finding the documents with the given filter.

        Examples:
            await MyClass.find_many(age={"$gt": 40}, alive=False, limit=20)
            filter_criteria = {"age": {"$gt": 40}, "alive": False}
            await MyClass.find_many(**filter_criteria, limit=20)

        Note:
            - The `filter` argument and keyword arguments are combined for the query.
            - The `limit` argument restricts the number of returned documents.
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
        """
            Updates a single document in the database collection based on the provided query and update fields.

            This method finds a single document matching the query criteria and updates it with the specified fields.
            It returns the updated document as an instance of the class. The method also supports additional
            keyword arguments for further customization.

            Args:
                query (dict): A dictionary specifying the filter criteria to identify the document to be updated.
                update_fields (dict): A dictionary specifying the fields to be updated in the document.

            Returns:
                Document: An instance of the class representing the updated document. Returns None if no document
                          matches the query criteria or if the update operation fails.

            Raises:
                ValueError: If there is an error in updating the document with the given criteria.

            Examples:
                await MyClass.update_one({"_id": "unique_id"}, {"name": "new_name", "age": 30})
                query_criteria = {"name": "old_name"}
                update_data = {"name": "updated_name"}
                await MyClass.update_one(query_criteria, update_data)

            Note:
                - The `update_fields` should not include the '_id' field as it is automatically popped from the update data.
            """
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
        """
        Updates multiple documents in the database that match the given query.

        Args:
            query (dict): The filter criteria to match documents that need to be updated.
            update_fields (dict): The fields and their new values that will be set in the matched documents.

        Usage:
            # Update all users aged over 40 to set a new field 'category' to 'senior'
            await MyClass.update_many({'age': {'$gt': 40}}, {'category': 'senior'})

            # Update users named 'John Doe' to increase their age by 1
            await MyClass.update_many({'name': 'John Doe'}, {'$inc': {'age': 1}})

        Returns:
            Tuple[List['Document'], int]: A tuple containing a list of updated document objects and the count of documents modified.

        Raises:
            ValueError: If there is an error in updating documents in the database.
        """
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
    async def delete_one(cls, query: dict, **kwargs) -> bool:
        """
        Deletes a single document from the database that matches the given query.

        Args:
            query (dict): The filter criteria to match the document that needs to be deleted.
            **kwargs: Additional keyword arguments that will be merged into the query.

        Usage:
            # Delete a user with a specific ID
            await MyClass.delete_one({'_id': '507f191e810c19729de860ea'})

            # Delete a user with a specific name
            await MyClass.delete_one(name='John Doe')

        Returns:
            bool: True if a document was deleted, otherwise False.

        Raises:
            ValueError: If there is an error in deleting the document from the database.
        """
        # Consolidate document creation
        query = {**(query or {}), **kwargs}
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
        Deletes multiple documents from the database that match the given query.

        Args:
            query (dict): The filter criteria to match the documents that need to be deleted.

        Usage:
            # Delete all users older than 40
            deleted_count = await MyClass.delete_many({'age': {'$gt': 40}})

            # Delete all users with a specific status
            deleted_count = await MyClass.delete_many({'status': 'inactive'})

        Returns:
            int: The number of documents deleted from the database.

        Raises:
            ValueError: If there is an error in deleting the documents from the database.
        """
        try:
            db = await cls.db()
            collection = db[cls.get_collection_name()]
            delete_result = await collection.delete_many(query)
            return delete_result.deleted_count
        except Exception as e:
            raise ValueError(f"Error deleting documents: {e}")

    @classmethod
    async def find_one_or_create(cls, query: dict, defaults: dict = None) -> Tuple['Document', bool]:
        """
        Finds a single document matching the query. If no document is found, creates a new document with the specified defaults.

        Args:
            query (dict): The filter criteria for the query.
            defaults (dict, optional): Default values for the document if it needs to be created. Defaults to None.

        Usage:
            # Find a user by username or create a new one with default age
            user, created = await User.find_one_or_create({'username': 'johndoe'}, defaults={'age': 30})

        Returns:
            Tuple[Document, bool]: A tuple of the found or created document, and a boolean indicating whether the document was created (True) or retrieved (False).

        Raises:
            ValueError: If there is an error in finding or creating the document.
        """

        db = await cls.db()
        collection = db[cls.get_collection_name()]
        document = await collection.find_one(query)

        if document:
            return cls(**document), False  # Document found, not created
        else:
            defaults = defaults or {}
            new_document = {**query, **defaults}
            created_document = await cls.insert_one(new_document)
            return created_document, True  # Document created

    @classmethod
    async def find_one_and_replace(cls, query: dict, replacement: dict) -> 'Document':
        """
        Finds a single document and replaces it with the provided replacement document.

        Args:
            query (dict): The filter criteria for the query.
            replacement (dict): The new document to replace the existing one.

        Usage:
            # Replace a user's details
            replaced_user = await User.find_one_and_replace({'username': 'johndoe'}, {'username': 'johndoe', 'age': 35})

        Returns:
            Document: The replaced document.

        Raises:
            ValueError: If there is an error in replacing the document.
        """
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
    async def find_one_and_update_empty_fields(cls, query: dict, update_fields: dict) -> Tuple['Document', bool]:
        """
        Finds a single document matching the query and updates its empty fields with the provided values.

        Args:
            query (dict): The filter criteria for the query.
            update_fields (dict): The fields and their values to update if they are empty in the document.

        Usage:
            # Update the user's email and age if they are empty
            updated_user, updated = await User.find_one_and_update_empty_fields(
                {'username': 'johndoe'},
                {'email': 'johndoe@example.com', 'age': 30}
            )

        Returns:
            Tuple[Document, bool]: A tuple of the updated document (or the original document if no update was performed),
                                    and a boolean indicating whether the document was updated (True) or not (False).

        Raises:
            ValueError: If there is an error in finding or updating the document.
        """
        db = await cls.db()
        collection = db[cls.get_collection_name()]
        existing_doc = await collection.find_one(query)

        if existing_doc:
            fields_to_update = {k: v for k, v in update_fields.items() if k not in existing_doc or not existing_doc[k]}
            if fields_to_update:
                updated_document = await cls.update_one(query, fields_to_update)
                return updated_document, True  # Document updated
            return cls(**existing_doc), False  # No update performed
        return None, False  # Document not found

    @classmethod
    async def find_one_and_delete(cls, query: dict) -> 'Document':
        """
        Finds a single document matching the query and deletes it.

        Args:
            query (dict): The filter criteria for the query.

        Usage:
            # Find and delete a user by username
            deleted_user = await User.find_one_and_delete({'username': 'johndoe'})

        Returns:
            Document: The deleted document, if found.

        Raises:
            ValueError: If there is an error in deleting the document.
        """
        try:
            db = await cls.db()
            collection = db[cls.get_collection_name()]
            deleted_document = await collection.find_one_and_delete(query)
            return cls(**deleted_document) if deleted_document else None
        except Exception as e:
            raise ValueError(f"Error deleting document: {e}")

    async def save(self) -> None:
        """
        Saves the current document instance to the database. If the document does not exist, it is inserted;
        otherwise, it is updated.

        This method applies timestamps as required and manages the document's `_id` attribute.

        Usage:
            user = User.find_one({'name': 'johndoe'})
            user.age = 45
            user.save()

        Raises:
            ValueError: If there is an error in saving the document to the database.
        """
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
        """
        Deletes the current document instance from the database based on its `_id`.

        Usage:
            user = User.find_one({'name': 'johndoe'})
            if user:
                user.delete()

        Raises:
            ValueError: If there is an error in deleting the document from the database.
        """
        try:
            db = await self.db()
            collection = db[self.get_collection_name()]
            await collection.delete_one({'_id': self._id})
        except Exception as e:
            raise ValueError(f"Error deleting document: {e}")

    @staticmethod
    def _json_encoder(obj):
        """
        Custom JSON encoder for handling complex types like ObjectId.

        Args:
            obj: The object to encode.

        Returns:
            str: A JSON serializable representation of `obj`.

        Raises:
            TypeError: If the object is not JSON serializable.
        """
        if isinstance(obj, ObjectId):
            return str(obj)  # Convert ObjectId to string
        # Add more custom encodings if necessary
        raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")

    def to_json(self):
        """
        Converts the document to a JSON string.

        Returns:
            str: A JSON string representation of the document.
        """
        return json.dumps(self.to_dict(), default=self._json_encoder)

    def to_dict(self):
        """
        Converts the document to a dictionary representation.

        This method excludes keys that contain '__' anywhere in their name or are 'Meta'.
        Enum values are converted to their corresponding values.

        Returns:
            dict: A dictionary representation of the document.
        """
        return {
            k: (v.value if isinstance(v, Enum) else v) for k, v in self.__dict__.items()
            if "__" not in k and k != "Meta"
        }

