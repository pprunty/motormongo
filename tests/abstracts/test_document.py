import pytest
from test_documents.user import User

@pytest.fixture
def setup_user():
    return NotImplemented

@pytest.mark.asyncio
async def test_insert_one():
    user = {
        "username": "johndoe",
        "email": "johndoe@hotmail.com",
        "password": "password123",
        "age": 69
    }
    result = await User.insert_one(user)
    result_dict = result.to_dict()
    assert "_id" in result_dict
    assert "updated_at" in result_dict
    assert "created_at" in result_dict
    result_dict.pop("_id")
    result_dict.pop("updated_at")
    result_dict.pop("created_at")
    assert result_dict == user

@pytest.mark.asyncio
async def test_insert_one_kwargs():
    user = {
        "username": "johndoe",
        "email": "johndoe@hotmail.com",
        "password": "password123",
        "age": 69
    }
    result = await User.insert_one(**user)
    print(f"result = {result.to_dict()}")
    result_dict = result.to_dict()
    assert "_id" in result_dict
    assert "updated_at" in result_dict
    assert "created_at" in result_dict
    result_dict.pop("_id")
    result_dict.pop("updated_at")
    result_dict.pop("created_at")
    assert result_dict == user

@pytest.mark.asyncio
async def test_destroy_one():
    query = { "username": "johndoe"}
    result = await User.find_one(**query)

    await User.delete_one()

    print(f"result = {result.to_dict()}")
    result_dict = result.to_dict()
    assert "_id" in result_dict
    assert "updated_at" in result_dict
    assert "created_at" in result_dict
    result_dict.pop("_id")
    result_dict.pop("updated_at")
    result_dict.pop("created_at")
    assert result_dict == user
