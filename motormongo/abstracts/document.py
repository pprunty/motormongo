import json
from datetime import timezone
from enum import Enum
from typing import Any, Dict, List, Tuple, Union

from bson import ObjectId
from pymongo import ReturnDocument

from motormongo.abstracts.exceptions import (
    DocumentAggregationError,
    DocumentDeleteError,
    DocumentInsertError,
    DocumentNotFoundError,
    DocumentUpdateError,
)
from motormongo.fields.field import Field
from motormongo.utils.formatter import (
    add_timestamps_if_required,
    camel_to_snake_or_lower,
    enforce_types,
)
from motormongo.utils.logging import logger


class DocumentMeta(type):
    """
    Metaclass for Document to automatically register subclasses
    for supporting polymorphism.
    """

    def __init__(cls, name, bases, attrs):
        super().__init__(name, bases, attrs)
        if not hasattr(cls, "_registered_documents"):
            cls._registered_documents = []
        else:
            cls._registered_documents.append(cls)
            logger.debug(f"Registered document class: {cls.__name__}")


class Document(metaclass=DocumentMeta):
    """
    A base class for MongoDB document models, providing methods for mongo operations.

    This class provides asynchronous methods for CRUD (Create, Read, Update, Delete) operations
    and other utility functions for working with MongoDB documents. It should be subclassed to
    create specific document models.

    Attributes:
        __collection (str): The name of the MongoDB collection associated with the model.
        _registered_documents (list): A class-level list that keeps track of all subclasses.

    Methods:
        __init__(self, **kwargs): Initialize a new document instance with the given attributes.
        __init_subclass__(cls, **kwargs): Class initialization hook for subclasses.
        db(cls): Asynchronously retrieves the Motor mongo client instance.
        get_collection_name(cls): Retrieves the collection name for the document class.
        convert_id(cls, query): Converts '_id' in the query to an ObjectId.
        insert_one(cls, document=None, **kwargs): Asynchronously inserts a single document.
        insert_many(cls, documents): Asynchronously inserts multiple documents.
        find_one(cls, filter=None, **kwargs): Asynchronously finds a single document.
        find_many(cls, filter=None, limit=None, **kwargs): Asynchronously retrieves multiple documents.
        update_one(cls, query, update_fields): Asynchronously updates a single document.
        update_many(cls, query, update_fields): Asynchronously updates multiple documents.
        delete_one(cls, query, **kwargs): Asynchronously deletes a single document.
        delete_many(cls, query, **kwargs): Asynchronously deletes multiple documents.
        find_one_or_create(cls, query, defaults): Asynchronously finds or creates a document.
        find_one_and_replace(cls, query, replacement): Asynchronously finds and replaces a document.
        find_one_and_update_empty_fields(cls, query, update_fields): Asynchronously updates empty fields in a document.
        find_one_and_delete(cls, query): Asynchronously finds and deletes a document.
        save(self): Asynchronously saves the current document instance.
        delete(self): Asynchronously deletes the current document instance.
        _json_encoder(obj): Custom JSON encoder for complex types.
        to_json(self): Converts the document to a JSON string.
        to_dict(self): Converts the document to a dictionary representation.
    """

    _registered_documents = []
    __type_field = "__type"  # Field to store the document's class type
    _fields = {}
    _indexes_created = (
        False  # Track whether indexes have been created for this Document subclass
    )

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
        self.__dict__[self.__type_field] = self.__class__.__name__
        # Logging the class creation
        logger.debug(f"Creating class for collection {self.__collection}")
        logger.debug(f"Creating class for collection {self.__collection}")

        # Handling '_id' separately
        if "_id" in kwargs:
            logger.debug(f"Setting _id: {kwargs['_id']}")
            setattr(self, "_id", ObjectId(kwargs["_id"]))

        for cls in reversed(self.__class__.__mro__):  # Iterate through the MRO
            for name, field in cls.__dict__.items():
                if isinstance(field, Field):
                    value = kwargs.get(name, field.options.get("default"))
                    if value is None and field.required:
                        raise ValueError(f"The field '{name}' is required.")
                    elif value is not None:
                        setattr(self, name, value)

        if "created_at" in kwargs:
            self.created_at = kwargs.get("created_at").replace(tzinfo=timezone.utc)
        if "updated_at" in kwargs:
            self.updated_at = kwargs.get("updated_at").replace(tzinfo=timezone.utc)

    def __init_subclass__(cls, **kwargs):
        """
        This method is a subclass initialization hook called whenever a subclass of 'Document' is created.

        Args:
            **kwargs: Arbitrary keyword arguments.

        Note:
            - This method registers each subclass in the '_registered_documents' list for tracking purposes.
        """
        super().__init_subclass__(**kwargs)
        cls._fields = {}
        for attr_name, attr_value in cls.__dict__.items():
            if isinstance(attr_value, Field):
                cls._fields[attr_name] = attr_value
                attr_value.__set_name__(cls, attr_name)
        Document._registered_documents.append(cls)

    @classmethod
    async def db(cls):
        from motormongo import get_db

        """
        Asynchronously retrieves the mongo client instance.

        Returns:
            The mongo client instance used by this document class.

        Note:
            - This is an asynchronous method and should be awaited.
        """
        return await get_db()

    @classmethod
    async def ensure_indexes(cls):
        from motormongo import DataBase

        subclasses = cls.__subclasses__()
        if subclasses:
            for subcls in subclasses:
                if not subcls._indexes_created:
                    await DataBase._create_indexes(subcls)
                    subcls._indexes_created = True
        else:
            if not cls._indexes_created:
                await DataBase._create_indexes(cls)
                cls._indexes_created = True

    @classmethod
    def get_collection_name(cls) -> Union[str, List[Tuple[object, str]]]:
        """
        Retrieves the collection name for the document class or a list of collection names for its subclasses,
        preferring explicitly defined collection names in the subclass's Meta attribute if available.

        Returns:
            Union[str, List[Tuple[object, str]]]: The collection name for the current class, or, if the class has subclasses,
                                    a list of collection names derived from either the subclass Meta attribute
                                    or the subclass names.
        """
        # Check for subclasses
        subclasses = cls.__subclasses__()
        if subclasses:
            # Initialize an empty list to store collection names for subclasses
            subclass_collection_names = []
            # Iterate over each subclass
            for subcls in subclasses:
                # Check for an explicitly defined collection name in the subclass's Meta attribute
                if hasattr(subcls, "Meta") and hasattr(subcls.Meta, "collection"):
                    subclass_collection_names.append((subcls, subcls.Meta.collection))
                else:
                    # If no explicit collection name is defined, convert the subclass name from CamelCase to snake_case
                    subclass_collection_names.append(
                        (subcls, camel_to_snake_or_lower(subcls.__name__))
                    )
            return subclass_collection_names

        if hasattr(cls, "Meta") and hasattr(cls.Meta, "collection"):
            return cls.Meta.collection

        # If no subclasses exist, return the snake_case collection name for the current class
        return camel_to_snake_or_lower(cls.__name__)

    @classmethod
    def convert_id(cls, query):
        """
        Converts the '_id' field in the query to an ObjectId, if necessary.

        Args:
            query (Dict): The query dictionary containing possibly a string '_id' field.

        Returns:
            Dict: The updated query with '_id' converted to ObjectId, if applicable.

        Raises:
            ValueError: If the '_id' format is invalid and cannot be converted to ObjectId.
        """
        for key, value in query.items():
            if isinstance(value, str):
                try:
                    query[key] = ObjectId(value)
                except Exception:
                    pass  # Ignore if the string cannot be converted to ObjectId
            elif isinstance(value, Dict):
                # Recursively convert for nested dictionaries
                query[key] = cls.convert_id(value)
        return query

    @classmethod
    async def insert_one(cls, document: Dict = None, **kwargs):
        """
        Asynchronously inserts a single document into the mongo.

        This method consolidates the provided `document` and any additional keyword
        arguments (`kwargs`) into a single document. It initializes an instance of
        the class with this document, applies any required timestamps, and then inserts
        it into the mongo. If the insertion is successful, it returns an instance of
        the class representing the inserted document.

        Usage:
            user = await MyClass.insert_one(name="johndoe")

            user = await MyClass.insert_one({"name": "johndoe", "age": 45})

            doc = {"name": "johndoe", "age": 45}
            user = await MyClass.insert_one(**doc)

        Args:
            document (Dict, optional): A dictionary representing the document to be inserted.
            **kwargs: Additional keyword arguments representing fields in the document.

        Returns:
            An instance of the class representing the inserted document.

        Raises:
            ValueError: If there is an error initializing the class instance or inserting the document into the mongo.
        """
        await cls.ensure_indexes()
        # Consolidate document creation
        document = {**(document or {}), **kwargs}

        logger.debug(f"document  = {document}")

        # Initialize the instance
        try:
            instance = cls.from_dict(**document)
        except TypeError as e:
            raise ValueError(f"Error initializing object: {e}")

        # Apply timestamps
        document_w_timestamps = add_timestamps_if_required(
            cls, operation="create", **instance.to_dict(id_as_string=False)
        )

        logger.debug(f"document w timestamp = {document_w_timestamps}")

        try:
            collection_name = cls.get_collection_name()
            db = await cls.db()
            result = await db[collection_name].insert_one(document_w_timestamps)
            inserted_document = await db[collection_name].find_one(
                {"_id": result.inserted_id}
            )
            logger.debug(f"__ insert = {inserted_document}")
            return cls.from_dict(**inserted_document)
        except Exception as e:
            raise DocumentInsertError(
                f"Error inserting {cls.__name__} document '{document}': {e}"
            )

    @classmethod
    async def insert_many(
        cls, documents: List[Dict[str, Any]]
    ) -> Tuple[List["Document"], Any]:
        """
        Asynchronously inserts multiple documents into the mongo collection associated with the class.

        This method first processes each document in the provided list to ensure it adheres
        to the class's structure and applies necessary timestamps. It then inserts these
        processed documents into the mongo collection and returns a tuple consisting of
        a list of class instances corresponding to the inserted documents and a list of
        their MongoDB-generated IDs.

        Args:
            documents (List[Dict[str, Any]]): A list of dictionaries where each dictionary
                                              represents a document to be inserted.

        Returns:
            Tuple[list['Document'], Any]: A tuple containing two elements. The first element
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
        await cls.ensure_indexes()
        # First, process each document to ensure it adheres to the class's structure and add timestamps if necessary
        processed_documents = []
        for doc in documents:
            if isinstance(doc, Dict):
                # Initialize the instance
                try:
                    instance = cls.from_dict(**doc)
                except TypeError as e:
                    raise ValueError(f"Error initializing object: {e}")
                # Apply timestamps
                document_w_timestamps = add_timestamps_if_required(
                    cls, operation="create", **instance.to_dict(id_as_string=False)
                )
                processed_documents.append(document_w_timestamps)
            else:
                raise ValueError(
                    "All items in the documents list must be dictionaries."
                )

        # Connect to the mongo and insert the documents
        try:
            db = await cls.db()
            collection = db[cls.get_collection_name()]
            result = await collection.insert_many(processed_documents)
            return [
                cls.from_dict(**doc) for doc in processed_documents
            ], result.inserted_ids
        except Exception as e:
            raise DocumentInsertError(
                f"Error inserting multiple {cls.__name__} documents '{documents}': {e}"
            )

    @classmethod
    async def find_one(cls, query: Dict = None, **kwargs) -> "Document":
        """
        Asynchronously finds a single document in the mongo collection that matches the given filter.

        Args:
            query (Dict, optional): A dictionary specifying the filter criteria for the query.
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
        await cls.ensure_indexes()
        filter = {**(query or {}), **kwargs}

        # Check if any value in the filter is a Document instance and replace it with its _id
        # todo: get this working
        for key, value in filter.items():
            if isinstance(value, Document) and hasattr(value, "_id"):
                filter[key] = value._id
            elif isinstance(value, Document) and not hasattr(value, "_id"):
                raise ValueError(
                    f"The document provided for '{key}' does not have an '_id'."
                )

        filter = cls.convert_id(filter)

        logger.debug(f"__filter = {filter}")

        try:
            db = await cls.db()
            collection = db[cls.get_collection_name()]
            document = await collection.find_one(filter)
            logger.debug(f"__doc rep = {document}")
            return cls.from_dict(**document) if document else None
        except Exception as e:
            raise DocumentNotFoundError(
                f"Error finding {cls.__name__} document with query '{filter}': {e}"
            )

    @classmethod
    async def find_many(
        cls,
        query: Dict = None,
        limit: int = None,
        return_as_list: bool = True,
        **kwargs,
    ) -> Union[List["Document"], List[Any], Any]:
        """
        Asynchronously retrieves multiple documents from one or more mongo collections that match the
        given filter and limit. Optionally, it can return an AsyncIOMotorCursor instead of a list for each collection.

        This method allows you to query multiple documents based on the filter criteria. It supports
        both a filter dictionary and additional keyword arguments. You can also specify a limit on
        the number of documents to retrieve and whether to return the results as a list or a cursor.

        Args:
            query (Dict, optional): A dictionary specifying the filter criteria for the query.
                                    Defaults to None.
            limit (int, optional): The maximum number of documents to return. Defaults to None,
                                   which means no limit.
            return_as_list (bool, optional): If True, returns a list of Documents. If False, returns a cursor.
                                             Defaults to True.
            **kwargs: Additional filter criteria specified as keyword arguments.

        Returns:
            Union[List["Document"], List[AsyncIOMotorCursor], Any]: Depending on return_as_list, either a list of class instances
                                                                    representing the found documents or an AsyncIOMotorCursor for each collection.
                                                                    Returns an empty list if no documents match the filter criteria
                                                                    and return_as_list is True.

        Raises:
            ValueError: If there is an error in finding the documents with the given filter.
        """
        await cls.ensure_indexes()
        filter = {**(query or {}), **kwargs}
        combined_results = (
            []
        )  # Initialize a list to store combined results from all collections

        try:
            db = await cls.db()
            collection_names = (
                cls.get_collection_name()
            )  # This might return a single name or a list of names

            if isinstance(collection_names, list):
                # If get_collection_name returns a list, iterate over each collection name
                for subcls, collection_name in collection_names:
                    collection = db[collection_name]
                    cursor = collection.find(filter)
                    if limit is not None:
                        cursor = cursor.limit(limit)
                    if return_as_list:
                        documents = await cursor.to_list(length=limit)
                        combined_results.extend(
                            [cls.from_dict(subcls=subcls, **doc) for doc in documents]
                        )
                    else:
                        combined_results.append(cursor)
            else:
                # Single collection name case
                collection = db[collection_names]
                cursor = collection.find(filter)
                if limit is not None:
                    cursor = cursor.limit(limit)
                if return_as_list:
                    documents = await cursor.to_list(length=limit)
                    combined_results = [cls.from_dict(**doc) for doc in documents]
                else:
                    combined_results = cursor

            return combined_results
        except Exception as e:
            logger.debug(
                f"Failed to retrieve documents for {cls.__name__} with query '{filter}': {str(e)}"
            )
            raise DocumentNotFoundError(
                f"Error finding {cls.__name__} documents with query '{filter}': {e}"
            )

    @classmethod
    async def update_one(cls, query: Dict, update_fields: Dict) -> "Document":
        """
        Asynchronously updates a single document in the mongo collection based on the provided query and update fields.

        This method finds a single document matching the query criteria and updates it with the specified fields.
        It returns the updated document as an instance of the class. The method also supports additional
        keyword arguments for further customization.

        Args:
            query (Dict): A dictionary specifying the filter criteria to identify the document to be updated.
            update_fields (Dict): A dictionary specifying the fields to be updated in the document.

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
        await cls.ensure_indexes()
        update_fields = add_timestamps_if_required(
            cls, **update_fields, operation="update"
        )
        query = cls.convert_id(query)
        for field in query.keys():
            update_fields.pop(field, None)

        try:
            logger.debug(f"__update_one instance 1 {update_fields}")
            instance = cls.from_dict(**update_fields)
            logger.debug(f"__update_one instance {instance.to_dict()}")
        except TypeError as e:
            raise ValueError(f"Error initializing object: {e}")

        try:
            db = await cls.db()
            collection = db[cls.get_collection_name()]
            update_result = await collection.find_one_and_update(
                query,
                {"$set": instance.to_dict(id_as_string=False)},
                return_document=ReturnDocument.AFTER,
            )
            if update_result is not None:
                return cls.from_dict(**update_result)
        except Exception as e:
            raise DocumentUpdateError(
                f"Error updating {cls.__name__} document with update fields '{update_fields}': {e}"
            )

    @classmethod
    async def update_many(
        cls, query: Dict, update_fields: Dict
    ) -> Union[Tuple[List["Document"], int], Tuple[List[Any], int]]:
        """
        Asynchronously updates multiple documents in one or more collections that match the given query.

        Args:
            query (Dict): The filter criteria to match documents that need to be updated.
            update_fields (Dict): The fields and their new values that will be set in the matched documents.

        Returns:
            Union[Tuple[List['Document'], int], Tuple[List[Any], int]]: A tuple containing a list of updated document objects and the count of documents modified.

        Raises:
            DocumentUpdateError: If there is an error in updating documents.
        """
        await cls.ensure_indexes()

        async def perform_update(collection, subcls=None):
            """
            Perform an update operation on a given collection and return the updated documents and their count.

            Args:
                collection: The collection to perform the update on.

            Returns:
                A tuple containing a list of updated documents and the count of documents modified.
            """
            result = await collection.update_many(query, {"$set": update_fields})
            if result.modified_count > 0:
                updated_documents = await collection.find(query).to_list(length=None)
                return [
                    cls.from_dict(subcls=subcls, **doc) for doc in updated_documents
                ], result.modified_count
            else:
                return [], 0

        try:
            db = await cls.db()
            collection_names = cls.get_collection_name()
            if isinstance(collection_names, list):
                combined_results = []
                total_modified = 0
                for subcls, collection_name in collection_names:
                    collection = db[collection_name]
                    updated_docs, modified_count = await perform_update(
                        collection=collection, subcls=subcls
                    )
                    combined_results.extend(updated_docs)
                    total_modified += modified_count
                return combined_results, total_modified
            else:
                collection = db[collection_names]
                return await perform_update(collection=collection)
        except Exception as e:
            raise DocumentUpdateError(
                f"Error updating {cls.__name__} documents with update fields '{update_fields}': {e}"
            )

    @classmethod
    async def delete_one(cls, query: Dict = None, **kwargs) -> bool:
        """
        Asynchronously deletes a single document from the mongo that matches the given query.

        Args:
            query (Dict): The filter criteria to match the document that needs to be deleted.
            **kwargs: Additional keyword arguments that will be merged into the query.

        Usage:
            # Delete a user with a specific ID
            await MyClass.delete_one({'_id': '507f191e810c19729de860ea'})

            # Delete a user with a specific name
            await MyClass.delete_one(name='John Doe')

        Returns:
            bool: True if a document was deleted, otherwise False.

        Raises:
            ValueError: If there is an error in deleting the document from the mongo.
        """
        await cls.ensure_indexes()
        # Consolidate document creation
        query = {**(query or {}), **kwargs}
        query = cls.convert_id(query)
        try:
            db = await cls.db()
            collection = db[cls.get_collection_name()]
            delete_result = await collection.delete_one(query)
            return delete_result.deleted_count > 0
        except Exception as e:
            raise DocumentDeleteError(
                f"Error deleting {cls.__name__} document with query '{query}': {e}"
            )

    @classmethod
    async def delete_many(cls, query: Dict = None, **kwargs) -> int:
        """
        Asynchronously deletes multiple documents from one or more collections that match the given query.

        Args:
            query (Dict, optional): The filter criteria to match the documents that need to be deleted.
            **kwargs: Additional keyword arguments that will be merged into the query or used as the query.

        Returns:
            int: The total number of documents deleted across all relevant collections.

        Raises:
            DocumentDeleteError: If there is an error in deleting the documents.
        """
        await cls.ensure_indexes()

        query = {**(query or {}), **kwargs}

        async def perform_deletion(collection):
            """
            Perform a deletion operation on a given collection and return the count of documents deleted.

            Args:
                collection: The collection to perform the deletion on.

            Returns:
                int: The number of documents deleted from the collection.
            """
            delete_result = await collection.delete_many(query)
            return delete_result.deleted_count

        try:
            db = await cls.db()
            collection_names = cls.get_collection_name()
            total_deleted = 0

            if isinstance(collection_names, list):
                for _, collection_name in collection_names:
                    collection = db[collection_name]
                    deleted_count = await perform_deletion(collection)
                    total_deleted += deleted_count
            else:
                collection = db[collection_names]
                total_deleted = await perform_deletion(collection)

            return total_deleted
        except Exception as e:
            raise DocumentDeleteError(
                f"Error deleting {cls.__name__} documents with query '{query}': {e}"
            )

    @classmethod
    async def find_one_or_create(
        cls, query: Dict, defaults: Dict
    ) -> Tuple["Document", bool]:
        enforce_types([(query, dict, "query"), (defaults, dict, "defaults")])
        """
        Asynchronously finds a single document matching the query. If no document is found, creates a new document with the specified defaults.

        Args:
            query (Dict): The filter criteria for the query.
            defaults (Dict, optional): Default values for the document if it needs to be created. Defaults to None.

        Usage:
            # Find a user by username or create a new one with default age
            user, created = await User.find_one_or_create({'username': 'johndoe'}, defaults={'age': 30})

        Returns:
            Tuple[Document, bool]: A tuple of the found or created document, and a boolean indicating whether the document was created (True) or retrieved (False).

        Raises:
            DocumentNotFoundError: If there is an error in finding the document.
            DocumentInsertError: If there is an error in creating the document.
        """
        await cls.ensure_indexes()

        try:
            db = await cls.db()
            collection = db[cls.get_collection_name()]
            document = await collection.find_one(query)

            if document:
                return cls.from_dict(**document), False  # Document found, not created
            else:
                defaults = defaults or {}
                new_document = {**query, **defaults}
                try:
                    created_document = await cls.insert_one(new_document)
                    return created_document, True  # Document created
                except Exception as e:
                    raise DocumentInsertError(
                        f"Error inserting {cls.__name__} document '{document}': {e}"
                    )
        except Exception as e:
            raise DocumentNotFoundError(
                f"Error finding {cls.__name__} document with query '{query}': {e}"
            )

    @classmethod
    async def find_one_and_replace(cls, query: Dict, replacement: Dict) -> "Document":
        """
        Asynchronously finds a single document and replaces it with the provided replacement document.

        Args:
            query (Dict): The filter criteria for the query.
            replacement (Dict): The new document to replace the existing one.

        Usage:
            # Replace a user's details
            replaced_user = await User.find_one_and_replace({'username': 'johndoe'}, {'username': 'johndoe', 'age': 35})

        Returns:
            Document: The replaced document.

        Raises:
            ValueError: If there is an error in replacing the document.
        """
        await cls.ensure_indexes()
        enforce_types([(query, dict, "query"), (replacement, dict, "replacement")])
        replacement = add_timestamps_if_required(cls, **replacement)
        try:
            db = await cls.db()
            collection = db[cls.get_collection_name()]
            updated_document = await collection.find_one_and_replace(
                query, replacement, return_document=ReturnDocument.AFTER
            )
            if updated_document:
                return cls.from_dict(**updated_document)
            else:
                raise DocumentNotFoundError(
                    f"Error finding {cls.__name__} document with query {query}."
                )
        except Exception as e:
            raise DocumentUpdateError(
                f"Error replacing {cls.__name__} document with query {query}: {e}"
            )

    @classmethod
    async def find_one_and_update_empty_fields(
        cls, query: Dict, update_fields: Dict
    ) -> Tuple["Document", bool]:
        """
        Asynchronously finds a single document matching the query and updates its empty fields with
        the provided values.

        Args:
            query (Dict): The filter criteria for the query.
            update_fields (Dict): The fields and their values to update if they are empty in the document.

        Usage:
            # Update the user's email and age if they are empty
            updated_user, updated = await MyClass.find_one_and_update_empty_fields(
                {'username': 'johndoe'},
                {'email': 'johndoe@example.com', 'age': 30}
            )

        Returns:
            Tuple[Document, bool]: A tuple of the updated document (or the original document if no update was performed),
                                    and a boolean indicating whether the document was updated (True) or not (False).

        Raises:
            ValueError: If there is an error in finding or updating the document.
        """
        await cls.ensure_indexes()
        enforce_types([(query, dict, "query"), (update_fields, dict, "update_fields")])
        try:
            db = await cls.db()
            collection = db[cls.get_collection_name()]
            existing_doc = await collection.find_one(query)

            if existing_doc:
                fields_to_update = {
                    k: v
                    for k, v in update_fields.items()
                    if k not in existing_doc or not existing_doc[k]
                }
                if fields_to_update:
                    updated_document = await cls.update_one(query, fields_to_update)
                    return updated_document, True  # Document updated
                return cls.from_dict(**existing_doc), False  # No update performed
            else:
                raise DocumentNotFoundError(
                    f"Error finding {cls.__name__} document with query {query}."
                )
        except DocumentNotFoundError:
            raise
        except Exception as e:
            raise DocumentUpdateError(
                f"Error updating empty fields of {cls.__name__} document with query {query}: {e}"
            )

    @classmethod
    async def find_one_and_delete(cls, query: Dict = None, **kwargs) -> "Document":
        """
        Asynchronously finds a single document matching the query and deletes it.

        Args:
            query (Dict): The filter criteria for the query.

        Usage:
            # Find and delete a user by username
            deleted_user = await User.find_one_and_delete({'username': 'johndoe'})

        Returns:
            Document: The deleted document, if found.

        Raises:
            ValueError: If there is an error in deleting the document.
        """
        await cls.ensure_indexes()
        query = {**(query or {}), **kwargs}
        try:
            db = await cls.db()
            collection = db[cls.get_collection_name()]
            deleted_document = await collection.find_one_and_delete(query)
            if deleted_document:
                return cls.from_dict(**deleted_document)
            else:
                raise DocumentNotFoundError(
                    f"Error finding {cls.__name__} document with query {query}."
                )
        except Exception as e:
            raise DocumentDeleteError(
                f"Error deleting {cls.__name__} document with query {query}: {e}"
            )

    async def save(self) -> None:
        """
        Asynchronously saves the current document instance to the mongo. If the document does not exist,
        it is inserted; otherwise, it is updated.

        This method applies timestamps as required and manages the document's `_id` attribute.

        Usage:
            user = User.find_one({'name': 'johndoe'})
            user.age = 45
            user.save()

        Raises:
            ValueError: If there is an error in saving the document to the mongo.
        """
        await self.ensure_indexes()
        document = self.to_dict(id_as_string=False)

        document = add_timestamps_if_required(
            self, operation="update" if hasattr(self, "_id") else "create", **document
        )
        logger.debug(f"doc = {document}")

        try:
            db = await self.db()
            collection = db[self.get_collection_name()]
            if not hasattr(self, "_id"):
                # This is a new document, insert it
                result = await collection.insert_one(document)
                self._id = result.inserted_id
                if hasattr(self, "Meta"):
                    if hasattr(self.Meta, "created_at_timestamp"):
                        self.created_at = document.get("created_at")
                    if hasattr(self.Meta, "updated_at_timestamp"):
                        self.updated_at = document.get("updated_at")
            else:
                # This is an existing document, replace it
                await collection.replace_one({"_id": self._id}, document)
                # Only update 'updated_at' for existing documents
                if hasattr(self, "Meta"):
                    if hasattr(self.Meta, "updated_at_timestamp"):
                        self.updated_at = document.get("updated_at")
        except Exception as e:
            raise DocumentInsertError(f"Error saving document '{document}': {e}")

    async def delete(self) -> None:
        """
        Asynchronously deletes the current document instance from the mongo based on its `_id`.

        Usage:
            user = User.find_one({'name': 'johndoe'})
            if user:
                user.delete()

        Raises:
            ValueError: If there is an error in deleting the document from the mongo.
        """
        await self.ensure_indexes()
        try:
            db = await self.db()
            collection = db[self.get_collection_name()]
            await collection.delete_one({"_id": self._id})
        except Exception as e:
            raise DocumentDeleteError(
                f"Error deleting {self.__name__} document '{self.to_dict()}': {e}"
            )

    @classmethod
    async def aggregate(
        cls,
        pipeline: List[Dict],
        return_as_list: bool = False,
    ) -> Union[List["Document"], List[Any], Any]:
        """
        Perform aggregation operations on the documents in one or more collections.

        Args:
            pipeline (list): A sequence of data aggregation operations.
            return_as_list (bool, optional): If True, returns a list of Documents. If False, returns a cursor.
                Defaults to False.

        Returns:
            Union[List["Document"], List[Any], Any]: Depending on return_as_list, either a list of class instances
                representing the documents resulting from the aggregation pipeline or an AsyncIOMotorCursor for each collection.
                Returns an empty list if no documents are found and return_as_list is True.

        Raises:
            DocumentAggregationError: If an error occurs during pipeline execution.
        """
        await cls.ensure_indexes()

        async def perform_aggregation(collection, subcls=None):
            """
            Perform aggregation on a single collection and process the results.

            Args:
                collection: The collection to perform aggregation on.

            Returns:
                The processed aggregation results, either as a list of documents or a cursor.
            """
            cursor = collection.aggregate(pipeline)
            if return_as_list:
                documents = await cursor.to_list(
                    length=None
                )  # Get all results without imposing a limit
                return [cls.from_dict(subcls=subcls, **doc) for doc in documents]
            else:
                return cursor

        combined_results = []
        try:
            db = await cls.db()
            collection_names = cls.get_collection_name()

            if isinstance(collection_names, list):
                for subcls, collection_name in collection_names:
                    collection = db[collection_name]
                    results = await perform_aggregation(
                        collection=collection, subcls=subcls
                    )
                    if return_as_list:
                        combined_results.extend(results)
                    else:
                        combined_results.append(results)
            else:
                collection = db[collection_names]
                results = await perform_aggregation(collection=collection)
                combined_results = results

            return combined_results
        except Exception as e:
            raise DocumentAggregationError(
                f"Error executing {cls.__name__} document pipeline with pipeline '{pipeline}': {e}"
            )

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
        raise TypeError(
            f"Object of type {obj.__class__.__name__} is not JSON serializable"
        )

    def to_json(self):
        """
        Converts the document to a JSON string.

        Returns:
            str: A JSON string representation of the document.
        """
        return json.dumps(self.to_dict(), default=self._json_encoder)

    @classmethod
    def _get_class_from_type(cls, type_name: str):
        """
        Finds the subclass based on the provided type name.

        Args:
            type_name (str): The name of the subclass as stored in the document's __type field.

        Returns:
            The class object corresponding to the type name, or None if no matching class is found.
        """
        if not type_name:
            logger.debug("No type name provided for _get_class_from_type.")
            return None

        for subclass in cls._registered_documents:
            if subclass.__name__ == type_name:
                logger.debug(
                    f"Found matching class '{type_name}' for document instantiation."
                )
                return subclass

        logger.warning(f"No matching class found for type name '{type_name}'.")
        return None

    @classmethod
    def from_dict(cls, subcls=None, **kwargs):
        """
        Factory method to instantiate objects of the correct subclass based on the document's
        __type field. This method ensures that each document is deserialized into an instance
        of the appropriate class.

        Returns:
            Document: An instance of the appropriate subclass of Document.
        """
        if subcls:
            return subcls(**kwargs)
        else:
            return cls(**kwargs)

    def to_dict(self, id_as_string=True):
        """
        Converts the document to a dictionary representation, including type information
        and using field-specific __get__ methods for serialization where applicable.

        Args:
            id_as_string (bool, optional): If True, converts ObjectId instances to strings.
                                           Defaults to True.

        Returns:
            Dict: A dictionary representation of the document.
        """
        from motormongo.abstracts.embedded_document import EmbeddedDocument

        doc_dict = {}
        for k, v in self.__dict__.items():
            if "__" not in k and k != "Meta":
                # Use custom serialization logic as before
                value = str(v) if id_as_string and isinstance(v, ObjectId) else v
                if isinstance(v, Enum):
                    value = v.value
                elif isinstance(v, EmbeddedDocument):
                    value = v.to_dict()
                # Assign the processed value to the key in the dictionary
                doc_dict[k] = value
        # Ensure the class type (__type) is included in the dictionary
        # todo: might need to add this back for polymorphism
        # doc_dict[self.__type_field] = self.__class__.__name__
        # Ensure '_id' is processed according to id_as_string flag
        if "_id" in self.__dict__:
            doc_dict["_id"] = str(self._id) if id_as_string else self._id

        return doc_dict
