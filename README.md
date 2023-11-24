[![Documentation Status](https://readthedocs.org/projects/pprunty-shapeshifter/badge/?version=latest)](https://pprunty-shapeshifter.readthedocs.io/en/latest/?badge=latest)
![PyPI - Downloads](https://img.shields.io/pypi/dm/requests)
![PyPI - Version](https://img.shields.io/pypi/v/requests)
![GitHub Contributors](https://img.shields.io/github/contributors/pprunty/shapeshifter.svg)

Author: [Patrick Prunty]()

`motormongo` - An Object Document Mapper
for [MongoDB]() built on-top of [Motor](), an asynchronous Python driver for MongoDB, designed to work with Tornado or asyncio
and enable non-blocking access to MongoDB.

Asynchronous operations in a backend system, built using [FastAPI]() for
example, enhances performance and scalability by enabling non-blocking, concurrent handling of multiple requests, leading to
more efficient use of server resources.

# Table of Contents

1. [Installation](#installation)
2. [Quickstart](#quickstart)
3. [C.R.U.D Class Methods](#class-methods)
4. [C.R.U.D Object Instance Methods](#class-methods)
5. [FastAPI Integration](#overview)


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

from motormongo.abstracts.base_document import Document
from motormongo.fields.binary_field import BinaryField
from motormongo.fields.string_field import StringField


class User(Document):
    username = StringField(help_text="The username for the user", min_length=3, max_length=50)
    email = StringField(help_text="The email for the user", regex=re.compile(r'^\S+@\S+\.\S+$'))  # Simple email regex
    password = BinaryField(help_text="The hashed password for the user")

```

### Step 3: Create a MongoDB document using the User class

```python
import bcrypt

await User.insert_one(
    {
        "username": "johndoe",
        "email": "johndoe@portmarnock.ie",
        "password": bcrypt.hashpw("password123".encode('utf-8'), salt=bcrypt.gensalt())
    }
)
```

### Step 4: Put all the code above into one file and run it

```shell
python main.py
```

## Step 5: Validate user was created in your MongoDB collection

You can do this using [MongoDB compass](), or add an alternative method to find and print all documents in the user 
collection:

```python
users = User.find_many({})
if users:
    print("User collection contains the following documents:")
    for user in users:
        print(user.to_dict())  # Assuming that to_dict() is a method of User class
else:
    print("User collection failed to update! Check your MongoDB connection details and try again!")
```

And run the file again, as done in Step. 4.

## Congratulations 🎉

You've successfully created your first motormongo Object Document Mapper class. 🥳

For further development details on how to run asynchronous CRUD operation using motormongo Document class methods
and object instance methods, continue reading.

If you wish to get straight into how to integrate motormongo with your [`FastAPI`]() application, skip ahead to the
[FastAPI Integration]() section.

## Class methods

### Operations

The following [classmethods]() are supported by motormongo's Document class:


| CRUD Type | Operation                                                   | Detail                                                                                             |
|-----------|-------------------------------------------------------------|----------------------------------------------------------------------------------------------------|
| Create    | [`insert_one(document)`](#create)                           | `await TaskDocument.insert_one({"name": "John", "age": 24, "alive": True})`                        |
| Create    | [`insert_many(List[document])`](#create)                    | `await TaskDocument.insert_many([{"name": "John", "age": 24, "alive": True}, {"name": "Mary", "age": 2, "alive": False}])` |
| Read      | [`find_one(query)`](#read)                                  | `await TaskDocument.find_one({"_id": "655fc281c440f677fa1e117e"})`                                 |
| Read      | [`find_many(filter)`](#read)                                | `await TaskDocument.find_many({"alive": True})`                                                     |
| Update    | [`update_one`](#update)                                     | `await TaskDocument.update_one({"_id": "655fc281c440f677fa1e117e"}, {"age": 49})`                  |
| Update    | [`update_many(query, fields)`](#update)                     | `await TaskDocument.update_many({"age": 70}, {"alive": False})`                                    |
| Update    | [`replace_one`](#update)                                    | [No example provided]                                                                               |
| Other     | [`find_one_or_create(query, document)`](#other)             | `await TaskDocument.find_one_or_create({"name": "John"}, {"name": "John Doe", "age": 24, "alive": False})` |
| Other     | [`find_one_and_replace`](#other)                            | `await TaskDocument.find_one_and_replace({"_id": ObjectId("655fc281c440f677fa1e117e")}, {"name": "John"})` |
| Other     | [`find_one_and_delete`](#other)                             | [No example provided]                                                                               |
| Other     | [`find_one_and_update_empty_fields(query, fields)`](#other) | `await TaskDocument.find_one_and_update_empty_fields({"_id": ObjectId("655fc281c440f677fa1e117e")}, {"name": "John"})` |


### Create

<a name="insert_one"></a>
* `insert_one(document)`

```python
await TaskDocument.insert_one(
    {
        "name": "John",
        "age": 24, 
        "alive": True
    }
)
```

* `insert_many(List[document])`
```python
await TaskDocument.insert_many(
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
task = await TaskDocument.find_one(
    {
        "_id": "655fc281c440f677fa1e117e"
    }
)
```
Note: The `_id` here is automatically converted to a BSON ObjectID, however, you can also pass a BSON ObjectID to the
function; motormongo handles this scenario:
```python
from bson import ObjectId

task = await TaskDocument.find_one(
    {
        "_id": ObjectId("655fc281c440f677fa1e117e")
    }
)
```

* `find_many(filter)`
```python
tasks = await TaskDocument.find_many(
    {
        "alive": True
    }
)
```

### Update

* `update_one`
```python
updated_task = await TaskDocument.update_one(
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
updated_tasks = await TaskDocument.update_many(
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

### Other

* `find_one_or_create(query, document)`
```python
task, was_created = await TaskDocument.find_one_or_create(
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
task = await TaskDocument.find_one_and_replace(
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
task = await TaskDocument.find_one_and_update_empty_fields(
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

[//]: # (# Find all tasks where the user is not alive)

[//]: # (tasks: List[TaskDocument] = await TaskDocument.find_many&#40;)

[//]: # (    {)

[//]: # (        "alive": False)

[//]: # (    })

[//]: # (&#41;)

[//]: # (# Recursively delete all TaskDocument instances in the tasks list who are not alive)

[//]: # (if tasks.count&#40;&#41; > 10:)

[//]: # (    # Do something logical)

[//]: # (```)

### Update

* `task.save()`

```python
# Find task by MongoDB _id
task = await TaskDocument.find_one(
    {
        "_id": "655fc281c440f677fa1e117e"
    }
)
# If there age is greater than 80, make them dead
if task.age > 80:
    task.alive = False
# Persist update on TaskDocument instance in MongoDB database
task.save()
```
In this example, `Task.find_one()` returns an instance of `TaskDocument`. If the age field
is greater than 80, the alive field is set to false. The instance of the document in the MongoDB
database is then updated by calling the `.save()` method on the `TaskDocument` object instance.

### Destroy

* `task.delete()`

```python
# Find all tasks where the user is not alive
tasks: List[TaskDocument] = await TaskDocument.find_many(
    {
        "alive": False
    }
)
# Recursively delete all TaskDocument instances in the tasks list who are not alive
tasks.delete()
```


## FastAPI integration

motormongo can be easily integrated in FastAPI APIs to leverage the asynchronous ability of 
FastAPI. To leverage motormongo's ease-of-use, Pydantic model's should be created to represent the MongoDB
Document as a Pydantic model.

Below are some example APIs detailing how 

### Creating a document

```python
from models.documents import TaskDocument
from models.requests import TaskModel

@app.post("/tasks/")
async def create_task(task: TaskModel):
    new_task = TaskDocument(**task.model_dump())
    await new_task.save()
    return new_task.to_dict()
```

Note: 