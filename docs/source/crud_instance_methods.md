# CRUD instance methods

`motormongo` also supports the manipulation of fields on the [object instance](). This allows
users to programmatically achieve the same operations listed above through the object instance
itself.

## Operations

The following are object instance methods are supported by `motormongo`'s `Document` class:

| CRUD Type | Operation                     |
|-----------|-------------------------------|
| Create    | [`save() -> None`](#save)     |
| Delete    | [`delete() -> None`](#delete) |

**Note:** All update operations can be manipulated on the fields in the Document class object itself.

### user.save() -> None

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

## Delete

### user.delete() -> None

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