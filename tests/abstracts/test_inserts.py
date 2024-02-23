import os

import pytest

from motormongo import DataBase
from tests.test_documents.user import User


@pytest.mark.asyncio
async def test_insert_one_success():
    await DataBase.connect(uri=os.getenv("MONGODB_URL"), db=os.getenv("MONGODB_DB"))
    user = {
        "username": "johndoe",
        "email": "johndoe@hotmail.com",
        "password": "password123",
        "age": 69,
    }
    result = await User.insert_one(user)
    result_dict = result.to_dict()
    for k, v in user.items():
        assert k in result_dict
        # TODO: Add this back once binary field check_function is added
        # assert k in result_dict and v == result_dict[k]
    await User.delete_one(_id=result._id)


@pytest.mark.asyncio
async def test_insert_one_w_extra_field_ignored():
    await DataBase.connect(uri=os.getenv("MONGODB_URL"), db=os.getenv("MONGODB_DB"))
    user = {
        "username": "johndoe",
        "email": "johndoe@hotmail.com",
        "password": "password123",
        "bad": "should not be here",
    }
    result = await User.insert_one(user)
    result_dict = result.to_dict()
    assert "bad" not in result_dict
    await User.delete_one(_id=result_dict["_id"])


@pytest.mark.asyncio
async def test_insert_one_kwargs_explicit():
    await DataBase.connect(uri=os.getenv("MONGODB_URL"), db=os.getenv("MONGODB_DB"))
    user = {
        "username": "johndoe",
        "email": "johndoe@hotmail.com",
        "password": "password123",
        "age": 69,
    }
    result = await User.insert_one(
        username=user["username"],
        email=user["email"],
        password=user["password"],
        age=user["age"],
    )
    result_dict = result.to_dict()
    for k, v in user.items():
        assert k in result_dict
    await User.delete_one(_id=result._id)


@pytest.mark.asyncio
async def test_insert_many():
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
    ]
    inserted_users, inserted_user_ids = await User.insert_many(users)
    assert inserted_users
    assert inserted_user_ids
    assert len(inserted_users) == 2
    await User.delete_many(username="johndoe")


# # TODO: Add this to field tests?
# @pytest.mark.asyncio
# async def test_insert_one_w_wrong_datatype_field():
#     await DataBase.connect(uri=os.getenv("MONGODB_URL"), db=os.getenv("MONGODB_DB"))
#     user = {
#         "username": "johndoe",
#         "email": "johndoe@hotmail.com",
#         "password": "password123",
#         "age": "69",
#         "dob": "should not be here"
#     }
#     result = await User.insert_one(user)
#     result_dict = result.to_dict()
#     assert "dob" not in result_dict
