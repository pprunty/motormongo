# motormongo Fields

`motormongo` supports a variety of field types to accurately define the schema of your MongoDB documents. Each field
type is designed to handle specific data types and validations:

- `BinaryField`: Stores binary data, useful for storing encoded or hashed data like passwords.
- `BooleanField`: Stores boolean values (`True` or `False`).
- `DateTimeField`: Manages date and time, with options for automatically setting current date/time on creation or update.
- `EmbeddedDocumentField`: For fields that should contain values from a predefined enumeration.
- `EnumField`: For fields that should contain values from a predefined enumeration.
- `FloatField`: Handles floating-point numbers, with options to specify minimum and maximum values.
- `GeoJSONField`: Manages geographical data in GeoJSON format, with an option to return data as JSON.
- `IntegerField`: Manages integer data, allowing specifications for minimum and maximum values.
- `ListField`: Handles lists of items, which can be of any type.
- `ReferenceField`: Creates a reference to another document.
- `StringField`: Handles string data with options for minimum and maximum length, and regex validation.

## Defaults for all fields

All fields have the following default parameters:

* **`default`**: Specifies the default value for the field if no value is provided. This parameter can be a static value
  or a callable object. The callable object is useful for dynamic values like generating timestamps or unique
  identifiers.
* **`required`**: A boolean indicating whether the field is mandatory. If set to True, the document cannot be saved
  without providing a value for this field.
* **`unique`**: A boolean specifying if the field value should be unique across the collection. This is crucial for
  fields like email addresses or usernames.


## BinaryField 

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

**Example Usage**:

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

## BooleanField

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

## DateTimeField

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

## EmbeddedDocumentField

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

## EnumField

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

## FloatField

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

## GeoJSONField

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

## IntegerField

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

## ListField

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

## ReferenceField

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

## StringField

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
