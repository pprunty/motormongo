import os

import pytest

from motormongo import DataBase
from tests.test_documents.user import User


@pytest.mark.asyncio
async def test_find_one_success():
    await DataBase.connect(uri=os.getenv("MONGODB_URL"), db=os.getenv("MONGODB_DB"))
    user = {
        "username": "johndoe",
        "email": "johndoe@hotmail.com",
        "password": "password123",
        "age": 69,
    }
    result = await User.insert_one(user)
    found_result = await User.find_one(_id=result._id)
    assert result.to_dict() == found_result.to_dict()
    await User.delete_one(_id=result._id)


@pytest.mark.asyncio
async def test_find_one_w_kwargs_filter_criteria():
    await DataBase.connect(uri=os.getenv("MONGODB_URL"), db=os.getenv("MONGODB_DB"))
    user = {
        "username": "james",
        "email": "james@hotmail.com",
        "password": "password123",
        "age": 7,
    }
    result = await User.insert_one(user)
    found_result = await User.find_one(
        {"username": "james", "email": "james@hotmail.com"}
    )  # < same as passing criteria (i.e no _id)
    assert result.to_dict() == found_result.to_dict()
    await User.delete_one(_id=found_result._id)


@pytest.mark.asyncio
async def test_find_one_returns_none_w_kwargs():
    await DataBase.connect(uri=os.getenv("MONGODB_URL"), db=os.getenv("MONGODB_DB"))
    filter_criteria = {
        "username": "johndoe45",
    }
    found_result = await User.find_one(**filter_criteria)
    assert found_result is None


@pytest.mark.asyncio
async def test_find_one_returns_none_w_out_kwargs():
    await DataBase.connect(uri=os.getenv("MONGODB_URL"), db=os.getenv("MONGODB_DB"))
    filter_criteria = {
        "username": "johndoe45",
    }
    found_result = await User.find_one(filter_criteria)
    assert found_result is None


@pytest.mark.asyncio
async def test_find_many():
    await DataBase.connect(uri=os.getenv("MONGODB_URL"), db=os.getenv("MONGODB_DB"))
    user = {
        "username": "johndoe",
        "email": "james@hotmail.com",
        "password": "password123",
        "age": 7,
    }
    result = await User.insert_one(user)
    assert result is not None
    filter_criteria = {
        "username": "johndoe",
    }
    found_result = await User.find_many(filter_criteria)
    assert len(found_result) > 0
    await User.delete_one({"_id": result._id})


@pytest.mark.asyncio
async def test_find_many_w_query():
    await DataBase.connect(uri=os.getenv("MONGODB_URL"), db=os.getenv("MONGODB_DB"))
    users = [
        {
            "username": "johndoe",
            "email": "james@hotmail.com",
            "password": "password123",
            "age": 5,
        },
        {
            "username": "johndoe",
            "email": "james@hotmail.com",
            "password": "password123",
            "age": 80,
        },
        {
            "username": "johndoe",
            "email": "james@hotmail.com",
            "password": "password123",
            "age": 84,
        },
    ]
    result = await User.insert_many(users)
    assert result is not None
    query = {"age": {"$gt": 25}}
    found_result = await User.find_many(query)
    print(f"found result = {[doc.to_dict() for doc in found_result]}")
    assert len(found_result) == 2
    await User.delete_many({})


@pytest.mark.asyncio
async def test_find_many_w_limit():
    await DataBase.connect(uri=os.getenv("MONGODB_URL"), db=os.getenv("MONGODB_DB"))
    users = [
        {
            "username": "johndoe",
            "email": "johndoe@hotmail.com",
            "password": "password123",
            "age": 69,
        },
        {
            "username": "johndoe",
            "email": "johndoe2@hotmail.com",
            "password": "password123",
            "age": 42,
        },
        {
            "username": "johndoe",
            "email": "johndoe@hotmail.com",
            "password": "password123",
            "age": 69,
        },
        {
            "username": "johndoe",
            "email": "johndoe2@hotmail.com",
            "password": "password123",
            "age": 42,
        },
    ]
    await User.insert_many(users)
    filter_criteria = {
        "username": "johndoe",
    }
    found_result = await User.find_many(filter_criteria)
    found_result_w_limit = await User.find_many(filter_criteria, limit=2)
    assert len(found_result_w_limit) == 2
    assert len(found_result) > len(found_result_w_limit)
    await User.delete_many(username="johndoe")
