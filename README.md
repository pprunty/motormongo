| Description             | Badge                                                                                                             |
|-------------------------|-------------------------------------------------------------------------------------------------------------------|
| **PyPI - Version**      | [![PyPI - Version](https://img.shields.io/pypi/v/motormongo)](https://pypi.org/project/motormongo/)               |
| **Downloads**           | [![Downloads](https://static.pepy.tech/badge/motormongo/month)](https://pepy.tech/project/motormongo)            |
| **PyPI License**        | [![PyPI License](https://img.shields.io/pypi/l/motormongo.svg)](https://pypi.org/project/motormongo/)            |
| **GitHub Contributors** | [![GitHub Contributors](https://img.shields.io/github/contributors/pprunty/motormongo.svg)](https://github.com/pprunty/motormongo/graphs/contributors) |
| **Code Coverage**       | [![codecov](https://codecov.io/gh/pprunty/motormongo/graph/badge.svg?token=XSNQ1ZBWIF)](https://codecov.io/gh/pprunty/motormongo) |
| **Code Style**          | ![code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)                                 |

[//]: # ([![PyPI - Downloads]&#40;https://img.shields.io/pypi/dm/motormongo&#41;]&#40;https://pypi.org/project/motormongo/&#41;)

Author: [Patrick Prunty](https://pprunty.github.io/pprunty/).

`motormongo` - An Object Document Mapper (ODM) for [MongoDB](https://www.mongodb.com) built on top
of [`motor`](https://github.com/mongodb/motor), the MongoDB
recommended asynchronous Python driver for MongoDB Python applications, designed to work with Tornado or
asyncio and enable non-blocking access to MongoDB.

Asynchronous operations in a backend system, built using [FastAPI](https://github.com/tiangolo/fastapi) for
example, enhances performance and scalability by enabling non-blocking, concurrent handling of multiple I/O requests,
leading to more efficient use of server resources, by forcing the CPU usage on the backend server's main thread to be
maximized across concurrent requests. For more low-level details on the advantages of asynchronous `motormongo` over
existing MongoDB ODMs, such as `mongoengine` [see here](#why-use-motormongo).

The interface for instantiating Document classes follows similar logic
to [`mongoengine`](https://github.com/MongoEngine/mongoengine), enabling ease-of-transition and
migration from `mongoengine` to the asynchronous `motormongo`.

1. [Installation](#installation)
2. [Quickstart](#quickstart)
3. [Why use motormongo?](#why-use-motormongo)
4. [motormongo Fields](#motormongo-fields)
5. [CRUD classmethods](#class-methods)
6. [CRUD instance methods](#instance-methods)
7. [Aggregation Operations](#aggregation)
8. [Polymorphism and Inheritance](#polymorphism-and-inheritance)
9. [Pooling Options and Configuration](#pooling-options-configuration)
10. [FastAPI integration](#fastapi-integration)
11. [License](#license)

## Installation

To install `motormongo`, you can use `pip` inside your virtual environment:

```shell
python -m pip install motormongo
```

Alternatively, to install `motormongo` into your `poetry` environment:

```shell
poetry add motormongo
```

## Quickstart

### Step 1. Create a motormongo client:

```python
import asyncio
from motormongo import DataBase


async def init_db():
    # This 'connect' method needs to be called inside of an async function
    await DataBase.connect(uri="<mongo_uri>", database="<mongo_database>")


if __name__ == "__main__":
    asyncio.run(init_db())
```

or, in a FastAPI application:

```python
from fastapi import FastAPI
from motormongo import DataBase

app = FastAPI()


@app.on_event("startup")
async def startup_db_client():
    await DataBase.connect(uri="<mongo_uri>", db="<mongo_database>")


@app.on_event("shutdown")
async def shutdown_db_client():
    await DataBase.close()
```

The `mongo_uri` should look something like this:

```text
mongodb+srv://<username>:<password>@<cluster>.mongodb.net
```

and `database` should be the name of an existing MongoDB database in your MongoDB instance.

For details on how to set up a local or cloud MongoDB database instance,
see [here](https://www.mongodb.com/cloud/atlas/lp/try4?utm_source=google&utm_campaign=search_gs_pl_evergreen_atlas_general_prosp-brand_gic-null_emea-ie_ps-all_desktop_eng_lead&utm_term=using%20mongodb&utm_medium=cpc_paid_search&utm_ad=p&utm_ad_campaign_id=9510384711&adgroup=150907565274&cq_cmp=9510384711&gad_source=1&gclid=Cj0KCQiAyeWrBhDDARIsAGP1mWQ6B0kPYX9Tqmzku-4r-uUzOGL1PKDgSTlfpYeZ0I6HE3C-dgh1xF4aArHqEALw_wcB).

You can also specify and pass `pooling_options` to the Motor on the `DataBase.connect()` method, like so:

```python
import asyncio
from motormongo import DataBase

# Example pooling options
pooling_options = {
    'maxPoolSize': 50,
    'minPoolSize': 10,
    'maxIdleTimeMS': 30000,
    'waitQueueTimeoutMS': 5000,
    'connectTimeoutMS': 10000,
    'socketTimeoutMS': 20000
}


async def init_db():
    # This 'connect' method needs to be called inside of an async function
    await DataBase.connect(uri="<mongo_uri>", database="<mongo_database>", **pooling_options)


if __name__ == "__main__":
    asyncio.run(init_db())
```

See [Pooling Options Configuration](#pooling-options-configuration) section for more details.

### Step 2. Define a motormongo Document:

Define a `motormongo` `User` document:

```python
import re
import bcrypt
from motormongo import Document, BinaryField, StringField


def hash_password(password: str) -> bytes:
    # Example hashing function
    return bcrypt.hashpw(password.encode('utf-8'), salt=bcrypt.gensalt())


class User(Document):
    username = StringField(help_text="The username for the user", min_length=3, max_length=50)
    email = StringField(help_text="The email for the user", regex=re.compile(r'^\S+@\S+\.\S+$'))  # Simple email regex
    password = BinaryField(help_text="The hashed password for the user", hash_function=hash_password)

    def verify_password(self, password: str) -> bool:
        """ Utility function which can be used to validate user's salted password later...
        
        ex.     user = await User.find_one({"_id": request.user_id})
                is_authenticated = user.verify_password(request.password)
        """
        return bcrypt.checkpw(password.encode("utf-8"), self.password)

    class Meta:
        collection = "users"  # < If not provided, will default to class name (ex. User->user, UserDetails->user_details)
        created_at_timestamp = True  # < Provide a DateTimeField for document creation
        updated_at_timestamp = True  # < Provide a DateTimeField for document updates
```

### Step 3: Create a MongoDB document using the User class

```python
import bcrypt

await User.insert_one(
    {
        "username": "johndoe",
        "email": "johndoe@portmarnock.ie",
        "password": "password123"
        # < hash_functon will hash the string literal password and store binary field in the database
    }
)
```

### Step 4: Validate user was created in your MongoDB collection

You can do this by using [MongoDB compass](https://www.mongodb.com/products/tools/compass) GUI, or alternatively, add a
query to find all documents in the user
collection after doing the insert in step 3:

```python
users = User.find_many({})
if users:
    print("User collection contains the following documents:")
    for user in users:
        print(user.to_dict())
else:
    print("User collection failed to update! Check your MongoDB connection details and try again!")
```

### Step 5: Put all the code above into one file and run it

```shell
python main.py
```

or in a FastAPI application:

```shell
uvicorn main:app --reload
```

Please refer to [FastAPI Documentation](https://fastapi.tiangolo.com/tutorial/) for more details on how to get setup
with FastAPI.

## Congratulations 🎉

You've successfully created your first `motormongo` Object Document Mapper class. 🥳

The subsequent sections detail the datatype fields provided by `motormongo`, as well as the CRUD
operations available on the classmethods and object instance methods of a `motormongo` document.

If you wish to get straight into how to integrate `motormongo` with your `FastAPI` application, skip ahead to the
[FastAPI Integration](#fastapi-integration) section.

## Why use motormongo?

Integrating `motormongo`, an asynchronous Object-Document Mapper (ODM) for MongoDB, into a backend built with an
asynchronous web framework like `FastAPI`, enhances the system's ability to handle I/O-bound operations efficiently.
Using the `await` keyword with `motormongo` operations allows the event loop to manage concurrent requests effectively,
freeing up the main thread to handle other tasks while waiting for database operations to complete.

### Understanding the Efficiency of Asynchronous Operations

#### Traditional Approach with `pymongo` and `mongoengine` (Synchronous)

Typically, a web server handling multiple requests that involve fetching documents from MongoDB would face bottlenecks
with synchronous database operations:

```python
from fastapi import FastAPI, HTTPException
from mongoengine import connect, Document, StringField
from fastapi.encoders import jsonable_encoder

connect(db="testdb", host="mongodb://localhost:27017/", alias="default")


class User(Document):
    name = StringField(required=True)


app = FastAPI()


@app.get("/get_data/")
async def get_data(name: str):
    user = User.objects(name=name).first()
    if user:
        return jsonable_encoder(user.to_mongo().to_dict())
    else:
        raise HTTPException(status_code=404, detail="User not found")
```

In this setup, operations such as `User.objects(name=name).first()` block the thread until completion, hindering the
server's ability to process other requests concurrently, leading to inefficient resource use and potential performance
bottlenecks.

#### Asynchronous Approach with `motor` and `motormongo`

Switching to an asynchronous ODM like `motormongo` allows FastAPI to handle database operations without blocking:

```python
from fastapi import FastAPI
from motormongo import DataBase, Document, StringField


class User(Document):
    name = StringField(required=True)


app = FastAPI()


@app.on_event("startup")
async def startup_db_client():
    await DataBase.connect(uri="mongodb://localhost:27017/", db="testdb")


@app.get("/get_data/")
async def get_data(name: str):
    user = await User.find_one({'name': name})
    if user:
        return user.to_dict()
    else:
        return {"message": "User not found"}
```

Using `await` with `motormongo` operations such as `User.find_one()` allows the application to perform non-blocking
database operations. This asynchronous model is particularly advantageous for I/O-bound applications, allowing the
server to handle multiple requests efficiently by utilizing Python's `asyncio`.

### Maximizing Performance with Multiple FastAPI Workers

To further enhance the performance of FastAPI applications utilizing `motormongo`, deploying multiple worker processes
can significantly increase the application's ability to handle high volumes of concurrent requests:

- **Scalability**: Deploying FastAPI with multiple workers enables the application to scale across multiple CPU cores,
  offering better handling of concurrent requests by running multiple instances of the application, each in its own
  process.
- **Resource Utilization**: More workers mean that the application can utilize more system resources, effectively
  distributing the load and preventing any single worker from becoming a bottleneck.
- **Deployment Strategy**: Use an ASGI server like `uvicorn` with the `--workers` option to specify the number of worker
  processes. For example, `uvicorn app:app --workers 4` would run the application with four worker processes.

By leveraging `motormongo` with FastAPI, developers can build backend systems capable of handling asynchronous I/O-bound
operations efficiently. This setup not only improves the application's responsiveness and throughput by utilizing the
asynchronous capabilities of Python's `asyncio` but also maximizes performance through the strategic deployment of
multiple workers. Together, these strategies enable the creation of highly scalable, efficient, and modern web
applications.

## motormongo Fields

`motormongo` supports a variety of field types to accurately define the schema of your MongoDB documents. Each field
type is designed to handle specific data types and validations:

- [BinaryField](#binaryfield): Stores binary data, useful for storing encoded or hashed data like passwords.
- [BooleanField](#booleanfield): Stores boolean values (`True` or `False`).
- [DateTimeField](#datetimefield): Manages date and time, with options for automatically setting current date/time on
  creation or update.
- [EmbeddedDocumentField](#embeddeddocumentfield): For fields that should contain values from a predefined enumeration.
- [EnumField](#enumfield): For fields that should contain values from a predefined enumeration.
- [FloatField](#floatfield): Handles floating-point numbers, with options to specify minimum and maximum values.
- [GeoJSONField](#geojsonfield): Manages geographical data in GeoJSON format, with an option to return data as JSON.
- [IntegerField](#integerfield): Manages integer data, allowing specifications for minimum and maximum values.
- [ListField](#listfield): Handles lists of items, which can be of any type.
- [ReferenceField](#referencefield): Creates a reference to another document.
- [StringField](#stringfield): Handles string data with options for minimum and maximum length, and regex validation.

### BinaryField

The `BinaryField` is designed for storing binary data within a database. It offers capabilities for encoding, hashing,
and decoding data, making it versatile for handling various types of binary data, including but not limited to encrypted
or hashed content.

**Parameters:**

- `hash_function`: (Optional) A callable that hashes input data. The function should have a type annotation to indicate
  whether it expects a `str` or `bytes` as input. This annotation is crucial as it dictates whether the `BinaryField`
  should encode the string before hashing. If the annotation indicates `str`, the field will pass the string directly to
  the `hash_function`. If `bytes`, the `BinaryField` will encode the string (using the provided `encode` function or
  default UTF-8 encoding) before hashing.
- `return_decoded`: (Optional) A boolean indicating whether to decode binary data when it is retrieved from the
  database. If set to `True`, the stored binary data will be decoded back into a string using the provided `decode`
  function or default UTF-8 decoding. This is useful for data that was encoded but not hashed, as hashed data cannot be
  meaningfully decoded.
- `encode`: (Optional) A function to encode a string to bytes before storage. If not provided, the class defaults to
  UTF-8 encoding. This function is used when the input data is a string and needs to be stored as binary data, or before
  hashing if the `hash_function` expects `bytes`.
- `decode`: (Optional) A function to decode bytes back to a string when data is retrieved from the database. This
  parameter is only relevant if `return_decoded` is `True`. If not provided, the class defaults to UTF-8 decoding.

**Important**: For the `hash_function` to work correctly with the `BinaryField`, it must include type annotations for
its parameters. This enables the `BinaryField` to determine the correct processing strategy (i.e., whether to encode the
string before hashing).

### Example Usage:

```python
from motormongo import Document, BinaryField, StringField
import bcrypt


# Hash function with type annotation indicating it expects a 'str'
def hash_password(password: str) -> bytes:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())


class User(Document):
    username = StringField(min_length=3, max_length=50)
    # Note: 'hash_function' requires a type annotation
    password = BinaryField(hash_function=hash_password, return_decoded=False)

    def verify_password(self, password: str) -> bool:
        # Verifies if the provided password matches the stored hash
        return bcrypt.checkpw(password.encode("utf-8"), self.password)


# Creating a user instance with a hashed password
user = User(username="johndoe", password="secret")
inserted_user = await user.save()

# Authentication checks
is_authenticated = inserted_user.verify_password("wrongpassword")  # Expected to return False
is_authenticated = inserted_user.verify_password("secret")  # Expected to return True
```

### BooleanField

The `BooleanField` is used for storing boolean values (True or False). It ensures that the data stored in this field is
strictly boolean.

**Parameters:**

- There are no specific parameters unique to BooleanField other than those inherited from the base Field class.

```python
from motormongo import Document, BooleanField, StringField


class Product(Document):
    name = StringField(min_length=1, max_length=100)
    is_available = BooleanField(default=False)


# Create a product indicating its availability
product = Product(name="Gadget", is_available=True)
await product.save()
```

### DateTimeField

The `DateTimeField` handles date and time values, with options to automatically update these values on document creation
or modification.

**Parameters:**

- `auto_now`: Automatically update the field to the current datetime when the document is saved.
- `auto_now_add`: Automatically set the field to the current datetime when the document is created.
- `datetime_formats`: List of string formats to parse datetime strings.

**Example Usage:**

```python
from motormongo import Document, DateTimeField


class Event(Document):
    start_time = DateTimeField(auto_now_add=True)


# Create an event with the current start time
event = Event()
await event.save()
```

### EmbeddedDocumentField

The `EmbeddedDocumentField` is used for embedding documents within a document, supporting nested document structures.
This field allows you to include complex data structures as part of your document.

**Parameters:**

- `document_type`: The class of the embedded document, which must be a subclass of `EmbeddedDocument`, `BaseModel` from
  Pydantic, or `dict` representation of the `EmbeddedDocument`.

**Example Usage:**

```python
from motormongo import Document, EmbeddedDocument, EmbeddedDocumentField, StringField
from pydantic import BaseModel


class Address(EmbeddedDocument):
    street = StringField()
    city = StringField()


class User(Document):
    name = StringField()
    address = EmbeddedDocumentField(document_type=Address)


class PydanticAddress(BaseModel):
    street: str
    city: str


# Create a user with an embedded address document
user = User(name="John Doe", address={"street": "123 Elm St", "city": "Springfield"})
# user = User(name="John Doe", address=Address(street="123 Elm St", city="Springfield")) # Also works
# user = User(name="John Doe", address=PydanticAddress(street="123 Elm St", city="Springfield")) # Also works
await user.save()
```

### EnumField

The `EnumField` is designed to store enumerated values, allowing for validation against a predefined set of options.

**Parameters:**

- `enum`: The enumeration class that defines valid values for the field.

**Example Usage:**

```python
import enum
from motormongo import Document, EnumField


class UserStatus(enum.Enum):
    ACTIVE = 'active'
    INACTIVE = 'inactive'
    BANNED = 'banned'


class User(Document):
    status = EnumField(enum=UserStatus)


# Create a user and set their status using the EnumField
user = User(status=UserStatus.ACTIVE)
# user = User(status="active") # Also works
await user.save()
```

### FloatField

The `FloatField` handles floating-point numbers, with options to specify minimum and maximum values.

**Parameters:**

- `min_value`: (Optional) The minimum allowable value.
- `max_value`: (Optional) The maximum allowable value.

**Example Usage:**

```python
from motormongo import Document, FloatField


class Measurement(Document):
    temperature = FloatField(min_value=-273.15)  # Absolute zero constraint


# Record a temperature measurement
measurement = Measurement(temperature=25.5)
await measurement.save()
```

### GeoJSONField

The `GeoJSONField` is designed for storing geographical coordinates in GeoJSON format.

**Parameters:**

- `return_as_list`: (Optional) If `True`, returns the coordinates as a [longitude, latitude] list instead of a GeoJSON
  object.

**Example Usage:**

```python
from motormongo import Document, GeoJSONField


class Location(Document):
    point = GeoJSONField()


# Create a location point
location = Location(point={"type": "Point", "coordinates": [-73.856077, 40.848447]})  # Could also use 
# location = Location(point=[-73.856077, 40.848447]) # This would also work
await location.save()
```

### IntegerField

The `IntegerField` is used for storing integer values, with optional validation for minimum and maximum values.

**Parameters:**

- `min_value`: (Optional) The minimum allowable value.
- `max_value`: (Optional) The maximum allowable value.

**Example Usage:**

```python
from motormongo import Document, IntegerField


class Product(Document):
    quantity = IntegerField(min_value=0)


# Create a product with quantity validation
product = Product(quantity=10)
await product.save()
```

### ListField

The `ListField` is used for storing a list of items, optionally validating the type of items in the list.

**Parameters:**

- `field`: (Optional) A `Field` instance specifying the type of items in the list.

**Example Usage:**

```python
from motormongo import Document, ListField, StringField


class ShoppingList(Document):
    items = ListField(field=StringField())


# Create a shopping list with string items
shopping_list = ShoppingList(items=["Milk", "Eggs", "Bread"])
await shopping_list.save()
```

### ReferenceField

The `ReferenceField` is used to create a reference to another document, typically for creating relationships between
collections.

**Parameters:**

- `document_class`: The class of the document to which the field references.

**Example Usage:**

```python
from motormongo import Document, ReferenceField, StringField


class User(Document):
    name = StringField()


class Post(Document):
    author = ReferenceField(document_class=User)


# Create a user and a post referencing the user
user = User(name="John Doe")
await user.save()
post = Post(author=user)
```

To fetch the referenced document, you must await the coroutine returned by accessing the reference field. This operation
asynchronously retrieves the related document instance from the database.

```python
# Assuming `post` is an instance of the Post document with a reference to a User
# Fetch the user referenced by the post's author field
referenced_user = await post.author
if referenced_user:
    print("Referenced User:",
          referenced_user.to_dict())  # Should print, {'_id': '65d8bf2dad3fa2e9169d2f94', 'name': 'John Doe'}
else:
    print("User not found or failed to fetch.")
```

This example demonstrates how to access and asynchronously fetch the document referenced by a `ReferenceField`. The
await
keyword is crucial because the operation is asynchronous, involving a database query to retrieve the referenced
document.

**Note:** Ensure that the fetching operation is performed within an asynchronous context, such as an async function. The
ReferenceField provides a powerful way to manage relationships between documents, enabling complex data models with
interconnected documents.

### StringField

The `StringField` is used for storing string data in a document. It supports validation for minimum and maximum length
and can enforce a specific regex pattern.

**Parameters:**

- `min_length`: (Optional) The minimum length of the string.
- `max_length`: (Optional) The maximum length of the string.
- `regex`: (Optional) A regex pattern that the string must match.

**Example Usage:**

```python
from motormongo import Document, StringField


class UserProfile(Document):
    username = StringField(min_length=3, max_length=50)
    bio = StringField(max_length=200, regex=r'^[A-Za-z0-9 ]*$')  # Alphanumeric and space only


# Create a user profile with validation
profile = UserProfile(username="user123", bio="I love coding.")
await profile.save()
```

## Class methods

## Operations

The following class methods are supported by `motormongo`'s `Document` class:

| CRUD Type | Operation                                                                                                                          |
|-----------|------------------------------------------------------------------------------------------------------------------------------------|
| Create    | [`insert_one(document: dict, **kwargs) -> Document`](#insert_one)                                                                  |
| Create    | [`insert_many(documents: List[dict]) -> Tuple[List[Document], Any]`](#insert_many)                                                 |
| Read      | [`find_one(query: dict, **kwargs) -> Document`](#find_one)                                                                         |
| Read      | [`find_many(query: dict, limit: int = None, return_as_list: bool = True **kwargs) -> List[Document]`](#find_many)                  |
| Update    | [`update_one(query: dict, update_fields: dict) -> Document`](#update_one)                                                          |
| Update    | [`update_many(query: dict, update_fields: dict) -> Tuple[List[Document], int]`](#update_many)                                      |
| Delete    | [`delete_one(query: dict, **kwargs) -> bool`](#delete_one)                                                                         |
| Delete    | [`delete_many(query: dict, **kwargs) -> int`](#delete_many)                                                                        |
| Mixed     | [`find_one_or_create(query: dict, defaults: dict) -> Tuple[Document, bool]`](#find_one_or_create)                                  |
| Mixed     | [`find_one_and_replace(query: dict, replacement: dict) -> Document`](#find_one_and_replace)                                        |
| Mixed     | [`find_one_and_delete(query: dict) -> Document`](#find_one_and_delete)                                                             |
| Mixed     | [`find_one_and_update_empty_fields(query: dict, update_fields: dict) -> Tuple[Document, bool]`](#find_one_and_update_empty_fields) |

All examples below assume `User` is a subclass of `motormongo` provided Document class.

### Create

#### <a name="insert_one"></a> `insert_one(document: dict, **kwargs) -> Document`

Inserts a single document into the database.

```python
user = await User.insert_one({
    "name": "John",
    "age": 24,
    "alive": True
})
```

Alternatively, using `**kwargs`:

```python
user = await User.insert_one(
    name="John",
    age=24,
    alive=True)
```

And similarly, with a dictionary:

```python
user_document = {
    "name": "John",
    "age": 24,
    "alive": True
}
user = await User.insert_one(**user_document)
```

#### <a name="insert_many"></a> `insert_many(List[document]) -> tuple[List['Document'], Any]`

```python
users, user_ids = await User.insert_many(
    [
        {
            "name": "John",
            "age": 24,
            "alive": True
        },
        {
            "name": "Mary",
            "age": 2,
            "alive": False
        }
    ]
)
```

or

```python
docs_to_insert = [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]
inserted_docs, inserted_ids = await User.insert_many(docs_to_insert)
```

### Read

#### <a name="find_one"></a> `find_one(query, **kwargs) -> Document`

```python
user = await User.find_one(
    {
        "_id": "655fc281c440f677fa1e117e"
    }
)
```

Alternatively, using `**kwargs`:

```python
user = await User.find_one(_id="655fc281c440f677fa1e117e")
```

**Note:** The `_id` string datatype here is automatically converted to a BSON ObjectID, however, `motormongo` handles
the
scenario when a
BSON ObjectId is passed as the `_id` datatype:

```python
from bson import ObjectId

user = await User.find_one(
    {
        "_id": ObjectId("655fc281c440f677fa1e117e")
    }
)
```

#### <a name="find_many"></a> `find_many(query, limit, **kwargs) -> List[Document]`

```python
users = await User.find_many(age={"$gt": 40}, alive=False, limit=20)
```

or

```python
query = {"age": {"$gt": 40}, "alive": False}
users = await User.find_many(**query, limit=20)
```

### Update

#### <a name="update_one"></a> `update_one(query, updated_fields) -> Document`

```python
updated_user = await User.update_one(
    {
        "_id": "655fc281c440f677fa1e117e"
    },
    {
        "name": "new_name",
        "age": 30
    }
)
```

or

```python
query_criteria = {"name": "old_name"}
update_data = {"name": "updated_name"}
updated_user = await User.update_one(query_criteria, update_data)
```

#### <a name="update_many"></a> `update_many(qeury, fields) -> Tuple[List[Any], int]`

```python
updated_users, modified_count = await User.update_many({'age': {'$gt': 40}}, {'category': 'senior'})
```

another example:

```python
updated_users, modified_count = await User.update_many({'name': 'John Doe'}, {'$inc': {'age': 1}})
```

### Delete

#### <a name="delete_one"></a> `delete_one(query, **kwargs) -> bool`

```python
deleted = await User.delete_one({'_id': '507f191e810c19729de860ea'})
```

Alternatively, using `**kwargs`:

```python
deleted = await User.delete_one(name='John Doe')
```

#### <a name="delete_many"></a> `delete_many(query, **kwargs) -> int`

```python
deleted_count = await User.delete_many({'age': {'$gt': 40}})
```

Another example:

```python
# Delete all users with a specific status
deleted_count = await User.delete_many({'status': 'inactive'})
```

Alternatively, using `**kwargs`:

```python
deleted_count = await User.delete_many(status='inactive')
```

### Mixed

#### <a name="find_one_or_create"></a> `find_one_or_create(query, defaults) -> Tuple['Document', bool]`

```python
user, created = await User.find_one_or_create({'username': 'johndoe'}, defaults={'age': 30})
```

#### <a name="find_one_and_replace"></a> `find_one_and_replace(query, replacement) -> Document`

```python
replaced_user = await User.find_one_and_replace({'username': 'johndoe'}, {'username': 'johndoe', 'age': 35})
```

#### <a name="find_one_and_delete"></a> `find_one_and_delete(query) -> Document`

```python
deleted_user = await User.find_one_and_delete({'username': 'johndoe'})
```

#### <a name="find_one_and_update_empty_fields"></a> `find_one_and_update_empty_fields(query, update_fields) -> Tuple['Document', bool]`

```python
updated_user, updated = await User.find_one_and_update_empty_fields(
    {'username': 'johndoe'},
    {'email': 'johndoe@example.com', 'age': 30}
)
```

## Instance methods

`motormongo` also supports the manipulation of fields on the [object instance](). This allows
users to programmatically achieve the same operations listed above through the object instance
itself.

### Operations

The following are object instance methods are supported by `motormongo`'s `Document` class:

| CRUD Type | Operation                     |
|-----------|-------------------------------|
| Create    | [`save() -> None`](#save)     |
| Delete    | [`delete() -> None`](#delete) |

**Note:** All update operations can be manipulated on the fields in the Document class object itself.

#### <a name="save"></a> `user.save() -> None`

```python
# Find user by MongoDB _id
user = await User.find_one(
    {
        "_id": "655fc281c440f677fa1e117e"
    }
)
# If there age is greater than 80, make them dead
if user.age > 80:
    user.alive = False
# Persist update on User instance in MongoDB mongo
user.save()
```

In this example, `User.find_one()` returns an instance of `User`. If the age field
is greater than 80, the alive field is set to false. The instance of the document in the MongoDB
database is then updated by calling the `.save()` method on the `User` object instance.

### Delete

#### <a name="delete"></a> `user.delete() -> None`

```python
# Find all users where the user is not alive
users = await User.find_many(
    {
        "alive": False
    }
)
# Recursively delete all User instances in the users list who are not alive
for user in users:
    user.delete()
```

### Aggregation

The `aggregate` class method is designed to perform aggregation operations on the documents within the collection. It
allows the execution of a sequence of data aggregation operations defined by the `pipeline` parameter. This method can
return the results either as a list of documents or as a cursor, based on the `return_as_list` flag.

**Parameters:**

- `pipeline`: A list of dictionaries defining the aggregation operations to be performed on the collection.
- `return_as_list` (optional): A boolean flag that determines the format of the returned results. If set to `True`, the
  method returns a list of documents. If `False` (default), it returns a cursor.

**Returns:**

- If `return_as_list` is `True`, returns a list of documents resulting from the aggregation pipeline.
- If `return_as_list` is `False`, returns a Cursor to iterate over the results.

**Raises:**

- `ValueError`: If an error occurs during the execution of the pipeline.

**Example Usage:**

```python
from yourmodule import YourDocumentClass

# Connect to the database (Assuming the database connection is already set up)
# Define an aggregation pipeline
pipeline = [
    {"$match": {"status": "active"}},
    {"$project": {"_id": 0, "username": 1, "status": 1}},
    {"$sort": {"username": 1}}
]

# Execute the aggregation without returning a list
cursor = await YourDocumentClass.aggregate(pipeline)
async for doc in cursor:
    print(doc)

# Execute the aggregation and return results as a list
docs_list = await YourDocumentClass.aggregate(pipeline, return_as_list=True)
print(docs_list)
```

## Polymorphism and Inheritance

This part of the documentation provides an overview of implementing and using polymorphism and inheritance using the
`motormongo` framework, enabling flexible and organized data models for various use cases.

### Base Model: Item

The `Item` class serves as the base model for different types of items stored in a MongoDB collection. It defines common
fields and methods that are shared across all item types.

```python
from motormongo import Document, StringField, FloatField


class Item(Document):
    name = StringField()
    cost = FloatField()
```

### Subclass Models

Subclasses of `Item` can introduce specific fields or override methods to cater to different item categories.

#### Book

A `Book` represents a specific type of `Item` with additional attributes related to books.

```python
class Book(Item):
    title = StringField()
    author = StringField()
    isbn = StringField()
```

#### Electronics

An `Electronics` item represents electronic goods with attributes like warranty period and brand.

```python
class Electronics(Item):
    warranty_period = StringField()  # E.g., "2 years"
    brand = StringField()
```

### Usage

#### Creating and Inserting Items

To insert items into the database, use the `insert_one` method. The item's type is managed automatically.

```python
# Insert a book
book = await Book.insert_one(title="1984", author="George Orwell", isbn="123456789", cost=20.0, name="Book")

# Insert an electronics item
electronics = await Electronics.insert_one(warranty_period="2 years", brand="TechBrand", cost=999.99, name="Laptop")
```

#### Querying Items

You can query items of any type using their base or specific models. Polymorphism allows retrieved instances to be of
the correct subclass.

```python
# Find a book by ISBN
found_book = await Book.find_one(isbn="123456789")

# Find an electronics item by brand
found_electronics = await Electronics.find_one(brand="TechBrand")
```

#### Polymorphic Behavior

The following operations are supported over the base `Item` Document class, enabling complex querying over base `Item`
Document class and all of its subclasses (i.e `Book` and `Electronics`):

| CRUD Type | Operation                                                                                                         |
|-----------|-------------------------------------------------------------------------------------------------------------------|
| Read      | [`find_many(query: dict, limit: int = None, return_as_list: bool = True **kwargs) -> List[Document]`](#find_many) |
| Update    | [`update_many(query: dict, update_fields: dict) -> Tuple[List[Document], int]`](#update_many)                     |
| Delete    | [`delete_many(query: dict, **kwargs) -> int`](#delete_many)                                                       |

As well as `aggregate` operations, see the [Aggregation Operation](#aggregation) section for more details.

Querying on the base `Item` model returns items of all types, correctly instantiated as their specific subclasses. See
below for a logical example of polymorphic querying:

```python
# Find all items with a cost over 50
expensive_items = await Item.find_many(cost={"$gt": 50})

for item in expensive_items:
    print(type(item))  # Prints the subclass (Book, Electronics, etc.)
    if isinstance(item, Book):
        print(f"Book: {item.title} by {item.author}")
    elif isinstance(item, Electronics):
        print(f"Electronics: {item.brand} with {item.warranty_period} warranty")
```

## Pooling Options Configuration

In `motormongo`, you have the flexibility to customize the pooling options for the Motor client. This allows you to
fine-tune the behavior of database connections according to your application's needs. Below are some of the parameters
you can configure, along with their descriptions and example usage.

### Configuration Parameters

- **Max Pool Size**: The maximum number of connections in the connection pool.
- **Min Pool Size**: The minimum number of connections in the connection pool.
- **Max Idle Time**: The maximum time (in milliseconds) a connection can remain idle in the pool before being closed.
- **Wait Queue Timeout**: The time (in milliseconds) a thread will wait for a connection to become available when the
  pool is exhausted.
- **Connect Timeout**: The time (in milliseconds) to wait for a connection to the MongoDB server to be established
  before timing out.
- **Socket Timeout**: The time (in milliseconds) to wait for a socket read or write to complete before timing out.

### Example Configuration

```python
import asyncio
from motormongo import DataBase

# Example pooling options
pooling_options = {
    'maxPoolSize': 50,
    'minPoolSize': 10,
    'maxIdleTimeMS': 30000,
    'waitQueueTimeoutMS': 5000,
    'connectTimeoutMS': 10000,
    'socketTimeoutMS': 20000
}


async def init_db():
    # This 'connect' method needs to be called inside of an async function
    await DataBase.connect(uri="<mongo_uri>", database="<mongo_database>", **pooling_options)


if __name__ == "__main__":
    asyncio.run(init_db())
```

or in FastAPI:

```python
from fastapi import FastAPI
from motormongo import DataBase

app = FastAPI()

# Example pooling options
pooling_options = {
    'maxPoolSize': 50,
    'minPoolSize': 10,
    'maxIdleTimeMS': 30000,
    'waitQueueTimeoutMS': 5000,
    'connectTimeoutMS': 10000,
    'socketTimeoutMS': 20000
}


@app.on_event("startup")
async def startup_db_client():
    await DataBase.connect(uri="<mongodb_uri>", db="<mongodb_db>", **pooling_options)

```

This configuration demonstrates how to set up `motormongo` with specific pooling options to optimize performance
and resource utilization in high-throughput environments.

For more information, consult the official documentation:

- [Motor: Asynchronous Python driver for MongoDB](https://motor.readthedocs.io/en/stable/)
- [MongoDB Manual: Tuning Your Connection Pool Settings](https://www.mongodb.com/docs/manual/reference/connection-string/#mongodb-urioption-urioption.maxPoolSize)

## FastAPI integration

`motormongo` can be easily integrated in FastAPI APIs to leverage the asynchronous ability of
FastAPI. To leverage `motormongo`'s ease-of-use, Pydantic model's should be created to represent the MongoDB
`motormongo` Document as a Pydantic model. Below is a light-weight CRUD FastAPI application using `motormongo`:

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from motormongo import DataBase, Document, BinaryField, StringField
import re
import bcrypt


def hash_password(password: str) -> bytes:
    # Example hashing function
    return bcrypt.hashpw(password.encode('utf-8'), salt=bcrypt.gensalt())


class User(Document):
    username = StringField(help_text="The username for the user", min_length=3, max_length=50)
    email = StringField(help_text="The email for the user", regex=re.compile(r'^\S+@\S+\.\S+$'))  # Simple email regex
    password = BinaryField(help_text="The hashed password for the user", hash_function=hash_password)

    def verify_password(self, password: str) -> bool:
        return bcrypt.checkpw(password.encode("utf-8"), self.password)

    class Meta:
        collection = "users"  # < If not provided, will default to class name (ex. User->user, UserDetails->user_details)
        created_at_timestamp = True  # < Provide a DateTimeField for document creation
        updated_at_timestamp = True  # < Provide a DateTimeField for document updates


class UserModelRequest(BaseModel):
    username: str = Field(example="johndoe")
    email: str = Field(example="johndoe@coldmail.com")
    password: str = Field(example="password123")


app = FastAPI()


@app.on_event("startup")
async def startup_db_client():
    await DataBase.connect(uri="<mongodb_uri>", db="<mongodb_db>")


@app.on_event("shutdown")
async def shutdown_db_client():
    await DataBase.close()


@app.post("/users/", status_code=201)
async def create_user(user: UserModelRequest):
    new_user = await User.insert_one(**user.dict())
    return new_user.to_dict()


@app.post("/user/auth", status_code=200)
async def is_authenticated(username: str, password: str):
    user = await User.find_one({"username": username})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.verify_password(password):
        raise HTTPException(status_code=401, detail="Unauthorized")
    else:
        return "You are authenticated! You can see this!"


@app.get("/users")
async def get_users():
    users = await User.find_many()
    if not users:
        raise HTTPException(status_code=404, detail="User not found")
    return [user.to_dict() for user in users]


@app.get("/users/{user_id}")
async def get_user(user_id: str):
    user = await User.find_one({"_id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user.to_dict()


@app.put("/users/{user_id}", status_code=200)
async def update_user(user_id: str, user_data: UserModelRequest):
    updated_user = await User.update_one({"_id": user_id}, user_data.model_dump())
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user.to_dict()


@app.delete("/users/{user_id}", status_code=204)
async def delete_user(user_id: str):
    user = await User.find_one({"_id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    await user.delete()
    return {"status": "User deleted successfully"}
```

## License

This project is licensed under the MIT License.