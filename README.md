[![PyPI - Version](https://img.shields.io/pypi/v/motormongo)](https://pypi.org/project/motormongo/)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/motormongo)](https://pypi.org/project/motormongo/)
[![GitHub Contributors](https://img.shields.io/github/contributors/pprunty/motormongo.svg)](https://github.com/pprunty/motormongo/graphs/contributors)
[![PyPI License](https://img.shields.io/pypi/l/motormongo.svg)](https://pypi.org/project/motormongo/)

Author: [Patrick Prunty](https://pprunty.github.io/pprunty/).

`motormongo` - An Object Document Mapper
for [MongoDB](https://www.mongodb.com) built on-top of [Motor](https://github.com/mongodb/motor), the MongoDB recommended asynchronous Python driver for MongoDB Python applications, designed to work with Tornado or
asyncio and enable non-blocking access to MongoDB.

Asynchronous operations in a backend system, built using [FastAPI](https://github.com/tiangolo/fastapi) for
example, enhances performance and scalability by enabling non-blocking, concurrent handling of multiple requests,
leading to more efficient use of server resources.

The interface for instantiating Document classes follows similar logic to [mongoengine](https://github.com/MongoEngine/mongoengine), enabling ease-of-transition and
 migration from `mongoengine` to `motormongo`.

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

### Step 1. Create a motormongo client:

```python
from motormongo import connect


def init_db():
    # This 'connect' method needs to be called inside of a function because it is asynchronous
    await connect(uri="<mongo_uri>", database="<mongo_database>")

if __name__ == "__main__":
    init_db()
```

The `mongo_uri` should look something like this:

```text
mongodb+srv://<username>:<password>@<cluster>.mongodb.net
```

and `database` should be the name of an existing MongoDB database in your MongoDB instance.

For details on how to set up a local or cloud MongoDB database instance, see [here](https://www.mongodb.com/cloud/atlas/lp/try4?utm_source=google&utm_campaign=search_gs_pl_evergreen_atlas_general_prosp-brand_gic-null_emea-ie_ps-all_desktop_eng_lead&utm_term=using%20mongodb&utm_medium=cpc_paid_search&utm_ad=p&utm_ad_campaign_id=9510384711&adgroup=150907565274&cq_cmp=9510384711&gad_source=1&gclid=Cj0KCQiAyeWrBhDDARIsAGP1mWQ6B0kPYX9Tqmzku-4r-uUzOGL1PKDgSTlfpYeZ0I6HE3C-dgh1xF4aArHqEALw_wcB).

### Step 2. Define a motormongo Document:

Define a motormongo `User` document:

```python
import re
import bcrypt
from motormongo.abstracts.document import Document
from motormongo.fields.binary_field import BinaryField
from motormongo.fields.string_field import StringField
from motormongo.fields.integer_field import IntegerField
from motormongo.fields.enum_field import EnumField

def hash_password(password) -> bytes:
    # Example hashing function
    return bcrypt.hashpw(password.encode('utf-8'), salt=bcrypt.gensalt())

class User(Document):
    username = StringField(help_text="The username for the user", min_length=3, max_length=50)
    email = StringField(help_text="The email for the user", regex=re.compile(r'^\S+@\S+\.\S+$'))  # Simple email regex
    password = BinaryField(help_text="The hashed password for the user", hash_function=hash_password)
    age = IntegerField(help_text="The age of the user")
    status = EnumField(enum=Status, help_text="Indicator for whether the user is active or not.")

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

If you wish to get straight into how to integrate motormongo with your `FastAPI` application, skip ahead to the
[FastAPI Integration](#fastapi-integration) section.

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

## Operations

The following class methods are supported by motormongo's `Document` class:

| CRUD Type | Operation                                                                                                                          |
|-----------|------------------------------------------------------------------------------------------------------------------------------------|
| Create    | [`insert_one(document: dict, **kwargs) -> Document`](#insert_one)                                                                  |
| Create    | [`insert_many(documents: List[dict]) -> Tuple[List[Document], Any]`](#insert_many)                                                 |
| Read      | [`find_one(filter: dict, **kwargs) -> Document`](#find_one)                                                                        |
| Read      | [`find_many(filter: dict, limit: int, **kwargs) -> List[Document]`](#find_many)                                                    |
| Update    | [`update_one(query: dict, update_fields: dict) -> Document`](#update_one)                                                          |
| Update    | [`update_many(query: dict, update_fields: dict) -> Tuple[List[Document], int]`](#update_many)                                      |
| Delete    | [`delete_one(query: dict, **kwargs) -> bool`](#delete_one)                                                                         |
| Delete    | [`delete_many(query: dict, **kwargs) -> int`](#delete_many)                                                                        |
| Mixed     | [`find_one_or_create(query: dict, defaults: dict) -> Tuple[Document, bool]`](#find_one_or_create)                                  |
| Mixed     | [`find_one_and_replace(query: dict, replacement: dict) -> Document`](#find_one_and_replace)                                        |
| Mixed     | [`find_one_and_delete(query: dict) -> Document`](#find_one_and_delete)                                                             |
| Mixed     | [`find_one_and_update_empty_fields(query: dict, update_fields: dict) -> Tuple[Document, bool]`](#find_one_and_update_empty_fields) |

### Create

#### <a name="insert_one"></a> `insert_one(document: dict, **kwargs) -> Document`
Inserts a single document into the database.
```python
user = await MyClass.insert_one({
    "name": "John",
    "age": 24,
    "alive": True
})
```

Alternatively, using `**kwargs`:

```python
user = await MyClass.insert_one(
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
user = await MyClass.insert_one(**user_document)
```

#### <a name="insert_many"></a> `insert_many(List[document]) -> tuple[List['Document'], Any]`

```python
users, user_ids = await MyClass.insert_many(
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
inserted_docs, inserted_ids = await MyClass.insert_many(docs_to_insert)
```

### Read

#### <a name="find_one"></a> `find_one(query, **kwargs) -> Document`

```python
user = await MyClass.find_one(
    {
        "_id": "655fc281c440f677fa1e117e"
    }
)
```

Alternatively, using `**kwargs`:

```python
user = await MyClass.find_one(_id="655fc281c440f677fa1e117e")
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

#### <a name="find_many"></a> `find_many(filter, limit, **kwargs) -> List[Document]`

```python
users =  await MyClass.find_many(age={"$gt": 40}, alive=False, limit=20)
```

or

```python
filter_criteria = {"age": {"$gt": 40}, "alive": False}
users = await MyClass.find_many(**filter_criteria, limit=20)
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
updated_user = await MyClass.update_one(query_criteria, update_data)
```

#### <a name="update_many"></a> `update_many(qeury, fields) -> Tuple[List[Any], int]`

```python
updated_users, modified_count = await MyClass.update_many({'age': {'$gt': 40}}, {'category': 'senior'})
```

another example:

```python
updated_users, modified_count = await MyClass.update_many({'name': 'John Doe'}, {'$inc': {'age': 1}})
```

### Destroy

#### <a name="delete_one"></a> `delete_one(query, **kwargs) -> bool`

```python
deleted = await MyClass.delete_one({'_id': '507f191e810c19729de860ea'})
```

Alternatively, using `**kwargs`:

```python
deleted = await MyClass.delete_one(name='John Doe')
```

#### <a name="delete_many"></a> `delete_many(query, **kwargs) -> int`

```python
deleted_count = await MyClass.delete_many({'age': {'$gt': 40}})
```

Another example:

```python
# Delete all users with a specific status
deleted_count = await MyClass.delete_many({'status': 'inactive'})
```

Alternatively, using `**kwargs`:

```python
deleted_count = await MyClass.delete_many(status='inactive')
```

### Mixed

#### <a name="find_one_or_create"></a> `find_one_or_create(query, defaults) -> Tuple['Document', bool]`

```python
user, created = await MyClass.find_one_or_create({'username': 'johndoe'}, defaults={'age': 30})
```

#### <a name="find_one_and_replace"></a> `find_one_and_replace(query, replacement) -> Document`

```python
replaced_user = await MyClass.find_one_and_replace({'username': 'johndoe'}, {'username': 'johndoe', 'age': 35})
```

#### <a name="find_one_and_delete"></a> `find_one_and_delete(query) -> Document`

```python
deleted_user = await MyClass.find_one_and_delete({'username': 'johndoe'})
```

#### <a name="find_one_and_update_empty_fields"></a> `find_one_and_update_empty_fields(query, update_fields) -> Tuple['Document', bool]`

```python
updated_user, updated = await MyClass.find_one_and_update_empty_fields(
                {'username': 'johndoe'},
                {'email': 'johndoe@example.com', 'age': 30}
            )
```

## Instance methods

motormongo also supports the manimulation of fields on the [object instance](). This allows
users to programmatically achieve the same operations listed above through the object instance
itself.

### Operations

The following are object instance methods are supported by motormongo's `Document` class:

| CRUD Type | Operation                                                                                                                          |
|-----------|------------------------------------------------------------------------------------------------------------------------------------|
| Create    | [`save() -> None`](#save)                                                                                                          |
| Delete    | [`delete() -> None`](#delete)                                                                                                      |

NOTE: All update operations can be manipulated on the fields in the Document class object itself.

#### <a name="save"></a> `user.save() -> None`

```python
# Find user by MongoDB _id
user = await MyClass.find_one(
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

In this example, `MyClass.find_one()` returns an instance of `MyClass`. If the age field
is greater than 80, the alive field is set to false. The instance of the document in the MongoDB
database is then updated by calling the `.save()` method on the `MyClass` object instance.

### Destroy

#### <a name="delete"></a> `user.delete() -> None`

```python
# Find all users where the user is not alive
users = await MyClass.find_many(
    {
        "alive": False
    }
)
# Recursively delete all User instances in the users list who are not alive
for user in users:
    user.delete()
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


## License

This project is licensed under the MIT License.