# Polymorphism and Inheritance

This part of the documentation provides an overview of implementing and using polymorphism and inheritance using the
`motormongo` framework, enabling flexible and organized data models for various use cases.

## Base Model: Item

The `Item` class serves as the base model for different types of items stored in a MongoDB collection. It defines common
fields and methods that are shared across all item types.

```python
from motormongo import Document, StringField, FloatField


class Item(Document):
    name = StringField()
    cost = FloatField()
```

## Subclass Models

Subclasses of `Item` can introduce specific fields or override methods to cater to different item categories.

### Book

A `Book` represents a specific type of `Item` with additional attributes related to books.

```python
class Book(Item):
    title = StringField()
    author = StringField()
    isbn = StringField()
```

### Electronics

An `Electronics` item represents electronic goods with attributes like warranty period and brand.

```python
class Electronics(Item):
    warranty_period = StringField()  # E.g., "2 years"
    brand = StringField()
```

## Usage

### Creating and Inserting Items

To insert items into the database, use the `insert_one` method. The item's type is managed automatically.

```python
# Insert a book
book = await Book.insert_one(title="1984", author="George Orwell", isbn="123456789", cost=20.0, name="Book")

# Insert an electronics item
electronics = await Electronics.insert_one(warranty_period="2 years", brand="TechBrand", cost=999.99, name="Laptop")
```

### Querying Items

You can query items of any type using their base or specific models. Polymorphism allows retrieved instances to be of
the correct subclass.

```python
# Find a book by ISBN
found_book = await Book.find_one(isbn="123456789")

# Find an electronics item by brand
found_electronics = await Electronics.find_one(brand="TechBrand")
```

## Polymorphic Behavior

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
