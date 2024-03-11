import os

import pytest

from motormongo import DataBase
from tests.test_documents.user import User


@pytest.mark.asyncio
async def test_find_one_or_create_finds():
    await DataBase.connect(uri=os.getenv("MONGODB_URL"), db=os.getenv("MONGODB_DB"))
    user = {
        "username": "johndoe",
        "email": "johndoe@hotmail.com",
        "password": "password123",
        "age": 69,
    }
    insert_result = await User.insert_one(user)
    assert insert_result is not None
    user = {
        "username": "johndoe",
        "email": "johndoe@hotmail.com",
        "password": "password123",
        "age": 69,
    }
    found_result, was_created = await User.find_one_or_create(
        {"_id": insert_result._id}, user
    )
    assert found_result is not None
    assert not was_created
    await User.delete_one(_id=found_result._id)


@pytest.mark.asyncio
async def test_find_one_or_create_creates():
    await DataBase.connect(uri=os.getenv("MONGODB_URL"), db=os.getenv("MONGODB_DB"))
    user = {
        "username": "johndoe",
        "email": "johndoe@hotmail.com",
        "password": "password123",
        "age": 69,
    }
    found_result, was_created = await User.find_one_or_create(
        {"_id": "65d38a11208dd7c4fa61d67b"}, user
    )
    assert found_result is not None
    assert was_created
    assert found_result._id is not None
    await User.delete_one(_id=found_result._id)

@pytest.mark.asyncio
async def test_find_one_or_create_w_embedded():
    await DataBase.connect(uri=os.getenv("MONGODB_URL"), db=os.getenv("MONGODB_DB"))
    user = {
        "username": "johndoe",
        "email": "johndoe@hotmail.com",
        "password": "password123",
        "age": 69,
        "profile": {
            "bio": "Hello World!"
        }
    }
    found_result, was_created = await User.find_one_or_create(
        {"_id": "65d38a11208dd7c4fa61d67b"}, user
    )
    print(f"found result embdedde = {found_result.profile}")
    assert found_result is not None
    assert was_created
    assert found_result._id is not None
    await User.delete_one(_id=found_result._id)


@pytest.mark.asyncio
async def test_find_one_and_update_empty_fields():
    await DataBase.connect(uri=os.getenv("MONGODB_URL"), db=os.getenv("MONGODB_DB"))
    user = {
        "username": "johndoe",
        "email": "johndoe@hotmail.com",
    }
    insert_result = await User.insert_one(user)
    assert insert_result is not None
    update_fields = {
        "username": "johndoe",
        "email": "johndoe@hotmail.com",
        "password": "password123",
        "age": 69,
    }
    updated_found_result, was_updated = await User.find_one_and_update_empty_fields(
        {"_id": insert_result._id}, update_fields
    )
    assert updated_found_result is not None
    if was_updated:
        assert updated_found_result.username == user["username"]
        assert updated_found_result.email == user["email"]
        assert updated_found_result.password is not None
        assert updated_found_result.age == update_fields["age"]
    await User.delete_one(_id=updated_found_result._id)


@pytest.mark.asyncio
async def test_wrong_datatype():
    await DataBase.connect(uri=os.getenv("MONGODB_URL"), db=os.getenv("MONGODB_DB"))
    user = {
        "username": "johndoe",
        "email": "johndoe@hotmail.com",
    }
    insert_result = await User.insert_one(user)
    assert insert_result is not None
    update_fields = {
        "username": "johndoe",
        "email": "johndoe@hotmail.com",
        "password": "password123",
        "age": 69,
    }
    # Using pytest.raises to assert that a TypeError is raised
    with pytest.raises(TypeError):
        updated_found_result, was_updated = await User.find_one_and_update_empty_fields(
            insert_result._id, update_fields
        )

    await User.delete_many({})
