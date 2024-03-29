import os

import pytest

from motormongo import DataBase
from tests.test_documents.items import Book, Electronics, Item


@pytest.mark.asyncio
async def test_book_insert_and_update():
    await DataBase.connect(uri=os.getenv("MONGODB_URL"), db=os.getenv("MONGODB_DB"))

    # Insert a Book item
    book_details = {
        "title": "1984",
        "author": "George Orwell",
        "isbn": "123456789",
        "cost": 20.0,
        "name": "Book",
    }
    book = await Book.insert_one(**book_details)
    assert book.title == "1984"
    assert book.author == "George Orwell"
    assert book.isbn == "123456789"
    assert book.cost == 20.0
    assert book.name == "Book"

    # Update the Book item
    updated_book = await Book.update_one({"_id": book._id}, {"cost": 22.0})
    assert updated_book.cost == 22.0
    assert updated_book.title == book.title  # Ensure other fields remain unchanged
    assert updated_book._id == book._id

    # Clean up
    await Book.delete_many({})


@pytest.mark.asyncio
async def test_electronics_insert_and_update():
    await DataBase.connect(uri=os.getenv("MONGODB_URL"), db=os.getenv("MONGODB_DB"))
    # Insert an Electronics item
    electronics_details = {
        "warranty_period": "2 years",
        "brand": "TechBrand",
        "cost": 999.99,
        "name": "Laptop",
    }
    electronics = await Electronics.insert_one(**electronics_details)
    assert electronics.warranty_period == "2 years"
    assert electronics.brand == "TechBrand"
    assert electronics.cost == 999.99
    assert electronics.name == "Laptop"

    # Update the Electronics item
    updated_electronics = await Electronics.update_one(
        {"_id": electronics._id}, {"cost": 1000.99}
    )
    assert updated_electronics.cost == 1000.99
    assert (
        updated_electronics.brand == electronics.brand
    )  # Ensure other fields remain unchanged
    assert updated_electronics._id == electronics._id

    # Clean up
    await Electronics.delete_many({})


@pytest.mark.asyncio
async def test_find_expensive_items():
    await DataBase.connect(uri=os.getenv("MONGODB_URL"), db=os.getenv("MONGODB_DB"))

    # Insert test data for Books and Electronics
    book_details = {
        "title": "Expensive Book",
        "author": "Famous Author",
        "isbn": "9999999999",
        "cost": 100.0,
        "name": "Book",
    }
    electronics_details = {
        "warranty_period": "5 years",
        "brand": "HighEndBrand",
        "cost": 2000.99,
        "name": "High-End Laptop",
    }
    await Book.insert_one(**book_details)
    await Electronics.insert_one(**electronics_details)

    # Find expensive items
    expensive_items = await Item.find_many(cost={"$gt": 50})
    print(f"expensive items = {[i.to_dict() for i in expensive_items]}")
    assert expensive_items, "No expensive items found"

    for item in expensive_items:
        print(type(item))  # Prints the subclass (Book, Electronics, etc.)
        if isinstance(item, Book):
            print(f"Book: {item.title} by {item.author}")
            assert item.cost > 50, "Book is not expensive"
        elif isinstance(item, Electronics):
            print(f"Electronics: {item.brand} with {item.warranty_period} warranty")
            assert item.cost > 50, "Electronics item is not expensive"

    # Clean up
    await Book.delete_many({})
    await Electronics.delete_many({})


@pytest.mark.asyncio
async def test_polymorphic_aggregate():
    await DataBase.connect(
        uri=os.getenv("MONGODB_URL"), db=os.getenv("MONGODB_COLLECTION")
    )

    # Insert test data
    book_details = {
        "title": "Expensive Book",
        "author": "Famous Author",
        "isbn": "9999999999",
        "cost": 100.0,
        "name": "Book",
    }
    electronics_details = {
        "warranty_period": "5 years",
        "brand": "HighEndBrand",
        "cost": 2000.99,
        "name": "High-End Laptop",
    }
    await Book.insert_one(**book_details)
    await Electronics.insert_one(**electronics_details)

    # Perform a polymorphic aggregation to find items with cost greater than 50
    expensive_items_pipeline = [{"$match": {"cost": {"$gt": 50}}}]
    expensive_items = await Item.aggregate(
        expensive_items_pipeline, return_as_list=True
    )
    assert expensive_items, "No expensive items found"
    for item in expensive_items:
        assert item.cost > 50, "Found item is not expensive"

    # Clean up
    await Book.delete_many({})
    await Electronics.delete_many({})


@pytest.mark.asyncio
async def test_polymorphic_update_many():
    await DataBase.connect(
        uri=os.getenv("MONGODB_URL"), db=os.getenv("MONGODB_COLLECTION")
    )

    # Insert test data
    book_details = {
        "title": "Moderately Priced Book",
        "author": "Moderate Author",
        "isbn": "8888888888",
        "cost": 60.0,
        "name": "Book",
    }
    electronics_details = {
        "warranty_period": "2 years",
        "brand": "ModerateBrand",
        "cost": 150.99,
        "name": "Moderate Laptop",
    }
    await Book.insert_one(**book_details)
    await Electronics.insert_one(**electronics_details)

    # Update all items where cost is greater than 50 by adding a 'high_value' flag
    update_result, modified_count = await Item.update_many(
        {"cost": {"$gt": 50}}, {"high_value": True}
    )
    assert modified_count > 0, "No documents were updated"

    # Verify that the 'high_value' flag is set
    high_value_items = await Item.find_many(high_value=True)
    for item in high_value_items:
        assert item.high_value is True, "Item does not have 'high_value' flag set"

    # Clean up
    await Book.delete_many({})
    await Electronics.delete_many({})


@pytest.mark.asyncio
async def test_polymorphic_delete_many():
    await DataBase.connect(
        uri=os.getenv("MONGODB_URL"), db=os.getenv("MONGODB_COLLECTION")
    )

    # Insert test data with a 'to_delete' flag for easy identification
    book_details = {
        "title": "Disposable Book",
        "author": "Disposable Author",
        "isbn": "7777777777",
        "cost": 10.0,
        "name": "Book",
    }
    electronics_details = {
        "warranty_period": "1 year",
        "brand": "DisposableBrand",
        "cost": 50.99,
        "name": "Disposable Laptop",
    }
    book = await Book.insert_one(**book_details)
    assert book
    electronic = await Electronics.insert_one(**electronics_details)
    print(f"ElectronicS = {electronic.to_dict()}")
    assert electronic

    # Delete items marked with 'to_delete'
    deleted_count = await Item.delete_many({"cost": {"$lt": 50}})
    assert deleted_count > 0, "No items marked for deletion were deleted"

    print(f"delete count = {deleted_count}")
    # Verify deletion
    remaining_items = await Item.find_many({"cost": {"$gte": 50}})
    print(f"remaining items = {[doc.to_dict() for doc in remaining_items]}")
    assert remaining_items[0].to_dict() == electronic.to_dict()
