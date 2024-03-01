import asyncio
import os
from datetime import datetime, timezone

import pytest

from motormongo import BooleanField, DataBase, DateTimeField, Document, StringField
from motormongo.fields.exceptions import DateTimeFormatError, DateTimeValueError
from tests.test_documents.user import User

# @pytest.mark.asyncio
# async def test_auto_now_field():
#     await DataBase.connect(
#         uri=os.getenv("MONGODB_URL"), db=os.getenv("MONGODB_DB")
#     )
#
#     # Assuming User has a field named 'last_login' with auto_now=True
#     user = User(username="autonowuser")
#     await user.save()
#
#     first_access = user.last_login
#     print(f"first access = {first_access}")
#     # Wait a bit to ensure a noticeable difference in time
#     await asyncio.sleep(1)
#     second_access = user.last_login
#     print(f"first access = {second_access}")
#
#     assert first_access != second_access
#     assert second_access > first_access
#
#     await User.delete_one({"username": user.username})


@pytest.mark.asyncio
async def test_created_at_field():
    await DataBase.connect(uri=os.getenv("MONGODB_URL"), db=os.getenv("MONGODB_DB"))

    user = User(username="autonowadduser")
    await user.save()
    print(f"initial user = {user.to_dict()}")

    print(f"updated user = {user.to_dict()}")
    initial_value = user.created_at
    # Simulate update
    user.username = "updateduser"
    await user.save()
    updated_value = user.created_at

    assert initial_value == updated_value

    await User.delete_one({"username": user.username})


@pytest.mark.asyncio
async def test_created_at_field_w_insert_one():
    await DataBase.connect(uri=os.getenv("MONGODB_URL"), db=os.getenv("MONGODB_DB"))

    # Assuming User has a field named 'created_at' with auto_now_add=True
    user = await User.insert_one(username="autonowadduser")
    print(f"initial user = {user.to_dict()}")
    initial_value = user.created_at
    # Simulate update
    user.username = "updateduser"
    await user.save()
    updated_value = user.created_at

    assert initial_value == updated_value

    await User.delete_one({"username": user.username})


@pytest.mark.asyncio
async def test_update_at_field_w_update_one():
    await DataBase.connect(uri=os.getenv("MONGODB_URL"), db=os.getenv("MONGODB_DB"))

    # Assuming User has a field named 'created_at' with auto_now_add=True
    user = await User.insert_one(username="autonowadduser")
    print(f"initial user = {user.to_dict()}")

    updated_user = await User.update_one({"_id": user._id}, {"username": "newusername"})

    assert updated_user.username == "newusername"
    assert updated_user.updated_at
    assert updated_user.updated_at > user.updated_at

    await User.delete_many({})


@pytest.mark.asyncio
async def test_datetime_field_parsing():
    await DataBase.connect(uri=os.getenv("MONGODB_URL"), db=os.getenv("MONGODB_DB"))

    user = User(username="datetimeuser", last_login="2023-01-01T12:00:00")
    await user.save()

    assert isinstance(user.last_login, datetime)
    assert user.last_login == datetime(2023, 1, 1, 12, 0, 0)

    await User.delete_one({"username": user.username})


@pytest.mark.asyncio
async def test_datetime_field_parsing_formats():
    await DataBase.connect(uri=os.getenv("MONGODB_URL"), db=os.getenv("MONGODB_DB"))

    user = User(username="datetimeuser", dob="2023-01-01T12:00:00")
    await user.save()
    assert isinstance(user.dob, datetime)

    user = User(username="datetimeuser", dob="2023-01-01")
    await user.save()
    assert isinstance(user.dob, datetime)

    user = User(username="datetimeuser", dob="01/01/2023")
    await user.save()
    assert isinstance(user.dob, datetime)

    user = User(username="datetimeuser", dob="01/01/2023")
    await user.save()
    assert isinstance(user.dob, datetime)


@pytest.mark.asyncio
async def test_datetime_fields_work():
    await DataBase.connect(uri=os.getenv("MONGODB_URL"), db=os.getenv("MONGODB_DB"))

    user = User(username="datetimeuser")
    await user.save()

    print(f"user rep = {user.to_dict()}")
    assert user.updated_at
    assert user.created_at

    created_at = user.created_at
    old_updated_at = user.updated_at
    user.username = "newusername"
    await user.save()

    assert user.created_at == created_at
    assert user.updated_at > old_updated_at
    await User.delete_many({})


@pytest.mark.asyncio
async def test_datetime_created_at():
    await DataBase.connect(uri=os.getenv("MONGODB_URL"), db=os.getenv("MONGODB_DB"))

    class Session(Document):
        is_active = BooleanField(default=False)
        created_at = DateTimeField(default=datetime.now(timezone.utc))

        class Meta:
            indexes = [
                {
                    "fields": ["created_at"],
                    "expireAfterSeconds": 300,
                }  # 5-minute expiration
            ]

    session = Session()
    await session.save()

    found_session = await Session.find_one(_id=session.id)
    session_dict = found_session.to_dict()

    assert "created_at" in session_dict
    assert "updated_at" not in session_dict

    # await Session.delete_many({})


@pytest.mark.asyncio
async def test_datetime_fields_work_w_classmethods():
    await DataBase.connect(uri=os.getenv("MONGODB_URL"), db=os.getenv("MONGODB_DB"))

    user = await User.insert_one(username="datetimeuser")

    print(f"user rep = {user.to_dict()}")
    assert user.updated_at
    assert user.created_at

    created_at = user.created_at
    old_updated_at = user.updated_at
    user.username = "newusername"
    await user.save()

    assert user.username == "newusername"
    print(f"T1 = {user.updated_at} and T2 = {old_updated_at}")
    assert user.created_at == created_at
    assert user.updated_at > old_updated_at
    await User.delete_many({})


@pytest.mark.asyncio
async def test_datetime_field_type_validation():
    await DataBase.connect(uri=os.getenv("MONGODB_URL"), db=os.getenv("MONGODB_DB"))

    with pytest.raises(DateTimeFormatError):
        user = User(username="wrongdateuser", last_login="not a real date")
        await user.save()


@pytest.mark.asyncio
async def test_datetime_field_valid_assignment():
    user = User(last_login="2023-01-01T12:00:00")
    assert user.last_login.year == 2023


@pytest.mark.asyncio
async def test_datetime_field_invalid_format():
    with pytest.raises(DateTimeFormatError):
        User(last_login="01-01-2023 12:00:00")  # Assuming this format is not supported


@pytest.mark.asyncio
async def test_datetime_field_invalid_type():
    with pytest.raises(DateTimeValueError):
        User(last_login=123)  # Not a datetime object, date object, or string
