[![Documentation Status](https://readthedocs.org/projects/pprunty-shapeshifter/badge/?version=latest)](https://pprunty-shapeshifter.readthedocs.io/en/latest/?badge=latest)
![PyPI - Downloads](https://img.shields.io/pypi/dm/requests)
![PyPI - Version](https://img.shields.io/pypi/v/requests)
![GitHub Contributors](https://img.shields.io/github/contributors/pprunty/shapeshifter.svg)

`motormongo` - An Object Document Mapper
for MongoDB built on-top of Motor, an asynchronous Python driver for MongoDB, designed to work with Tornado or asyncio
and enable non-blocking access to MongoDB. Asynchronous operations in a backend system, build using FastAPI for
example, enhances performance and scalability by enabling non-blocking, concurrent handling of multiple requests, leading to
more efficient use of server resources.

## Usage

Define a motormongo document:

```python
from motormongo import Document, StringField, IntegerField, BooleanField


class Task(Document):
    name = StringField(help_text="")
    money = IntegerField(help_text="")
    alive = BooleanField(help_text="")
```


## Class methods

### Operations

The following [classmethods]() are supported by motormongo's Document class:

### Create

* `insert_one(document)`

```python
await Task.insert_one(
    {
        "name": "John",
        "age": 24, 
        "alive": True
    }
)
```

* `insert_many`
```python
await Task.insert_many(
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

* `find_one`
```python
task = await Task.find_one(
    {
        "_id": "655fc281c440f677fa1e117e"
    }
)
```
Note: The `_id` here is automatically converted to a BSON ObjectID, however, you can also pass a BSON ObjectID to the
function:
```python
from bson import ObjectId

task = await Task.find_one(
    {
        "_id": ObjectId("655fc281c440f677fa1e117e")
    }
)
```

* `find_many`
```python
tasks = await Task.find_many(
    {
        "alive": True
    }
)
```

### Update

* `update_one`
```python
updated_task = await Task.update_one(
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
updated_tasks = await Task.update_many(
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
task, was_created = await Task.find_one_or_create(
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
* `find_one_and_delete`
* `find_one_and_update_empty_fields(query, fields)`
```python
task = await Task.find_one_and_update_empty_fields(
    {
        "_id": ObjectId("655fc281c440f677fa1e117e")
    },
    {
        "name": "John"
    }
)
```

## Static methods


## FastAPI integration

motormongo can be easily integrated in FastAPI APIs to leverage the asynchronous ability of 
FastAPI. To leverage motormongo's ease-of-use, Pydantic model's should be created to represent the MongoDB
Document as a Pydantic model.

Below are some example APIs detailing how 

### Creating a document

```python
from models.documents import Task
from models.requests import TaskModel

@app.post("/tasks/")
async def create_task(task: TaskModel):
    new_task = Task(**task.model_dump())
    await new_task.save()
    return new_task.to_dict()
```

Note: 