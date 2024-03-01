# CRUD classmethods

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

## Create

### insert_one(document: dict, **kwargs) -> Document

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

### insert_many(List[document]) -> tuple[List['Document'], Any]

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

## Read

#### find_one(query, **kwargs) -> Document

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

### find_many(query, limit, **kwargs) -> List[Document]

```python
users = await User.find_many(age={"$gt": 40}, alive=False, limit=20)
```

or

```python
query = {"age": {"$gt": 40}, "alive": False}
users = await User.find_many(**query, limit=20)
```

## Update

### update_one(query, updated_fields) -> Document

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

### update_many(qeury, fields) -> Tuple[List[Any], int]

```python
updated_users, modified_count = await User.update_many({'age': {'$gt': 40}}, {'category': 'senior'})
```

another example:

```python
updated_users, modified_count = await User.update_many({'name': 'John Doe'}, {'$inc': {'age': 1}})
```

## Delete

### delete_one(query, **kwargs) -> bool

```python
deleted = await User.delete_one({'_id': '507f191e810c19729de860ea'})
```

Alternatively, using `**kwargs`:

```python
deleted = await User.delete_one(name='John Doe')
```

### delete_many(query, **kwargs) -> int

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

## Mixed

### find_one_or_create(query, defaults) -> Tuple['Document', bool]

```python
user, created = await User.find_one_or_create({'username': 'johndoe'}, defaults={'age': 30})
```

### find_one_and_replace(query, replacement) -> Document

```python
replaced_user = await User.find_one_and_replace({'username': 'johndoe'}, {'username': 'johndoe', 'age': 35})
```

### find_one_and_delete(query) -> Document

```python
deleted_user = await User.find_one_and_delete({'username': 'johndoe'})
```

### find_one_and_update_empty_fields(query, update_fields) -> Tuple['Document', bool]

```python
updated_user, updated = await User.find_one_and_update_empty_fields(
    {'username': 'johndoe'},
    {'email': 'johndoe@example.com', 'age': 30}
)
```