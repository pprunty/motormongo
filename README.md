[![Documentation Status](https://readthedocs.org/projects/pprunty-shapeshifter/badge/?version=latest)](https://pprunty-shapeshifter.readthedocs.io/en/latest/?badge=latest)
![PyPI - Downloads](https://img.shields.io/pypi/dm/requests)
![PyPI - Version](https://img.shields.io/pypi/v/requests)
![GitHub Contributors](https://img.shields.io/github/contributors/pprunty/shapeshifter.svg)

Author: [Patrick Prunty]()

`motormongo` - An Object Document Mapper
for [MongoDB]() built on-top of [Motor](), an asynchronous Python driver for MongoDB, designed to work with Tornado or
asyncio
and enable non-blocking access to MongoDB.

Asynchronous operations in a backend system, built using [FastAPI]() for
example, enhances performance and scalability by enabling non-blocking, concurrent handling of multiple requests,
leading to
more efficient use of server resources.

## Installation

To install motormongo, you can use `pip` inside your virtual environment:

```shell
python -m pip install motormongo
```

Alternatively, to install motormongo into your `poetry` environment:

```shell
poetry add motormongo
```

## Quickstart

### Step 1. Create a Motor Client:

```python
from motor.motor_asyncio import AsyncIOMotorClient

```

For details on how to set up a local or cloud MongoDB database instance, see [here]().

### Step 2. Define a motormongo Document:

Define a motormongo `User` document:

```python
import re
import bcrypt
from motormongo.abstracts.document import Document
from motormongo.fields.binary_field import BinaryField
from motormongo.fields.string_field import StringField
from motormongo.fields.string_field import IntegerField

def hash_password(password):
    # Example hashing function
    return bcrypt.hashpw(password.encode('utf-8'), salt=bcrypt.gensalt())

class User(Document):
    username = StringField(help_text="The username for the user", min_length=3, max_length=50)
    email = StringField(help_text="The email for the user", regex=re.compile(r'^\S+@\S+\.\S+$'))  # Simple email regex
    password = BinaryField(help_text="The hashed password for the user", hash_function=hash_password)
    age = IntegerField(help_text="The age of the user")

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
        "password": "password123" #< hash_functon will hash the string literal password
    }
)
```

### Step 4: Validate user was created in your MongoDB collection

You can do this using [MongoDB compass](), or alternatively, add a query to find all documents in the user
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

## Congratulations 🎉

You've successfully created your first motormongo Object Document Mapper class. 🥳

The subsequent sections detail the datatype fields provided by motormongo, as well as the CRUD
operations available on the classmethods and object instance methods of a motormongo document.

If you wish to get straight into how to integrate motormongo with your [`FastAPI`]() application, skip ahead to the
[FastAPI Integration]() section.

## motormongo Fields

motormongo supports the following datatype fields for your motormongo Document class:

1. `StringField(min_length, max_length, regex)`
2. `IntegerField(min_value, max_value)`
3. `BooleanField`
4. `EnumField(Enum)`
5. `DateTimeField(auto_now, auto_now_add)`
6. `ListField`
7. `ReferenceField(Document)`
8. `BinaryField(hash_function)`
9. `GeoJSONField()`

## Class methods

### Operations

The following [classmethods]() are supported by motormongo's Document class:

| CRUD Type | Operation                                                             |
|-----------|-----------------------------------------------------------------------|
| Create    | [`insert_one(document)`](#create)` -> Object`                           |
| Create    | [`insert_many(List[document])`](#create)` -> List[Object]`              |
| Read      | [`find_one(query)`](#read)` -> Object`                                  |
| Read      | [`find_many(filter)`](#read)` -> List[Object]`                          |
| Update    | [`update_one`](#update) ->                                            |
| Update    | [`update_many(query, fields)`](#update)                               |
| Update    | [`replace_one`](#update)                                              |
| Mixed     | [`find_one_or_create(query, document)`](#mixed)` -> (Object, boolean)`  |
| Mixed     | [`find_one_and_replace`](#mixed)                                      |
| Mixed     | [`find_one_and_delete`](#mixed)                                       |
| Mixed     | [`find_one_and_update_empty_fields(query, fields)`](#mixed)` -> Object` |

### Create

<a name="insert_one"></a>

* `insert_one(document)`

```python
await User.insert_one(
    {
        "name": "John",
        "age": 24,
        "alive": True
    }
)
```

* `insert_many(List[document])`

```python
await User.insert_many(
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

### Read

* `find_one(query)`

```python
user = await User.find_one(
    {
        "_id": "655fc281c440f677fa1e117e"
    }
)
```

Note: The `_id` string datatype here is automatically converted to a BSON ObjectID, however, motormongo handles the scenario when a
BSON ObjectId is passed as the `_id` datatype:

```python
from bson import ObjectId

user = await User.find_one(
    {
        "_id": ObjectId("655fc281c440f677fa1e117e")
    }
)
```

* `find_many(filter)`

```python
users = await User.find_many(
    {
        "alive": True
    }
)
```

### Update

* `update_one`

```python
updated_user = await User.update_one(
    {
        "_id": "655fc281c440f677fa1e117e"
    },
    {
        "age": 49
    }
)
```

* `update_many(qeury, fields)`

```python
updated_users = await User.update_many(
    {
        "age": 70
    },
    {
        "alive": False
    }
)
```

* `replace_one`

### Destroy

*

### Mixed

* `find_one_or_create(query, document)`

```python
user, was_created = await User.find_one_or_create(
    {
        "name": "John"
    },
    {
        "name": "John Doe",
        "age": 24,
        "alive": False
    }
)
```

* `find_one_and_replace`

```python
user = await User.find_one_and_replace(
    {
        "_id": ObjectId("655fc281c440f677fa1e117e")
    },
    {
        "name": "John"
    }
)
```

* `find_one_and_delete`
* `find_one_and_update_empty_fields(query, fields)`

```python
user = await User.find_one_and_update_empty_fields(
    {
        "_id": ObjectId("655fc281c440f677fa1e117e")
    },
    {
        "name": "John"
    }
)
```

## Instance methods

motormongo also supports the manimulation of fields on the [object instance](). This allows
users to programmatically achieve the same operations listed above through the object instance
itself.

### Operations

The following object instance methods are
suported by an instance of a motormongo Document object:

### Read

[//]: # (* `.count&#40;&#41;`)

[//]: # (```python)

[//]: # (# Find all users where the user is not alive)

[//]: # (users: List[User] = await User.find_many&#40;)

[//]: # (    {)

[//]: # (        "alive": False)

[//]: # (    })

[//]: # (&#41;)

[//]: # (# Recursively delete all User instances in the users list who are not alive)

[//]: # (if users.count&#40;&#41; > 10:)

[//]: # (    # Do something logical)

[//]: # (```)

### Update

* `user.save()`

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
# Persist update on User instance in MongoDB database
user.save()
```

In this example, `Task.find_one()` returns an instance of `User`. If the age field
is greater than 80, the alive field is set to false. The instance of the document in the MongoDB
database is then updated by calling the `.save()` method on the `User` object instance.

### Destroy

* `user.delete()`

```python
# Find all users where the user is not alive
users: List[User] = await User.find_many(
    {
        "alive": False
    }
)
# Recursively delete all User instances in the users list who are not alive
users.delete()
```

## FastAPI integration

motormongo can be easily integrated in FastAPI APIs to leverage the asynchronous ability of
FastAPI. To leverage motormongo's ease-of-use, Pydantic model's should be created to represent the MongoDB
Document as a Pydantic model.

Below are some example APIs detailing how

### Creating a document

```python
from models.documents import User
from models.requests import UserModel


@app.post("/users/")
async def create_user(user: UserModel):
    new_user = User(**user.model_dump())
    await new_user.save()
    return new_user.to_dict()
```

Note: 