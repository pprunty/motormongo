import os

import pytest

from motormongo import DataBase
from tests.test_documents.user import User


@pytest.mark.asyncio
async def test_update_success():
    await DataBase.connect(
        uri=os.getenv("MONGODB_URL"), db=os.getenv("MONGODB_DB")
    )
    user = {
        "username": "johndoe",
        "email": "johndoe@hotmail.com",
        "password": "password123",
        "age": 69,
    }
    result = await User.insert_one(user)
    update_result = await User.update_one({"_id": result._id}, {"age": 70})
    assert update_result.age != result.age
    assert update_result.age == 70
    assert result._id == update_result._id
    assert update_result.created_at == result.created_at
    assert update_result.updated_at > result.updated_at
    await User.delete_one(_id=update_result._id)


@pytest.mark.asyncio
async def test_update_w_criteria():
    await DataBase.connect(
        uri=os.getenv("MONGODB_URL"), db=os.getenv("MONGODB_DB")
    )
    user = {
        "username": "johndoe-unique12",
    }
    await User.insert_one(user)
    update_result = await User.update_one({"username": "johndoe-unique12"}, {"age": 69})
    assert update_result.username == "johndoe-unique12"
    assert update_result.age == 69
    await User.delete_one(_id=update_result._id)


@pytest.mark.asyncio
async def test_update_many_success():
    await DataBase.connect(
        uri=os.getenv("MONGODB_URL"), db=os.getenv("MONGODB_DB")
    )
    users = [
        {
            "username": "johndoe1",
            "email": "johndoe@hotmail.com",
            "alive": True,
            "age": 69,
        },
        {
            "username": "johndoe2",
            "email": "johndoe2@hotmail.com",
            "alive": True,
            "age": 42,
        },
        {
            "username": "johndoe2",
            "email": "johndoe2@hotmail.com",
            "alive": True,
            "age": 10,
        },
    ]
    inserted_users, inserted_user_ids = await User.insert_many(users)
    assert inserted_users
    assert inserted_user_ids
    query = {"age": {"$gt": 67}}
    update_result, update_count = await User.update_many(query, {"alive": False})
    assert update_result
    assert update_count == 1
    for user in update_result:
        assert user.alive == False
    await User.delete_many({})
